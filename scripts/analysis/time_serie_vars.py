import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm

# Variáveis cujo sinal é invertido nas tabelas (passam a ser positivas para cima)
INVERTER_SINAL = ["avg_slhtf", "avg_snlwrf", "avg_snswrf", "avg_ishf", "avg_tnlwrf", "avg_tnswrf"]


def media_espacial(ds, mascara=None):
    """Média na área do box, ponderada por cos(lat), de cada variável do dataset.
    `mascara` (0/1 em latitude x longitude) restringe a média a terra ou oceano."""
    pesos = np.cos(np.deg2rad(ds["latitude"]))
    if mascara is not None:
        pesos = pesos * mascara
    medias = {}
    for var in ds.data_vars:
        da = ds[var]
        unidade = getattr(da, "units", "unknown")
        lname = getattr(da, "long_name", var)
        if {"latitude", "longitude"} <= set(da.dims):
            da = da.weighted(pesos).mean(dim=["latitude", "longitude"])
        outras = [d for d in da.dims if d != "time"]
        if outras:
            da = da.mean(dim=outras)
        medias[cm.nome_coluna(var, unidade, lname)] = da
    return xr.Dataset(medias)


def time_series_var(modo="analise"):
    """Gera uma tabela de séries temporais com médias espaciais para cada variável em arquivos NetCDF.
    modo='clima' usa os dados da normal (datain/processed/clima) e salva time_series_normal_*.csv."""

    df_box = cm.ler_boxes()
    print(df_box.head())
    lsm = None

    for _, row in df_box.iterrows():
        exp_name = row['exp_name']
        name = row['name']
        superficie = cm.superficie_de(row)
        if superficie != "todos" and lsm is None:
            lsm = cm.ler_mascara()
            if lsm is None:
                raise FileNotFoundError(f"Box {exp_name}/{name} usa superficie={superficie}, mas a máscara "
                                        f"não foi baixada. Rode: python scripts/download/get_data.py mascara")

        DIR_DATAIN = cm.dir_processed(modo) / exp_name / name
        files = sorted(DIR_DATAIN.glob("*.nc"))
        if not files:
            print(f"Atenção: nenhum arquivo encontrado em {DIR_DATAIN}")
            continue

        df_all = None
        for file in files:
            print(f"Lendo arquivo: {file}")
            with xr.open_dataset(file) as ds:
                if "valid_time" in ds.dims:
                    ds = ds.rename({"valid_time": "time"})
                if "time" not in ds.dims:
                    print(f"  Atenção: {file.name} sem dimensão de tempo, ignorado")
                    continue
                mascara = cm.mascara_superficie(lsm, superficie, ds["latitude"], ds["longitude"])
                if mascara is not None and mascara.sum() == 0:
                    print(f"  Atenção: box {exp_name}/{name} não tem pontos de {superficie}; ignorado")
                    df_all = None
                    break
                df_medias = media_espacial(ds, mascara).to_dataframe().reset_index()

            # normalizar para o primeiro dia do mês e agregar duplicatas no mesmo mês
            df_medias["time"] = pd.to_datetime(df_medias["time"]).dt.to_period("M").dt.to_timestamp()
            df_medias = df_medias.groupby("time").mean(numeric_only=True)

            if df_all is None:
                df_all = df_medias
            else:
                # em nomes repetidos entre arquivos, mantém o que já está em df_all
                df_medias = df_medias.drop(columns=df_all.columns.intersection(df_medias.columns))
                df_all = df_all.join(df_medias, how="outer")

        if df_all is None:
            print(f"Atenção: nenhum dado temporal para {exp_name}/{name}")
            continue

        df = df_all.sort_index().reset_index()
        df = df.drop(columns=["number"], errors="ignore")
        col = cm.colunas_por_abrev(df)

        # Balanços calculados com os fluxos na convenção original do ERA5 (positivo para baixo)
        bal = cm.calcula_balancos(
            df[col['avg_tnswrf']], df[col['avg_tnlwrf']],
            df[col['avg_snswrf']], df[col['avg_snlwrf']],
            df[col['avg_ishf']], df[col['avg_slhtf']],
            df[col['avg_tprate']],
        )

        # Conversões de unidade
        # tp nas médias mensais do ERA5 é a acumulação média diária (m/dia)
        dias_no_mes = df["time"].dt.days_in_month
        df['tp_mm (mm) (Total precipitation)'] = df[col['tp']] * 1000 * dias_no_mes
        df['avg_tprate_W (W m**-2) (Time-mean total precipitation rate)'] = df[col['avg_tprate']] * cm.L_V
        df['t2m (°C) (2 metre temperature)'] = df[col['t2m']] - 273.15
        df['d2m (°C) (2 metre dewpoint temperature)'] = df[col['d2m']] - 273.15

        # Troca de sinal: fluxos passam a ser positivos para cima
        for abrev in INVERTER_SINAL:
            df[col[abrev]] *= -1

        df['balanc_earth (W m**-2) (earth_balance)'] = bal["earth"]
        df['balanc_atmos (W m**-2) (atmospheric_balance)'] = bal["atmos"]
        df['balanc_surface (W m**-2) (surface_balance)'] = bal["surface"]

        # Por segundo -> por dia (kg m**-2 day**-1 = mm/dia) e tp de m para mm/dia
        df = cm.converter_unidades(df)

        out_csv = cm.arq_serie(exp_name, name, modo)
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        print(f"Tabela salva em: {out_csv}\n")


if __name__ == "__main__":
    # python time_serie_vars.py [analise|clima]
    time_series_var(sys.argv[1] if len(sys.argv) > 1 else "analise")

import pandas as pd
import xarray as xr
from pathlib import Path

# Função principal
def time_series_var():
    """Gera uma tabela de séries temporais com médias espaciais para cada variável em arquivos NetCDF."""

    # Diretórios
    DIR_SCRIPT = Path(__file__).resolve().parent
    DIR_ROOT = DIR_SCRIPT.parent.parent
    DIR_BOX = DIR_ROOT / "dataout" / "tables"

    # Ler CSV com as caixas
    df_box = pd.read_csv(DIR_BOX / "boxes.csv")
    print(df_box.head())

    # Itera sobre todas as combinações de exp_name e name
    for idx, row in df_box.iterrows():
        exp_name = row['exp_name']
        name     = row['name']

        # Diretório dos NetCDF para este box
        DIR_DATAIN = DIR_ROOT / "datain" / "processed" / exp_name / name

        # Lista todos os arquivos NetCDF
        files = sorted(DIR_DATAIN.glob("*.nc"))
        if not files:
            print(f"Atenção: nenhum arquivo encontrado em {DIR_DATAIN}")
            continue

        # Lista para armazenar os DataFrames individuais
        dfs = []

        # Processa cada arquivo NetCDF
        for file in files:
            print(f"Lendo arquivo: {file}")
            ds = xr.open_dataset(file)

            # Renomear dimensão 'valid_time' para 'time', se existir
            if "valid_time" in ds.dims:
                ds = ds.rename({"valid_time": "time"})

            nome_file = file.stem
            print(f"  Nome do arquivo: {nome_file}")

            # Calcular médias espaciais de todas as variáveis
            medias = {}
            for var in ds.data_vars:
                unidade = getattr(ds[var], "units", "unknown")
                nome_completa = getattr(ds[var], "long_name", var)
                nome_coluna = f"{var} ({unidade}) ({nome_completa})"
                print(f"  Processando variável: {var} -> coluna: {nome_coluna}")

                dims_para_media = [d for d in ds[var].dims if d != 'time']
                medias[nome_coluna] = ds[var].mean(dim=dims_para_media)

            # Converte para DataFrame
            df_medias = xr.Dataset(medias).to_dataframe().reset_index()
            df_medias["arquivo"] = nome_file

            # Adiciona ao lista de DataFrames
            dfs.append(df_medias)

            ds.close()

        # Concatena todos os DataFrames deste box
        df_resultado = pd.concat(dfs, ignore_index=True)

        # Remove colunas que podem não existir
        df_resultado = df_resultado.drop(columns=["number", "expver", "arquivo"], errors="ignore")

        # Trabalhando nas unidades e sinais das variáveis (exemplo: tp em mm)
        df_resultado['tp_mm (mm) (Total precipitation)'] = df_resultado['tp (m) (Total precipitation)'] * 1000 * 30
        df_resultado['avg_slhtf (W m**-2) (Time-mean surface latent heat flux)'] *= -1
        df_resultado['avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)'] *= -1
        df_resultado['avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)'] *= -1
        df_resultado['avg_ishf (W m**-2) (Time-mean surface sensible heat flux)'] *= -1
        df_resultado['avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)'] *= -1
        df_resultado['avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)'] *= -1
        df_resultado['avg_tprate_W (W m**-2) (Time-mean total precipitation rate)'] = df_resultado['avg_tprate (kg m**-2 s**-1) (Time-mean total precipitation rate)'] * 2500000
        df_resultado['t2m (°C) (2 metre temperature)'] = df_resultado['t2m (K) (2 metre temperature)'] - 273.15
        df_resultado['d2m (°C) (2 metre dewpoint temperature)'] = df_resultado['d2m (K) (2 metre dewpoint temperature)'] - 273.15

        
        # Balances
        lw_nettop = df_resultado['avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)']
        sw_nettop = df_resultado['avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)']
        sw_netsrf = df_resultado['avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)']
        lw_netsrf = df_resultado['avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)']
        lh = df_resultado['avg_slhtf (W m**-2) (Time-mean surface latent heat flux)']
        sh = df_resultado['avg_ishf (W m**-2) (Time-mean surface sensible heat flux)']
        mtpr = df_resultado['avg_tprate_W (W m**-2) (Time-mean total precipitation rate)']

        df_resultado['balanc_earth (W m**-2) (earth_balance)'] = (-1)*(lw_nettop + sw_nettop)
        df_resultado['balanc_atmos (W m**-2) (atmospheric_balance)'] = (-1)*(sw_nettop - sw_netsrf) + (-1)*(lw_nettop - lw_netsrf) + sh + mtpr
        df_resultado['balanc_surface (W m**-2) (surface_balance)'] = (-1)*(sw_netsrf + lw_netsrf) - sh - lh

        # Salvar CSV
        out_csv = DIR_ROOT / "dataout" / "tables" / exp_name /f"time_series_{exp_name}_{name}.csv"
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df_resultado.to_csv(out_csv, index=False)
        print(f"Tabela salva em: {out_csv}\n")

if __name__ == "__main__":
    time_series_var()

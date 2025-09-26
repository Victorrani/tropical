import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

def plot_medias():

    limits_dict = {
        'cbh (m) (Cloud base height)': [-1000, 1000],
        'd2m (K) (2 metre dewpoint temperature)': [-5, 5],
        't2m (K) (2 metre temperature)': [-5, 5],
        'hcc ((0 - 1)) (High cloud cover)': [-0.2, 0.2],
        'lcc ((0 - 1)) (Low cloud cover)': [-0.2, 0.2],
        'mcc ((0 - 1)) (Medium cloud cover)': [-0.2, 0.2],
        'tcc ((0 - 1)) (Total cloud cover)': [-0.2, 0.2],
        'tcw (kg m**-2) (Total column water)': [-15, 15],
        'tcwv (kg m**-2) (Total column vertically-integrated water vapour)': [-15, 15],
        'tp (m) (Total precipitation)': [-0.01, 0.01],
        'avg_ie (kg m**-2 s**-1) (Time-mean moisture flux)': [-1e-4, 1e-4],
        'avg_sdirswrf (W m**-2) (Time-mean surface direct short-wave radiation flux)': [-50, 50],
        'avg_sdirswrfcs (W m**-2) (Time-mean surface direct short-wave radiation flux, clear sky)': [-5, 5],
        'avg_sdlwrf (W m**-2) (Time-mean surface downward long-wave radiation flux)': [-25, 25],
        'avg_sdlwrfcs (W m**-2) (Time-mean surface downward long-wave radiation flux, clear sky)': [-25, 25],
        'avg_sdswrf (W m**-2) (Time-mean surface downward short-wave radiation flux)': [-50, 50],
        'avg_sdswrfcs (W m**-2) (Time-mean surface downward short-wave radiation flux, clear sky)': [-10, 10],
        'avg_sduvrf (W m**-2) (Time-mean surface downward UV radiation flux)': [-10, 10],
        'avg_slhtf (W m**-2) (Time-mean surface latent heat flux)': [-20, 20],
        'avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)': [-20, 20],
        'avg_snlwrfcs (W m**-2) (Time-mean surface net long-wave radiation flux, clear sky)': [-20, 20],
        'avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)': [-30, 30],
        'avg_snswrfcs (W m**-2) (Time-mean surface net short-wave radiation flux, clear sky)': [-10, 10],
        'avg_ishf (W m**-2) (Time-mean surface sensible heat flux)': [-30, 30],
        'avg_tdswrf (W m**-2) (Time mean top downward short-wave radiation flux)': [-2.5, 2.5],
        'avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)': [-20, 20],
        'avg_tnlwrfcs (W m**-2) (Time-mean top net long-wave radiation flux, clear sky)': [-10, 10],
        'avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)': [-30, 30],
        'avg_tnswrfcs (W m**-2) (Time-mean top net short-wave radiation flux, clear sky)': [-5, 5],
        'avg_tprate (kg m**-2 s**-1) (Time-mean total precipitation rate)': [-0.0001, 0.0001],
        'avg_vimdf (kg m**-2 s**-1) (Time-mean total column vertically-integrated moisture divergence flux)': [-0.0001, 0.0001],
        'tp_mm (mm) (Total precipitation)': [-100, 100],
        'avg_tprate_W (W m**-2) (Time-mean total precipitation rate)': [-100, 100],
        't2m (°C) (2 metre temperature)': [-5, 5],
        'd2m (°C) (2 metre dewpoint temperature)': [-5, 5],
        'balanc_earth (W m**-2) (earth_balance)': [-20, 20],
        'balanc_atmos (W m**-2) (atmospheric_balance)': [-100, 100],
        'balanc_surface (W m**-2) (surface_balance)': [-5, 5]
    }

    DIR_SCRIPT = Path(__file__).resolve().parent
    DIR_ROOT = DIR_SCRIPT.parent.parent
    DIR_FIGS = DIR_ROOT / "dataout"
    DIR_BOX = DIR_ROOT / "dataout" / "tables"

    df_box = pd.read_csv(DIR_BOX / "boxes.csv")

    def _prep_mes_index(d: pd.DataFrame) -> pd.DataFrame:
        """Garante coluna 'mes' (1..12) como índice crescente."""
        d = d.copy()
        if "mes" in d.columns:
            d["mes"] = pd.to_numeric(d["mes"], errors="coerce")
        elif "time" in d.columns:
            d["mes"] = pd.to_datetime(d["time"], errors="coerce").dt.month
        else:
            raise ValueError("CSV de climatologia sem 'mes' ou 'time'.")
        d.set_index("mes", inplace=True)
        d.sort_index(inplace=True)
        return d

    for _, row in df_box.iterrows():
        exp_name = row["exp_name"]
        name     = row["name"]

        DIR_CSV = DIR_FIGS / "tables" / exp_name

        # arquivos esperados
        paths = {
            "Série total": DIR_CSV / f"{exp_name}_{name}_clima.csv",
            "1980–1995"  : DIR_CSV / f"{exp_name}_{name}_clima_80_95.csv",
            "1996–2004"  : DIR_CSV / f"{exp_name}_{name}_clima_96_04.csv",
            "2005–2015"  : DIR_CSV / f"{exp_name}_{name}_clima_05_15.csv",
            "2016–2024"  : DIR_CSV / f"{exp_name}_{name}_clima_16_24.csv",
        }

        df = pd.read_csv(paths['Série total'])
        df1 = pd.read_csv(paths["1980–1995"])
        df2 = pd.read_csv(paths["1996–2004"])
        df3 = pd.read_csv(paths["2005–2015"])
        df4 = pd.read_csv(paths["2016–2024"])

        variavel = df.columns
        print(variavel)
        var_name = input(str('Escolha a varíavel ara plotar: '))
        nome_var = var_name.strip().split()[2] if var_name.strip() else ""
        unidade = var_name.strip().split()[1] if var_name.strip() else ""
        print(nome_var)
        
        print(f'Variavel escolhida: {var_name}')

        fig, ax = plt.subplots(figsize=(20, 6))
        ax.plot(df[var_name], marker='o')
        ax.plot(df1[var_name], marker='x')
        ax.plot(df2[var_name], marker='d')
        ax.plot(df3[var_name], marker='x')
        ax.plot(df4[var_name], marker='o')

        ax.set_title(f'Time Series of {nome_var}')
        ax.set_xlabel('Mês')
        ax.set_ylabel(unidade)
        ax.grid(True)
        
        outdir = DIR_FIGS / exp_name / name / "clima"
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / f'{exp_name}_{name}_clima{nome_var}_time_series.jpg', dpi=300, bbox_inches='tight')
        plt.close(fig)

#
if __name__ == "__main__":
    plot_medias()

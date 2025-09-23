import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import re

def plot_desv():

    # Dicionário de limites para cada variável
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

    # Diretórios importantes
    DIR_FIGS = DIR_ROOT / "dataout"
    DIR_BOX = DIR_ROOT / "dataout" / "tables" 

    print("Raiz do projeto:", DIR_ROOT) 
    print("Diretório do script:", DIR_SCRIPT)
    print("Diretório de saída:", DIR_FIGS)
    print("Preparando os plots de todas as variáveis do dataset gerado pelo namelist.txt...")

    df_box = pd.read_csv(DIR_BOX / "boxes.csv")
    print(df_box.head())

    # Itera sobre todas as combinações de exp_name e name
    for idx, row in df_box.iterrows():
        exp_name = row['exp_name']
        name     = row['name']

        DIR_CSV = DIR_FIGS / "tables" / exp_name 

        files = sorted(DIR_CSV.glob("anomalias*.csv"))
        for file in files:
            print(f"Lendo arquivo: {file}")
            stem = file.stem
            # Removemos o prefixo "time_series_"
            nome_regiao = stem.replace("time_series_", "")
            print(nome_regiao)

            df = pd.read_csv(file, parse_dates=["time"])

            for var in df.columns:
                if var == "mes" or var == "time":
                    continue

                # Regex segura
                nome_abreviado, unidade, nome_completo = var, "", var
                match = re.match(r"^(.*?) \((.*?)\) \((.*?)\)$", var)
                if match:
                    nome_abreviado, unidade, nome_completo = match.groups()

                print(f"Plotando variável: {var}")
                fig, ax = plt.subplots(figsize=(20, 6))
                ax.plot(df["time"], df[var], marker='o')
                ax.set_title(f'Time Series of {nome_completo}')
                ax.set_xlabel('Time')
                ax.set_ylabel(unidade)
                ax.grid(True)
                if var in limits_dict:
                    ax.set_ylim(limits_dict[var])

                outdir = DIR_FIGS / exp_name / name / "anomalias"
                outdir.mkdir(parents=True, exist_ok=True)
                fig.savefig(outdir / f'{nome_regiao}_{nome_abreviado}_anomalias_time_series.jpg', dpi=300, bbox_inches='tight')
                plt.close(fig)

                print(f'Saved plot for {var} to {outdir / f"{nome_regiao}_{nome_abreviado}_anomalias_time_series.jpg"}')

            

if __name__ == "__main__":
    plot_desv()
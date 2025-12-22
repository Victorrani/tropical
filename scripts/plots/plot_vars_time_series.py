import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import re

def plot_vars_time_series():

    # Dicionário de limites para cada variável
    limits_dict = {
        'cbh (m) (Cloud base height)': [0, 5000],
        'd2m (K) (2 metre dewpoint temperature)': [280, 310],
        't2m (K) (2 metre temperature)': [260, 310],
        'hcc ((0 - 1)) (High cloud cover)': [0, 1],
        'lcc ((0 - 1)) (Low cloud cover)': [0, 1],
        'mcc ((0 - 1)) (Medium cloud cover)': [0, 1],
        'tcc ((0 - 1)) (Total cloud cover)': [0, 1],
        'tcw (kg m**-2) (Total column water)': [0, 100],
        'tcwv (kg m**-2) (Total column vertically-integrated water vapour)': [0, 100],
        'tp (m) (Total precipitation)': [0, 0.03],
        'avg_ie (kg m**-2 s**-1) (Time-mean moisture flux)': [-1e-4, 0],
        'avg_sdirswrf (W m**-2) (Time-mean surface direct short-wave radiation flux)': [0, 300],
        'avg_sdirswrfcs (W m**-2) (Time-mean surface direct short-wave radiation flux, clear sky)': [0, 300],
        'avg_sdlwrf (W m**-2) (Time-mean surface downward long-wave radiation flux)': [300, 500],
        'avg_sdlwrfcs (W m**-2) (Time-mean surface downward long-wave radiation flux, clear sky)': [300, 450],
        'avg_sdswrf (W m**-2) (Time-mean surface downward short-wave radiation flux)': [100, 300],
        'avg_sdswrfcs (W m**-2) (Time-mean surface downward short-wave radiation flux, clear sky)': [200, 400],
        'avg_sduvrf (W m**-2) (Time-mean surface downward UV radiation flux)': [0, 50],
        'avg_slhtf (W m**-2) (Time-mean surface latent heat flux)': [0, 150],
        'avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)': [0, 200],
        'avg_snlwrfcs (W m**-2) (Time-mean surface net long-wave radiation flux, clear sky)': [-200, 0],
        'avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)': [-500, 0],
        'avg_snswrfcs (W m**-2) (Time-mean surface net short-wave radiation flux, clear sky)': [0, 500],
        'avg_ishf (W m**-2) (Time-mean surface sensible heat flux)': [-5, 100],
        'avg_tdswrf (W m**-2) (Time mean top downward short-wave radiation flux)': [0, 600],
        'avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)': [0, 400],
        'avg_tnlwrfcs (W m**-2) (Time-mean top net long-wave radiation flux, clear sky)': [-400, -200],
        'avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)': [-400, -200],
        'avg_tnswrfcs (W m**-2) (Time-mean top net short-wave radiation flux, clear sky)': [0, 500],
        'avg_tprate (kg m**-2 s**-1) (Time-mean total precipitation rate)': [0, 2e-4],
        'avg_vimdf (kg m**-2 s**-1) (Time-mean total column vertically-integrated moisture divergence flux)': [-2e-4, 2e-4],
        'tp_mm (mm) (Total precipitation)': [0, 500],
        'avg_tprate_W (W m**-2) (Time-mean total precipitation rate)': [0, 500],
        't2m (°C) (2 metre temperature)': [15, 35],
        'd2m (°C) (2 metre dewpoint temperature)': [5, 30],
        'balanc_earth (W m**-2) (earth_balance)': [-250, 250],
        'balanc_atmos (W m**-2) (atmospheric_balance)': [-300, 300],
        'balanc_surface (W m**-2) (surface_balance)': [-10, 10]
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
        files = sorted(DIR_CSV.glob("*.csv"))

    
        for file in files:
            print(f"Lendo arquivo: {file}")
            stem = file.stem
            # Removemos o prefixo "time_series_"
            nome_regiao = stem.replace("time_series_", "")
            print(nome_regiao)

            df = pd.read_csv(file, parse_dates=["time"])

            for var in df.columns:
                if var == "time":
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

                outdir = DIR_FIGS / exp_name / name 
                outdir.mkdir(parents=True, exist_ok=True)
                fig.savefig(outdir / f'{nome_regiao}_{nome_abreviado}_time_series.jpg', dpi=300, bbox_inches='tight')
                plt.close(fig)

                print(f'Saved plot for {var} to {outdir / f"{nome_regiao}_{nome_abreviado}_time_series.jpg"}')

if __name__ == "__main__":
    plot_vars_time_series()

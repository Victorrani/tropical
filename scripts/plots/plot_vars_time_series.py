import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import re


def plot_vars_time_series():
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

                outdir = DIR_FIGS / exp_name / name 
                outdir.mkdir(parents=True, exist_ok=True)
                fig.savefig(outdir / f'{nome_regiao}_{nome_abreviado}_time_series.jpg', dpi=300, bbox_inches='tight')
                plt.close(fig)

                print(f'Saved plot for {var} to {outdir / f"{nome_regiao}_{nome_abreviado}_time_series.jpg"}')

if __name__ == "__main__":
    plot_vars_time_series()

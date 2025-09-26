import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import re

def plot_desv():


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
        files = sorted(DIR_CSV.glob("time_series_*.csv"))

    
        for file in files:
            print(f"Lendo arquivo: {file}")
            stem = file.stem
            # Removemos o prefixo "time_series_"
            nome_regiao = stem.replace("time_series_", "")
            print(nome_regiao)

            df = pd.read_csv(file)
            df['time'] = pd.to_datetime(df['time'])
            #print(df.dtypes)
            
            df['time'] = pd.to_datetime(df['time'])

# Extrair o mês para agrupar
            df['mes'] = df['time'].dt.month
            df['ano'] = df['time'].dt.year

            print(df['ano'])

            quit()
            # Calcular a média por mês (agrupa todos os janeiros, fevereiros, etc.)
            media_climatologica_mensal = df.groupby('mes').mean(numeric_only=True)
            media_climatologica_mensal_80_95 = df[(df['ano'] >= 1980) & (df['ano'] <= 1995)].groupby('mes').mean(numeric_only=True)
            media_climatologica_mensal_96_04 = df[(df['ano'] >= 1996) & (df['ano'] <= 2004)].groupby('mes').mean(numeric_only=True)
            media_climatologica_mensal_05_15 = df[(df['ano'] >= 2005) & (df['ano'] <= 2015)].groupby('mes').mean(numeric_only=True)
            media_climatologica_mensal_16_24 = df[(df['ano'] >= 2016) & (df['ano'] <= 2024)].groupby('mes').mean(numeric_only=True)




            # salva CSV
            out_clim = DIR_CSV / f"{exp_name}_{name}_clima.csv"
            media_climatologica_mensal.to_csv(out_clim)
            media_climatologica_mensal_80_95.to_csv(DIR_CSV / f"{exp_name}_{name}_clima_80_95.csv")
            media_climatologica_mensal_96_04.to_csv(DIR_CSV / f"{exp_name}_{name}_clima_96_04.csv")
            media_climatologica_mensal_05_15.to_csv(DIR_CSV / f"{exp_name}_{name}_clima_05_15.csv")
            media_climatologica_mensal_16_24.to_csv(DIR_CSV / f"{exp_name}_{name}_clima_16_24.csv") 
            print(f"Climatologias salvas em: {out_clim}")

            
            

            

if __name__ == "__main__":
    plot_desv()
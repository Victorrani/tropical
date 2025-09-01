import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import time
import cartopy.crs as ccrs
from matplotlib.colors import TwoSlopeNorm
from cartopy.io import shapereader as shpreader
import numpy as np
from matplotlib.colors import BoundaryNorm, TwoSlopeNorm
import re


DIR_SCRIPT = Path(__file__).resolve().parent

# Raiz do projeto 
DIR_ROOT = DIR_SCRIPT.parent.parent

# Diretórios importantes
DIR_LOGS = DIR_ROOT / "logs"
DIR_DATAIN = DIR_ROOT / "datain" / "processed"
DIR_FIGS = DIR_ROOT / "dataout" 
DIR_SHAPES = DIR_ROOT / "shapefiles" / "BR_UF_2019.shp"

print("Raiz do projeto:", DIR_ROOT) 
print("Diretório do script:", DIR_SCRIPT)
print("Diretório de saída:", DIR_FIGS)

print("Preparando os plots de todas as variáveis do dataset gerado pelo namelist.txt...")

DIR_CSV = DIR_ROOT / "dataout" / "tables" 


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
        
        

        match = re.match(r"^(.*?) \((.*?)\) \((.*?)\)$", var)
        if match:
            nome_abreviado, unidade, nome_completo = match.groups()
            print("Abreviado:", nome_abreviado)
            print("Unidade:", unidade)
            print("Nome completo:", nome_completo)
       
        print(f"Plotando variável: {var}")
  
        fig, ax = plt.subplots(figsize=(20, 6))

        ax.plot(df["time"], df[var], marker='o')
        ax.set_title(f'Time Series of {nome_completo}')
        ax.set_xlabel('Time')
        ax.set_ylabel(unidade)
        ax.grid(True)   


        outdir = DIR_FIGS / file.stem / nome_abreviado
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / f'{nome_regiao}_{nome_abreviado}_time_series.jpg', dpi=300, bbox_inches='tight')
        plt.close(fig)

        print(f'Saved plot for {var} to {outdir / f"{nome_regiao}_{nome_abreviado}_time_series.jpg"}')
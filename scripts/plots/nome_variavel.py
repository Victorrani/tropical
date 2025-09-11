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

files = sorted(DIR_DATAIN.glob("*.nc"))

for file in files:
    print(f"Lendo arquivo: {file}")
    ds = xr.open_dataset(file)
    for var in ds.variables:
        # Acessando long_name e short_name
        long_name = getattr(ds[var], "long_name", "Long name não disponível")
        short_name = ds[var].name  # O short_name é o nome da variável no dataset
        
        # Imprimindo os resultados
        print(f"Variável: {var}")
        print(f"  Nome completo (long_name): {long_name}")
        print(f"  Nome abreviado (short_name): {short_name}")
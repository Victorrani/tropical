import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import time


DIR_SCRIPT = Path(__file__).resolve().parent

# Raiz do projeto 
DIR_ROOT = DIR_SCRIPT.parent.parent

# Diretórios importantes
DIR_OUT = DIR_ROOT / "datain" / "processed"
DIR_LOGS = DIR_ROOT / "logs"
DIR_DATAIN = DIR_ROOT / "datain" / "raw"



print("Raiz do projeto:", DIR_ROOT) 
print("Diretório do script:", DIR_SCRIPT)
print("Diretório de saída:", DIR_OUT)

ds = xr.open_dataset(DIR_DATAIN / "data_stream-moda_stepType-avgad.nc")

print(ds)


with open(DIR_SCRIPT / 'teste.csv', "r") as f:
    linhas = [linha.strip() for linha in f if linha.strip()]
    print(linhas)

for linha in linhas:
    # Criar dicionário {chave: valor}
    dados = dict(item.split("=") for item in linha.split(";"))
    
    name = dados['name']
    lat_max = float(dados['lat_max'])
    lat_min = float(dados['lat_min'])
    lon_max = float(dados['lon_max'])
    lon_min = float(dados['lon_min'])
    
    # Recorte simples
    ds_box = ds.sel(
        latitude=slice(lat_min, lat_max),
        longitude=slice(lon_min, lon_max)
    )
    
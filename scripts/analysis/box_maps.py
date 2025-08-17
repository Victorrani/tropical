import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import time
import cartopy.crs as ccrs
import cartopy.feature

DIR_SCRIPT = Path(__file__).resolve().parent
# Raiz do projeto
DIR_ROOT = DIR_SCRIPT.parent.parent 
# Diretórios importantes
DIR_OUT = DIR_ROOT / "datain" / "processed"
DIR_LOGS = DIR_ROOT / "logs"
DIR_DATAIN = DIR_ROOT / "datain" / "raw"
DIR_FIGS = DIR_ROOT / "dataout" / "figs" / "box" 

df = pd.read_csv(DIR_FIGS / "boxes.csv")


print(df)


# desenvolve o restante do código a partir daqui)
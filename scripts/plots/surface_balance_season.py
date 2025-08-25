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

print("Calculando o balanço de energia para os casos...")

files = sorted(DIR_DATAIN.glob("*.nc"))

norm = TwoSlopeNorm(vmin=0, vcenter=200, vmax=400)

for file in files:
    print(f"Lendo arquivo: {file}")
    ds = xr.open_dataset(file)
    ds = ds.rename({'valid_time': 'time'})
    seasonal_mean = ds.groupby("time.season").mean("time")
    
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()},
                              constrained_layout=True)
    axes = axes.flatten()
    time = seasonal_mean['season'].values
    seasons = ['DJF', 'MAM', 'JJA', 'SON']
     # Loop para plotar cada estação
    for i, season in enumerate(seasons):
        print(f"Processando tempo: {time[i]}")


        sw_nettop = seasonal_mean['avg_tnswrf'].sel(season=season) * (-1)
        lw_nettop = seasonal_mean['avg_tnlwrf'].sel(season=season) * (-1)

        sw_netsrf = seasonal_mean['avg_snswrf'].sel(season=season) * (-1)
        lw_netsrf = seasonal_mean['avg_snlwrf'].sel(season=season) * (-1)
        sh = seasonal_mean['avg_ishf'].sel(season=season) * (-1)
        lh = seasonal_mean['avg_slhtf'].sel(season=season) * (-1)
        mtpr = seasonal_mean['avg_tprate'].sel(season=season) * 2500000

        


        atmospheric_balance = (-1)*(sw_nettop - sw_netsrf) + (-1)*(lw_nettop - lw_netsrf) + sh + mtpr

        # Cálculo com o sentido físico do ECMWF
        atmospheric_balance_physics = (-1)*(sw_nettop - sw_netsrf) + (-1)*(lw_nettop - lw_netsrf) + sh + mtpr


        surface_balance = (sw_netsrf + lw_netsrf) - sh - lh
        surface_balance_physics = (-1)*((sw_netsrf + lw_netsrf) - sh - lh)


        ax = axes[i]

        im = ax.contourf(surface_balance_physics.longitude, surface_balance_physics.latitude,
                          surface_balance_physics,
                         transform=ccrs.PlateCarree(),
                         cmap='turbo', levels=np.arange(0, 401, 10), norm=norm, extend='both')
        ax.set_title(f'Surface Balance - {seasons[i]}', loc='left')
        ax.coastlines()
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        shapefile = list(shpreader.Reader(DIR_SHAPES).geometries())
        ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=0.3)
        ax.add_feature(ccrs.cartopy.feature.BORDERS, linestyle=':', linewidth=0.5)
        ax.add_feature(ccrs.cartopy.feature.LAND, facecolor='lightgray')

        gl = ax.gridlines(crs=ccrs.PlateCarree(), color='black',
                      alpha=1.0, linestyle='--', linewidth=0.4,
                      xlocs=np.arange(-180, 181, 10),  # Ajustar intervalo de longitude conforme necessário
                      ylocs=np.arange(-90, 90, 10),  # Ajustar intervalo de latitude conforme necessário
                      draw_labels=True)
        gl.top_labels = False  # Desativar rótulos no topo
        gl.right_labels = False  # Desativar rótulos à direita

    # Ajustes e colorbar
    
    
    cbar = fig.colorbar(
        im, ax=axes, orientation='vertical', shrink=0.8, label='W/m²'
    )
    cbar.set_ticks(np.arange(0, 400, 20))
    cbar.ax.tick_params(labelsize=10)
    fig.suptitle(f'Surface Balance - {file.stem}', fontsize=16)

    fig.savefig(DIR_FIGS / f'surface_balance_{file.stem}.png', dpi=300, bbox_inches='tight')
    
    #plt.close(fig)
    ds.close()
    
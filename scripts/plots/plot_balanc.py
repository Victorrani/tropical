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

# Diretórios importantes

DIR_SCRIPT = Path(__file__).resolve().parent
DIR_ROOT = DIR_SCRIPT.parent.parent
DIR_LOGS = DIR_ROOT / "logs"
DIR_DATAIN = DIR_ROOT / "datain" / "processed"
DIR_FIGS = DIR_ROOT / "dataout" 
DIR_SHAPES = DIR_ROOT / "shapefiles" / "BR_UF_2019.shp"

print("Raiz do projeto:", DIR_ROOT) 
print("Diretório do script:", DIR_SCRIPT)
print("Diretório de saída:", DIR_FIGS)

print("Preparando os plots dos balanços... Isso pode demorar um pouco...")

# Listando em ordem alfabética os arquivos que serão utilizados
files = sorted(DIR_DATAIN.glob("*.nc"))

# Looping no diretório de dados selecionado no namelist.txt
# Abrindo o arquivo e garantindo algumas funcionalidades 
for file in files:
    print(f"Lendo arquivo: {file}")
    ds = xr.open_dataset(file)
    ds = ds.rename({'valid_time': 'time'})
    ds_vars = list(ds.data_vars)
    times = ds['time'].values

    
    # Looping no tempo. Para cada instante de tempo será gerado 3 mapas
    for t in times:
        data = ds.sel(time=t)
        print(f"  Tempo: {t}")
        time_nome = str(t)[0:7]

        # Cálculo para os balanços

        # Earth baance
        sw_nettop = -data['avg_tnswrf']
        lw_nettop = -data['avg_tnlwrf']
        earth_balance = sw_nettop + lw_nettop
        earth_balance = -earth_balance 

        # Surface Balance
        sw_netsrf = -data['avg_snswrf']
        lw_netsrf = -data['avg_snlwrf']
        sh = -data['avg_ishf']
        lh = -data['avg_slhtf']
        mtpr = data['avg_tprate'] * 2.5e6  # calor latente

        # Atmospheric Balance
        atmospheric_balance = -(sw_nettop - sw_netsrf) - (lw_nettop - lw_netsrf) + sh + mtpr
        # se for igual ao físico, não precisa duplicar
        atmospheric_balance_physics = atmospheric_balance  

        # Superfície
        surface_balance = (sw_netsrf + lw_netsrf) - sh - lh
        surface_balance = -surface_balance # definição ECMWF

        # Criação da composição: 1 linha 3 colunas
        fig, ax = plt.subplots(
    nrows=1, ncols=3, figsize=(18, 6),
    subplot_kw={'projection': ccrs.PlateCarree()}
)


        ax = np.atleast_2d(ax)

        norm_earth = TwoSlopeNorm(vmin=-120, vcenter=0, vmax=120)
        norm_atm = TwoSlopeNorm(vmin=-300, vcenter=0, vmax=300)
        
        # Figuras geradas com o colorbar individual
        im1 = ax[0,0].contourf(
            earth_balance['longitude'], earth_balance['latitude'], earth_balance,
            transform=ccrs.PlateCarree(), cmap="RdBu_r",
            levels=np.arange(-150, 160, 25), norm=norm_earth, extend="both"
        )
        cbar1 = fig.colorbar(im1, ax=ax[0,0], orientation="horizontal", shrink=0.8, pad=0.05)
        cbar1.set_label("W m$^{-2}$")
        ax[0,0].set_title("Earth Balance")

        im2 = ax[0,1].contourf(
            atmospheric_balance['longitude'], atmospheric_balance['latitude'], atmospheric_balance,
            transform=ccrs.PlateCarree(), cmap="RdBu_r",
            levels=np.arange(-300, 310, 25), norm=norm_atm, extend="both"
        )
        cbar2 = fig.colorbar(im2, ax=ax[0,1], orientation="horizontal", shrink=0.8, pad=0.05)
        cbar2.set_label("W m$^{-2}$")
        ax[0,1].set_title("Atmospheric Balance")

        im3 = ax[0,2].contourf(
            surface_balance['longitude'], surface_balance['latitude'], surface_balance,
            transform=ccrs.PlateCarree(), cmap="hot_r",
            levels=np.arange(0, 401, 25), extend="max"
        )
        cbar3 = fig.colorbar(im3, ax=ax[0,2], orientation="horizontal", shrink=0.8, pad=0.05)
        cbar3.set_label("W m$^{-2}$")
        fig.suptitle(f'Balanços: {time_nome}', fontsize=14, y=0.90)
        ax[0,2].set_title("Surface Balance")
        
        # Detalhes das figuras, criação dos mapas, gridlines estados e rios
        for j in range(3):
            axj = ax[0, j]
            shapefile = list(shpreader.Reader(DIR_SHAPES).geometries())
            axj.coastlines()
            axj.add_geometries(shapefile, ccrs.PlateCarree(),
                               edgecolor='black', facecolor='none', linewidth=0.3)
            axj.add_feature(ccrs.cartopy.feature.BORDERS, linestyle=':', linewidth=0.5)
            axj.add_feature(ccrs.cartopy.feature.LAND, facecolor='lightgray')
            axj.add_feature(ccrs.cartopy.feature.RIVERS, edgecolor='blue', linewidth=0.7)

            gl = axj.gridlines(crs=ccrs.PlateCarree(), color='black',
                               alpha=1.0, linestyle='--', linewidth=0.4,
                               xlocs=np.arange(-180, 181, 10),
                               ylocs=np.arange(-90, 91, 10),
                               draw_labels=True)
            gl.top_labels = False
            gl.right_labels = False

        # Salvando as figuras em diretórios específicos para cada arquivo lido
        outdir = DIR_FIGS / file.stem / "balanc"
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / f'balanc_{t}_{file.stem}.jpg', dpi=300, bbox_inches='tight')
       
        plt.close(fig)
ds.close()
















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


from matplotlib.colors import BoundaryNorm, TwoSlopeNorm
import numpy as np

# configuração específica para cada variável
var_config = {
    "tp": {
        "scale": 1000,  # de metros para mm
        "levels": np.arange(0, 105, 5),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "turbo",
        "label": "Total precipitation (mm)",
        "extend": "max"
    },
    "avg_ie": {
        "scale": 1,
        "levels": np.linspace(-8e-5, 5e-5, 27),   # intervalos de ~5e-6
        "norm": lambda lv: TwoSlopeNorm(vmin=-8e-5, vcenter=0, vmax=5e-5),
        "cmap": "BrBG",
        "label": "Moisture flux (kg m⁻² s⁻¹)"
    },
    "avg_sdirswrf": {
        "scale": 1,
        "levels": np.arange(0, 1100, 50),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrRd",
        "label": "Surface direct SW radiation flux (W m⁻²)"
    },
    "avg_sdirswrfcs": {
        "scale": 1,
        "levels": np.arange(0, 1100, 50),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrRd",
        "label": "Surface direct SW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_sdlwrf": {
        "scale": 1,
        "levels": np.arange(0, 600, 20),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "inferno",
        "label": "Downward LW radiation flux (W m⁻²)"
    },
    "avg_sdlwrfcs": {
        "scale": 1,
        "levels": np.arange(0, 600, 20),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "inferno",
        "label": "Downward LW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_sdswrf": {
        "scale": 1,
        "levels": np.arange(0, 1100, 50),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrBr",
        "label": "Downward SW radiation flux (W m⁻²)"
    },
    "avg_sdswrfcs": {
        "scale": 1,
        "levels": np.arange(0, 1100, 50),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrBr",
        "label": "Downward SW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_sduvrf": {
        "scale": 1,
        "levels": np.arange(0, 50, 2),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "PuBu",
        "label": "Downward UV radiation flux (W m⁻²)"
    },
    "avg_slhtf": {
        "scale": 1,
        "levels": np.linspace(-200, 200, 21),
        "norm": lambda lv: TwoSlopeNorm(vmin=-200, vcenter=0, vmax=200),
        "cmap": "RdBu_r",
        "label": "Latent heat flux (W m⁻²)"
    },
    "avg_snlwrf": {
        "scale": 1,
        "levels": np.linspace(-200, 200, 21),
        "norm": lambda lv: TwoSlopeNorm(vmin=-200, vcenter=0, vmax=200),
        "cmap": "RdBu_r",
        "label": "Net LW radiation flux (W m⁻²)"
    },
    "avg_snlwrfcs": {
        "scale": 1,
        "levels": np.linspace(-200, 200, 21),
        "norm": lambda lv: TwoSlopeNorm(vmin=-200, vcenter=0, vmax=200),
        "cmap": "RdBu_r",
        "label": "Net LW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_snswrf": {
        "scale": 1,
        "levels": np.linspace(-200, 200, 21),
        "norm": lambda lv: TwoSlopeNorm(vmin=-200, vcenter=0, vmax=200),
        "cmap": "RdBu_r",
        "label": "Net SW radiation flux (W m⁻²)"
    },
    "avg_snswrfcs": {
        "scale": 1,
        "levels": np.linspace(-200, 200, 21),
        "norm": lambda lv: TwoSlopeNorm(vmin=-200, vcenter=0, vmax=200),
        "cmap": "RdBu_r",
        "label": "Net SW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_ishf": {
        "scale": 1,
        "levels": np.linspace(-200, 200, 21),
        "norm": lambda lv: TwoSlopeNorm(vmin=-200, vcenter=0, vmax=200),
        "cmap": "RdBu_r",
        "label": "Sensible heat flux (W m⁻²)"
    },
    "avg_tdswrf": {
        "scale": 1,
        "levels": np.arange(0, 1500, 50),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrBr",
        "label": "Top downward SW radiation flux (W m⁻²)"
    },
    "avg_tnlwrf": {
        "scale": 1,
        "levels": np.linspace(-300, 300, 25),
        "norm": lambda lv: TwoSlopeNorm(vmin=-300, vcenter=0, vmax=300),
        "cmap": "RdBu_r",
        "label": "Top net LW radiation flux (W m⁻²)"
    },
    "avg_tnlwrfcs": {
        "scale": 1,
        "levels": np.linspace(-300, 300, 25),
        "norm": lambda lv: TwoSlopeNorm(vmin=-300, vcenter=0, vmax=300),
        "cmap": "RdBu_r",
        "label": "Top net LW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_tnswrf": {
        "scale": 1,
        "levels": np.linspace(-300, 300, 25),
        "norm": lambda lv: TwoSlopeNorm(vmin=-300, vcenter=0, vmax=300),
        "cmap": "RdBu_r",
        "label": "Top net SW radiation flux (W m⁻²)"
    },
    "avg_tnswrfcs": {
        "scale": 1,
        "levels": np.linspace(-300, 300, 25),
        "norm": lambda lv: TwoSlopeNorm(vmin=-300, vcenter=0, vmax=300),
        "cmap": "RdBu_r",
        "label": "Top net SW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_tprate": {
        "scale": 1,
        "levels": np.linspace(0, 0.001, 21),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "Blues",
        "label": "Precipitation rate (kg m⁻² s⁻¹)"
    },
    "avg_vimdf": {
        "scale": 1,
        "levels": np.linspace(-1e-3, 1e-3, 21),
        "norm": lambda lv: TwoSlopeNorm(vmin=-1e-3, vcenter=0, vmax=1e-3),
        "cmap": "BrBG",
        "label": "Vertically-integrated moisture divergence (kg m⁻² s⁻¹)"
    }
}

for file in files:
    print(f"Lendo arquivo: {file}")
    ds = xr.open_dataset(file)
    ds = ds.rename({'valid_time': 'time'})
    ds_vars = list(ds.data_vars)
    times = ds['time'].values

for var in ds.data_vars:
    times = ds['time'].values
    print(f"Processando variável: {var} ({ds[var].long_name})")
    
    for t in times:
        data = ds[var].sel(time=t)
        name = data.long_name
        print(f"  Tempo: {t}")

        if var in var_config:
            cfg = var_config[var]
            data = data * cfg["scale"]
            levels = cfg["levels"]
            norm = cfg["norm"](levels)
            cmap = cfg["cmap"]
            label = cfg["label"]
            extend = cfg['extend'] if 'extend' in cfg else 'both'
        else:
            # fallback genérico
            levels = np.linspace(float(data.min()), float(data.max()), 21)
            norm = BoundaryNorm(levels, ncolors=256)
            cmap = "viridis"
            label = f"{data.long_name} ({data.units})"

        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        im = ax.contourf(data['longitude'], data['latitude'], data,
                          transform=ccrs.PlateCarree(), cmap=cmap, levels=levels,
                          norm=norm, extend=extend)
        cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.8)
        cbar.set_label(label)

        ax.set_title(f'{name} - Time: {pd.to_datetime(t).strftime("%Y-%m")}', fontsize=14)
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
        outdir = DIR_FIGS / file.stem / var
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / f'{var}_{t}_{file.stem}.jpg', dpi=300, bbox_inches='tight')
       
        plt.close(fig)
ds.close()
















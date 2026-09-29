"""
Mapas das variáveis de cada box (datain/processed/EXP/nome/*.nc), um mapa por
variável e por mês, em dataout/EXP/nome/mapas/<variavel>/.
Obs.: aqui os fluxos estão na convenção original do ERA5 (positivo para baixo).

Uso (todos os anos da série, só os meses escolhidos):
    python scripts/plots/plot_vars.py 12                 # só dezembro
    python scripts/plots/plot_vars.py 12 1 2             # dezembro, janeiro e fevereiro
    python scripts/plots/plot_vars.py all                # todos os meses (milhares de mapas!)
    python scripts/plots/plot_vars.py 1 --vars tp avg_slhtf   # só algumas variáveis
    python scripts/plots/plot_vars.py                    # pergunta os meses no terminal
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
from matplotlib.colors import BoundaryNorm, TwoSlopeNorm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm

# configuração específica para cada variável
VAR_CONFIG = {
    "tp": {
        "scale": 1000,  # m/dia (média mensal do ERA5) -> mm/dia
        "levels": np.arange(0, 21, 1),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlGnBu",
        "label": "Total precipitation (mm dia⁻¹)",
        "extend": "max"
    },
    "avg_ie": {
        "scale": 86400,  # por segundo -> por dia
        "levels": np.arange(-7, 4.5, 0.5),
        "norm": lambda lv: TwoSlopeNorm(vmin=-7, vcenter=0, vmax=4),
        "cmap": "BrBG",
        "label": "Moisture flux (kg m⁻² dia⁻¹ = mm dia⁻¹)"
    },
    "avg_sdirswrf": {
        "scale": 1,
        "levels": np.arange(0, 400, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrRd",
        "label": "Surface direct SW radiation flux (W m⁻²)"
    },
    "avg_sdirswrfcs": {
        "scale": 1,
        "levels": np.arange(0, 400, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrRd",
        "label": "Surface direct SW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_sdlwrf": {
        "scale": 1,
        "levels": np.arange(0, 500, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "inferno",
        "label": "Downward LW radiation flux (W m⁻²)"
    },
    "avg_sdlwrfcs": {
        "scale": 1,
        "levels": np.arange(0, 500, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "inferno",
        "label": "Downward LW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_sdswrf": {
        "scale": 1,
        "levels": np.arange(0, 500, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrBr",
        "label": "Downward SW radiation flux (W m⁻²)"
    },
    "avg_sdswrfcs": {
        "scale": 1,
        "levels": np.arange(0, 500, 25),
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
        "levels": np.arange(0, 500, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlOrBr",
        "label": "Top downward SW radiation flux (W m⁻²)"
    },
    "avg_tnlwrf": {
        "scale": 1,
        "levels": np.linspace(-300, 0, 25),  # ERA5: negativo (para cima)
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "RdBu_r",
        "label": "Top net LW radiation flux (W m⁻²)"
    },
    "avg_tnlwrfcs": {
        "scale": 1,
        "levels": np.linspace(-300, 300, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "RdBu_r",
        "label": "Top net LW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_tnswrf": {
        "scale": 1,
        "levels": np.linspace(0, 300, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "RdBu_r",
        "label": "Top net SW radiation flux (W m⁻²)"
    },
    "avg_tnswrfcs": {
        "scale": 1,
        "levels": np.linspace(0, 300, 25),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "RdBu_r",
        "label": "Top net SW radiation flux (clear sky) (W m⁻²)"
    },
    "avg_tprate": {
        "scale": 86400,  # por segundo -> por dia
        "levels": np.arange(0, 21, 1),
        "norm": lambda lv: BoundaryNorm(lv, ncolors=256),
        "cmap": "YlGnBu",
        "label": "Precipitation rate (kg m⁻² dia⁻¹ = mm dia⁻¹)",
        "extend": "max"
    },
    "avg_vimdf": {
        "scale": 86400,  # por segundo -> por dia
        "levels": np.arange(-10, 11, 1),
        "norm": lambda lv: TwoSlopeNorm(vmin=-10, vcenter=0, vmax=10),
        "cmap": "BrBG",
        "label": "Vertically-integrated moisture divergence (kg m⁻² dia⁻¹ = mm dia⁻¹)"
    }
}

# Variáveis com escalas separadas para continente e oceano (usadas se a máscara
# datain/mascara/land_sea_mask.nc existir). Convenção ERA5: negativo = para cima.
TERRA_OCEANO = {
    "avg_slhtf": ({"levels": np.arange(-160, 1, 10), "cmap": "YlOrBr_r"},
                  {"levels": np.arange(-250, 1, 25), "cmap": cm.cmap_oceano_sequencial()}),
    "avg_ishf": ({"levels": np.arange(-80, 11, 10), "cmap": "YlOrBr_r"},
                 {"levels": np.arange(-40, 11, 5), "cmap": cm.cmap_oceano_sequencial()}),
}


def estilo(var, data):
    """Níveis, norma, colormap, rótulo e extend para a variável."""
    if var in VAR_CONFIG:
        cfg = VAR_CONFIG[var]
        levels = cfg["levels"]
        return cfg["scale"], levels, cfg["norm"](levels), cfg["cmap"], cfg["label"], cfg.get("extend", "both")

    # fallback genérico: níveis a partir dos valores do campo
    vmin, vmax = float(data.min()), float(data.max())
    if not np.isfinite(vmin) or vmin == vmax:
        vmax = vmin + 1
    levels = np.linspace(vmin, vmax, 21)
    label = f"{getattr(data, 'long_name', var)} ({getattr(data, 'units', '')})"
    return 1, levels, BoundaryNorm(levels, ncolors=256), "viridis", label, "both"


def ler_meses(argumentos):
    """Converte ['12', '1'] -> [12, 1]; 'all' -> None (todos). Sem argumentos, pergunta."""
    while True:
        if not argumentos:
            try:
                argumentos = input("Meses para plotar (1-12 separados por espaço, ou 'all'): ").split()
            except EOFError:
                sys.exit("\nNenhum mês informado.")
        if [a.lower() for a in argumentos] == ["all"]:
            return None
        try:
            meses = sorted({int(a) for a in argumentos})
            if meses and all(1 <= m <= 12 for m in meses):
                return meses
        except ValueError:
            pass
        print(f"Meses inválidos: {' '.join(argumentos)}. Use números de 1 a 12 ou 'all'.")
        argumentos = None


def plot_vars(meses=None, variaveis=None):
    """meses: lista de 1..12 (None = todos). variaveis: nomes abreviados (None = todas)."""
    print(f"Meses: {meses or 'todos'}   Variáveis: {variaveis or 'todas'}")

    df_box = cm.ler_boxes()
    geometrias = cm.ler_geometrias()
    lsm = cm.ler_mascara()

    for _, row in df_box.iterrows():
        exp_name = row['exp_name']
        name = row['name']

        for file in sorted((cm.DIR_PROCESSED / exp_name / name).glob("*.nc")):
            print(f"Lendo arquivo: {file}")
            ds = cm.abrir_netcdfs([file])

            if meses is not None:
                ds = ds.sel(time=ds['time'].dt.month.isin(meses))

            for var in ds.data_vars:
                da = ds[var]
                if not {"latitude", "longitude"} <= set(da.dims):
                    continue
                if variaveis is not None and var not in variaveis:
                    continue
                print(f"Processando variável: {var} ({getattr(da, 'long_name', var)})")
                scale, levels, norm, cmap, label, extend = estilo(var, da)
                outdir = cm.dir_figuras(exp_name, name, "mapas", var)

                for t in ds['time'].values:
                    data = da.sel(time=t) * scale
                    time_nome = pd.Timestamp(t).strftime("%Y-%m")

                    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
                    if var in TERRA_OCEANO and lsm is not None:
                        cm.contourf_terra_oceano(fig, ax, data, lsm, *TERRA_OCEANO[var],
                                                 getattr(da, "units", ""))
                    else:
                        im = ax.contourf(data['longitude'], data['latitude'], data,
                                         transform=ccrs.PlateCarree(), cmap=cmap, levels=levels,
                                         norm=norm, extend=extend)
                        cbar = fig.colorbar(im, ax=ax, orientation='horizontal', shrink=0.8)
                        cbar.set_label(label)
                    ax.set_title(f'{getattr(da, "long_name", var)}\nTime: {time_nome}', fontsize=14)
                    cm.decorar_mapa(ax, geometrias)

                    fig.savefig(outdir / f'{var}_{time_nome}_{exp_name}_{name}.jpg', dpi=cm.DPI, bbox_inches='tight')
                    plt.close(fig)
            ds.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("meses", nargs="*", help="meses de 1 a 12, ou 'all'")
    p.add_argument("--vars", nargs="+", metavar="VAR", help="variáveis (nome abreviado, ex.: tp avg_slhtf)")
    a = p.parse_args()
    plot_vars(ler_meses(a.meses), a.vars)

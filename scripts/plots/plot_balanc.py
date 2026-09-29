"""
Mapas dos balanços de energia (Terra, atmosfera e superfície) para cada mês.

    python scripts/plots/plot_balanc.py   # um conjunto de mapas por box (datain/processed)

Veja também plot_balanc_box.py, que plota o domínio completo com os boxes desenhados.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm

VARS_BALANCO = ["avg_tnswrf", "avg_tnlwrf", "avg_snswrf", "avg_snlwrf", "avg_ishf", "avg_slhtf", "avg_tprate"]

PAINEIS = [
    ("earth", "Earth Balance", np.arange(-150, 151, 25)),
    ("atmos", "Atmospheric Balance", np.arange(-300, 301, 25)),
    ("surface", "Surface Balance", np.arange(-10, 11, 2)),
]

# Balanço de superfície: com a máscara, continente e oceano têm escalas próprias
# (no oceano o saldo mensal é muito maior, pois ele armazena e transporta calor)
SUPERFICIE_TERRA = {"levels": np.arange(-10, 11, 2), "cmap": "RdBu_r"}
SUPERFICIE_OCEANO = {"levels": np.arange(-150, 151, 25), "cmap": cm.cmap_oceano_divergente()}  # teal-laranja (ver common.py)


def balancos_dataset(ds):
    return cm.calcula_balancos(*(ds[v] for v in VARS_BALANCO))


def figura_balancos(bal, titulo, out, geometrias, boxes=None, passo_grade=2.5, lsm=None):
    """Uma figura com 3 mapas (Terra, atmosfera, superfície) para um instante de tempo.
    Com `lsm` (máscara do ERA5), o balanço de superfície usa escalas separadas
    para continente e oceano."""
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(18, 6),
                            subplot_kw={'projection': ccrs.PlateCarree()})

    for ax, (chave, nome, levels) in zip(axs, PAINEIS):
        campo = bal[chave]
        if chave == "surface" and lsm is not None:
            cm.contourf_terra_oceano(fig, ax, campo, lsm, SUPERFICIE_TERRA, SUPERFICIE_OCEANO, "W m$^{-2}$")
        else:
            im = ax.contourf(campo['longitude'], campo['latitude'], campo,
                             transform=ccrs.PlateCarree(), cmap="RdBu_r",
                             levels=levels, extend="both")
            cbar = fig.colorbar(im, ax=ax, orientation="horizontal", shrink=0.8, pad=0.05)
            cbar.set_label("W m$^{-2}$")
        ax.set_title(nome)
        cm.decorar_mapa(ax, geometrias, passo_grade)

        if boxes is not None:
            for _, b in boxes.iterrows():
                ax.add_patch(Rectangle((b['lon_min'], b['lat_min']),
                                       b['lon_max'] - b['lon_min'], b['lat_max'] - b['lat_min'],
                                       linewidth=2, edgecolor='red', facecolor='none',
                                       transform=ccrs.PlateCarree()))

    fig.suptitle(titulo, fontsize=14)
    fig.savefig(out, dpi=cm.DPI, bbox_inches='tight')
    plt.close(fig)


def plot_balanc():
    print("Preparando os plots dos balanços... Isso pode demorar um pouco...")

    df_box = cm.ler_boxes()
    geometrias = cm.ler_geometrias()
    lsm = cm.ler_mascara()
    if lsm is None:
        print("Máscara continente/oceano não encontrada (get_data.py mascara): escala única")

    for _, row in df_box.iterrows():
        exp_name = row['exp_name']
        name = row['name']

        files = sorted((cm.DIR_PROCESSED / exp_name / name).glob("*.nc"))
        if not files:
            print(f"Atenção: nenhum arquivo encontrado para {exp_name}/{name}")
            continue

        ds = cm.abrir_netcdfs(files, VARS_BALANCO)
        bal = balancos_dataset(ds)
        outdir = cm.dir_figuras(exp_name, name, "balanc")

        for t in ds['time'].values:
            time_nome = pd.Timestamp(t).strftime("%Y-%m")
            print(f"  {exp_name}/{name} {time_nome}")
            figura_balancos({k: v.sel(time=t) for k, v in bal.items()},
                            f'Balanços {exp_name} {name}: {time_nome}',
                            outdir / f'balanc_{time_nome}_{exp_name}_{name}.jpg',
                            geometrias, lsm=lsm)
        ds.close()


if __name__ == "__main__":
    plot_balanc()

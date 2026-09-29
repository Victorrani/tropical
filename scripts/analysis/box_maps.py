"""Mapa com a localização dos boxes definidos no namelist (dataout/tables/boxes.csv)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm


def box_maps(margem=5):
    df = cm.ler_boxes()
    print(df)

    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([df['lon_min'].min() - margem, df['lon_max'].max() + margem,
                   df['lat_min'].min() - margem, df['lat_max'].max() + margem], crs=ccrs.PlateCarree())
    cm.decorar_mapa(ax, cm.ler_geometrias())

    for _, b in df.iterrows():
        ax.add_patch(Rectangle((b['lon_min'], b['lat_min']),
                               b['lon_max'] - b['lon_min'], b['lat_max'] - b['lat_min'],
                               linewidth=2, edgecolor='red', facecolor='none', transform=ccrs.PlateCarree()))
        ax.text(b['lon_min'], b['lat_max'] + 0.2, f"{b['exp_name']} {b['name']}",
                color='red', fontsize=9, transform=ccrs.PlateCarree())

    ax.set_title('Boxes do namelist')
    out = cm.DIR_DATAOUT / "boxes.jpg"
    fig.savefig(out, dpi=cm.DPI, bbox_inches='tight')
    plt.close(fig)
    print(f"Mapa salvo em: {out}")


if __name__ == "__main__":
    box_maps()

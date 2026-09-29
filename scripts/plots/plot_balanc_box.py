"""
Mapas dos balanços de energia no domínio completo (datain/raw), com os boxes
do namelist desenhados em vermelho. Uma figura por mês em dataout/balanc/.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm
from plot_balanc import VARS_BALANCO, balancos_dataset, figura_balancos


def plot_balanc_box():
    print("Preparando os plots dos balanços... Isso pode demorar um pouco...")

    df_box = cm.ler_boxes()
    print(df_box.head())
    geometrias = cm.ler_geometrias()
    lsm = cm.ler_mascara()

    files = sorted(cm.DIR_RAW.glob("*.nc"))
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo .nc em {cm.DIR_RAW}")

    ds = cm.abrir_netcdfs(files, VARS_BALANCO)
    bal = balancos_dataset(ds)
    outdir = cm.DIR_DATAOUT / "balanc"
    outdir.mkdir(parents=True, exist_ok=True)

    for t in ds['time'].values:
        time_nome = pd.Timestamp(t).strftime("%Y-%m")
        print(f"  Tempo: {time_nome}")
        figura_balancos({k: v.sel(time=t) for k, v in bal.items()},
                        f'Balanços: {time_nome}',
                        outdir / f'balanc_{time_nome}_box.jpg',
                        geometrias, boxes=df_box, passo_grade=10, lsm=lsm)
    ds.close()


if __name__ == "__main__":
    plot_balanc_box()

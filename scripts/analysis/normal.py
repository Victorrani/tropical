"""
Gera a normal climatológica (common.NORMAL, 1991–2020) para os boxes do namelist.

    python scripts/analysis/normal.py          # baixa, processa e apaga os netCDF
    python scripts/analysis/normal.py --manter # mantém os netCDF da normal

Passos: download (área dos boxes) -> recorte -> série das médias no box ->
normal mensal (dataout/tables/EXP/EXP_nome_normal_91_20.csv) -> remove os .nc.

Rode de novo sempre que mudar os boxes do namelist: a normal só é válida
para o mesmo domínio (o desv.py confere isso).
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "download"))
import common as cm
from slice import slice_box
from time_serie_vars import time_series_var
from climatologia import normal


def gerar_normal(manter=False, sim=False):
    dir_raw = cm.dir_raw("clima")
    if any(dir_raw.glob("*.nc")):
        print(f"Usando os netCDF já baixados em {dir_raw}")
    else:
        from get_data import download_data  # importa cdsapi só se for baixar
        download_data("clima", sim=sim)

    slice_box("clima")
    time_series_var("clima")
    for _, row in cm.ler_boxes().iterrows():
        normal(row)

    if manter:
        print(f"netCDF da normal mantidos em {dir_raw} e {cm.dir_processed('clima')}")
    else:
        for d in (dir_raw, cm.dir_processed("clima")):
            if d.exists():
                shutil.rmtree(d)
                print(f"✔ Removido {d}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manter", action="store_true", help="não apaga os netCDF da normal")
    p.add_argument("--sim", action="store_true", help="não pede confirmação para domínios grandes")
    a = p.parse_args()
    gerar_normal(a.manter, a.sim)

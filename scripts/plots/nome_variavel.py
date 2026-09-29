"""Lista as variáveis (nome curto, nome completo e unidade) dos netCDF em datain/."""
import sys
from pathlib import Path

import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm


def nome_variavel():
    files = sorted(cm.DIR_RAW.glob("*.nc")) or sorted(cm.DIR_PROCESSED.rglob("*.nc"))
    if not files:
        print(f"Nenhum arquivo .nc em {cm.DIR_RAW} ou {cm.DIR_PROCESSED}")
        return

    for file in files:
        print(f"Lendo arquivo: {file}")
        with xr.open_dataset(file) as ds:
            for var in ds.data_vars:
                long_name = getattr(ds[var], "long_name", "Long name não disponível")
                units = getattr(ds[var], "units", "")
                print(f"  {var:<16} {long_name} ({units})")


if __name__ == "__main__":
    nome_variavel()

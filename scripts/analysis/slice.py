import sys
from pathlib import Path

import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm


def slice_box(modo="analise"):
    """Recorta os netCDF de datain/raw (ou datain/raw/clima) para cada box do namelist.txt."""

    print("Raiz do projeto:", cm.DIR_ROOT)
    dir_raw, dir_processed = cm.dir_raw(modo), cm.dir_processed(modo)
    print("Modo:", modo)
    print("Diretório de saída:", dir_processed)

    df = cm.ler_namelist()
    print(df)

    # Tabela com todos os boxes: usada pelos demais scripts
    cm.DIR_TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(cm.BOXES_CSV, index=False)

    arquivos_nc = sorted(dir_raw.glob("*.nc"))
    if not arquivos_nc:
        raise FileNotFoundError(f"Nenhum arquivo .nc em {dir_raw}. Rode antes: python scripts/download/get_data.py {modo}")

    for arquivo in arquivos_nc:
        # ex.: data_stream-moda_stepType-avgad -> avgad
        nome_curto = arquivo.stem.split("stepType-")[-1]
        print(f"Lendo {arquivo.name}")

        with xr.open_dataset(arquivo) as ds:
            lat = ds["latitude"]
            lon = ds["longitude"]
            # ERA5 vem com latitude decrescente, mas não assumimos isso
            lat_desc = bool(lat[0] > lat[-1])

            for _, b in df.iterrows():
                exp_name, name = b["exp_name"], b["name"]
                lat_slice = slice(b["lat_max"], b["lat_min"]) if lat_desc else slice(b["lat_min"], b["lat_max"])
                ds_box = ds.sel(latitude=lat_slice, longitude=slice(b["lon_min"], b["lon_max"]))

                if ds_box.sizes["latitude"] == 0 or ds_box.sizes["longitude"] == 0:
                    raise ValueError(
                        f"Box {exp_name}/{name} fora do domínio dos dados "
                        f"(lat {float(lat.min())}..{float(lat.max())}, lon {float(lon.min())}..{float(lon.max())})"
                    )

                print(f"  Box: {name}, Latitude: {b['lat_min']}|{b['lat_max']}, "
                      f"Longitude: {b['lon_min']}|{b['lon_max']} "
                      f"({ds_box.sizes['latitude']}x{ds_box.sizes['longitude']} pontos)")

                output_dir = dir_processed / exp_name / name
                output_dir.mkdir(parents=True, exist_ok=True)
                df[(df["exp_name"] == exp_name) & (df["name"] == name)].to_csv(output_dir / "boxes.csv", index=False)

                out_nc = output_dir / f"{exp_name}_{nome_curto}_{name}.nc"
                ds_box.to_netcdf(out_nc, mode="w", format="NETCDF4")
                print(f"  Arquivo {out_nc.name} salvo em {output_dir}")


if __name__ == "__main__":
    # python slice.py [analise|clima]
    slice_box(sys.argv[1] if len(sys.argv) > 1 else "analise")

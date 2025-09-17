import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import time
import cartopy.crs as ccrs



def slice_box():

    DIR_SCRIPT = Path(__file__).resolve().parent

# Raiz do projeto 
    DIR_ROOT = DIR_SCRIPT.parent.parent

    # Diretórios importantes
    DIR_OUT = DIR_ROOT / "datain" / "processed"
    DIR_LOGS = DIR_ROOT / "logs"
    DIR_DATAIN = DIR_ROOT / "datain" / "raw"
    DIR_FIGS = DIR_ROOT / "dataout" / "tables"
    DIR_FIGS.mkdir(parents=True, exist_ok=True)


    print("Raiz do projeto:", DIR_ROOT) 
    print("Diretório do script:", DIR_SCRIPT)
    print("Diretório de saída:", DIR_OUT)

    lista_nomes = ['radiation', 'cloudBaseHight', 'clouds']
    arquivos_nc = sorted(DIR_DATAIN.glob("*.nc"))
    for arquivo, nome_curto in zip(arquivos_nc, lista_nomes):
        nome_arquivo = arquivo.stem
        print(nome_arquivo)
        print("Criando arquivos individuais dos experimentos...")
        ds = xr.open_dataset(DIR_DATAIN / arquivo)


        with open(DIR_SCRIPT / 'namelist.txt', "r") as f:
            linhas = [linha.strip() for linha in f if linha.strip()]

        linhas = linhas[1:]
        for linha in linhas:
            # Criar dicionário {chave: valor}
            dados = dict(item.split("=") for item in linha.split(";"))

        boxes = []
        for linha in linhas:
            pares = linha.split(';')
            d = {}
            for par in pares:
                k, v = par.split('=')
                try:
                    d[k] = float(v) if '.' in v or '-' in v else int(v)
                except ValueError:
                    d[k] = v 
            boxes.append(d)


        df = pd.DataFrame(boxes)
        print(df)

        # Salvar em CSV (sem o índice)
        df.to_csv(DIR_FIGS / "boxes.csv", index=False)
        

        for b in boxes:
            exp_name = b['exp_name']
            name    = b["name"]
            latmin  = b["lat_min"]
            latmax  = b["lat_max"]
            lonmin  = b["lon_min"]
            lonmax  = b["lon_max"]
    
            ds_box = ds.sel({"latitude": slice(latmax, latmin), "longitude": slice(lonmin, lonmax)})
            print(f"Box: {name}, Latitude: {latmin}|{latmax}, Longitude: {lonmin}|{lonmax}")

            output_dir = DIR_OUT / exp_name / name
            output_dir.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_dir / "boxes.csv", index=False)

            ds_box.to_netcdf(output_dir / f"{exp_name}_{nome_curto}_{name}.nc", mode="w", format="NETCDF4")
            print(f"Arquivo {exp_name}_{nome_curto}_{name}.nc salvo com sucesso em {output_dir}")

        ds.close()

if __name__ == "__main__":
    slice_box()






import zipfile
from pathlib import Path
import cdsapi

print()
print()
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent
print("Raiz do projeto:", project_root)
print()
print()

def download_data():
    """
    Função para baixar dados do ERA5 usando a API do CDS.
    """
    # Aqui você pode adicionar o código para baixar os dados, se necessário.

    #===== 1) Download ERA5 =====
    dataset = "reanalysis-era5-single-levels-monthly-means"
    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": [
            "total_precipitation",
            "mean_evaporation_rate",
            "mean_surface_direct_short_wave_radiation_flux",
            "mean_surface_direct_short_wave_radiation_flux_clear_sky",
            "mean_surface_downward_long_wave_radiation_flux",
            "mean_surface_downward_long_wave_radiation_flux_clear_sky",
            "mean_surface_downward_short_wave_radiation_flux",
            "mean_surface_downward_short_wave_radiation_flux_clear_sky",
            "mean_surface_downward_uv_radiation_flux",
            "mean_surface_latent_heat_flux",
            "mean_surface_net_long_wave_radiation_flux",
            "mean_surface_net_long_wave_radiation_flux_clear_sky",
            "mean_surface_net_short_wave_radiation_flux",
            "mean_surface_net_short_wave_radiation_flux_clear_sky",
            "mean_surface_sensible_heat_flux",
            "mean_top_downward_short_wave_radiation_flux",
            "mean_top_net_long_wave_radiation_flux",
            "mean_top_net_long_wave_radiation_flux_clear_sky",
            "mean_top_net_short_wave_radiation_flux",
            "mean_top_net_short_wave_radiation_flux_clear_sky",
            "mean_total_precipitation_rate",
            "mean_vertically_integrated_moisture_divergence",
            "total_column_water",
            "total_column_water_vapour"
        ],
        "year": ["2024"],
        "month": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived"
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request).download()
    print("✔ Dados do ERA5 baixados com sucesso.")
    return True

download_data()

quit()
#===== 2) Procurar o arquivo .zip baixado =====

current_dir = Path.cwd()


zip_files = list(current_dir.glob("*.zip"))
dir_out = project_root / "data" / "raw"   # <-- aqui está o certo

if not zip_files:
    raise FileNotFoundError("Nenhum arquivo .zip encontrado no diretório atual após o download.")

zip_path = zip_files[0]  # pega o primeiro encontrado

# ===== 3) Extrair para o diretório desejado =====
dest_dir = Path(dir_out)
dest_dir.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(dest_dir)

print(f"✔ Arquivo {zip_path.name} extraído para {dest_dir}")

# ===== 4) Remover o arquivo .zip após a extração =====
zip_path.unlink()
print(f"✔ Arquivo {zip_path.name} removido após a extração.")



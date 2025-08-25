import zipfile
from pathlib import Path
import logging
import time
import cdsapi


# Caminho absoluto do script
DIR_SCRIPT = Path(__file__).resolve().parent

# Raiz do projeto 
DIR_ROOT = DIR_SCRIPT.parent.parent

# Diretórios importantes
DIR_OUT = DIR_ROOT / "datain" / "raw"
DIR_LOGS = DIR_ROOT / "logs"


def download_data():
    """
    Função para baixar dados do ERA5 usando a API do CDS.
    Esta função realiza o download de dados climáticos do ERA5, extrai os arquivos baixados
    de um arquivo .zip e organiza os dados em um diretório específico.
    """
    
    print(f"Raiz do projeto:     {DIR_ROOT}")
    print(f"Diretório do script: {DIR_SCRIPT}")
    print(f"Diretório de saída:  {DIR_OUT}")
    print(f"Diretório de logs:   {DIR_LOGS}")
    print('-' * 50)

    tempo_inicio = time.time()
    logging.basicConfig(
        filename=DIR_LOGS / 'download.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("Iniciando o download dos dados do ERA5.")
    #===== 1) Download ERA5 =====
    # Altere o ano e o mês conforme necessário
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
        "year": ["2020", "2021", "2022", "2023", "2024"],
        "month": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived"
    }
    logging.info(f"Requisição: {dataset}")
    logging.info("Variáveis solicitadas: " + ", ".join(request["variable"]))
    logging.info("Período: " + ", ".join(request["year"]) + " - " + ", ".join(request["month"]))
    logging.info("Formato de dados: " + request["data_format"])

    print("Iniciando o download dos dados do ERA5...")
    print("Aguarde, isso pode levar alguns minutos...")
    client = cdsapi.Client()
    client.retrieve(dataset, request).download()
    print("✔ Dados do ERA5 baixados com sucesso.")



#===== 2) Procurar o arquivo .zip baixado =====


    zip_files = list(DIR_SCRIPT.glob("*.zip"))  # <-- aqui está o certo

    if not zip_files:
        raise FileNotFoundError("Nenhum arquivo .zip encontrado no diretório atual após o download.")

    zip_path = zip_files[0]  # pega o primeiro encontrado

    # ===== 3) Extrair para o diretório desejado =====
    dest_dir = Path(DIR_OUT)
    dest_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)

    print(f"✔ Arquivo {zip_path.name} extraído para {dest_dir}")

    # ===== 4) Remover o arquivo .zip após a extração =====
    zip_path.unlink()
    print(f"✔ Arquivo {zip_path.name} removido após a extração.")

    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio
    tempo_minutos = tempo_total / 60
    print(f"Tempo total de download: {tempo_minutos:.2f} minutos")
    logging.info(f"Tempo total de download: {tempo_minutos:.2f} minutos")

if __name__ == "__main__":
    download_data()

"""
Download das médias mensais do ERA5 para a área dos boxes do namelist.

    python scripts/download/get_data.py clima              # período da normal (1991–2020)
    python scripts/download/get_data.py analise            # ANO_INICIO–ANO_FIM (abaixo)
    python scripts/download/get_data.py analise 2023 2024  # período escolhido
    python scripts/download/get_data.py mascara            # máscara continente/oceano (uma vez)

A normal ('clima') usa a área dos boxes; o modo 'analise' usa AREA (ou a área
dos boxes, se AREA=None). As médias dos boxes são iguais nos dois casos, pois a
grade do ERA5 é a mesma.
"""
import argparse
import logging
import shutil
import sys
import time
import zipfile
from pathlib import Path

import cdsapi
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm

# ===== Configuração do download (altere aqui) =====
# Período padrão do modo 'analise' (o modo 'clima' usa common.NORMAL)
ANO_INICIO = 2015
ANO_FIM = 2025

# Domínio do modo 'analise' [N, W, S, E]. None = retângulo que envolve os boxes
# do namelist + MARGEM graus. Um domínio maior serve para os mapas.
# O modo 'clima' usa SEMPRE a área dos boxes: a normal é calculada por box,
# então um domínio maior só deixaria o download mais pesado.
AREA = [30, -120, -70, -30]
MARGEM = 1.0

# Acima deste tamanho estimado o script avisa e pede confirmação.
# Domínios grandes deixam o download lento e podem não caber na memória.
LIMITE_GB = 1.0

# O CDS limita o tamanho de cada pedido (variáveis x meses). O período é
# dividido em blocos; se aparecer "Your request is too large", diminua este valor.
ANOS_POR_PEDIDO = 5

# Tentativas por pedido quando o CDS falha do lado do servidor
TENTATIVAS = 3

RESOLUCAO = 0.25  # grade do ERA5 (graus)

VARIAVEIS = [
    "2m_dewpoint_temperature",
    "2m_temperature",
    "cloud_base_height",
    "high_cloud_cover",
    "low_cloud_cover",
    "medium_cloud_cover",
    "total_cloud_cover",
    "total_column_water",
    "total_column_water_vapour",
    "total_precipitation",
    "mean_total_precipitation_rate",
    "mean_evaporation_rate",
    "mean_vertically_integrated_moisture_divergence",
    "mean_surface_latent_heat_flux",
    "mean_surface_sensible_heat_flux",
    "mean_surface_direct_short_wave_radiation_flux",
    "mean_surface_downward_long_wave_radiation_flux",
    "mean_surface_downward_short_wave_radiation_flux",
    "mean_surface_downward_uv_radiation_flux",
    "mean_surface_net_long_wave_radiation_flux",
    "mean_surface_net_short_wave_radiation_flux",
    "mean_top_downward_short_wave_radiation_flux",
    "mean_top_net_long_wave_radiation_flux",
    "mean_top_net_short_wave_radiation_flux",
]


def area_dos_boxes():
    """[N, W, S, E] cobrindo todos os boxes do namelist, com MARGEM graus a mais."""
    df = cm.ler_namelist()
    return [min(df["lat_max"].max() + MARGEM, 90), max(df["lon_min"].min() - MARGEM, -180),
            max(df["lat_min"].min() - MARGEM, -90), min(df["lon_max"].max() + MARGEM, 180)]


def estimar_tamanho_gb(area, n_anos):
    """Estimativa do tamanho em disco (netCDF comprimido, ~2 bytes por valor)."""
    n, w, s, e = area
    pontos = ((n - s) / RESOLUCAO + 1) * ((e - w) / RESOLUCAO + 1)
    return pontos * n_anos * 12 * len(VARIAVEIS) * 2 / 1e9


def confirmar_dominio(area, n_anos, sim=False):
    """Mostra o tamanho do domínio e pede confirmação se ele for grande."""
    n, w, s, e = area
    tamanho = estimar_tamanho_gb(area, n_anos)
    print(f"Área [N, W, S, E]: {area}  ({n - s:.1f}° x {e - w:.1f}°)")
    print(f"Tamanho estimado: {tamanho:.2f} GB")
    if tamanho <= LIMITE_GB:
        return
    print("\n" + "!" * 60)
    print("⚠ ATENÇÃO: domínio grande.")
    print("  Prefira boxes menores no namelist.txt: o download fica lento e o")
    print("  processamento pode não caber na memória. Se precisar do domínio")
    print("  inteiro (ex.: média global), considere uma resolução mais grossa.")
    print("!" * 60 + "\n")
    if sim:
        return
    if input("Continuar mesmo assim? [s/N] ").strip().lower() not in ("s", "sim"):
        sys.exit("Download cancelado.")


def baixar_com_tentativas(client, dataset, request, destino, tentativas=TENTATIVAS, espera=60):
    """Baixa um pedido, tentando de novo se o CDS falhar (ex.: 'OperationalError' no servidor).
    Erros de pedido grande demais não são repetidos: é preciso diminuir ANOS_POR_PEDIDO."""
    for n in range(1, tentativas + 1):
        try:
            client.retrieve(dataset, request).download(str(destino))
            return
        except Exception as e:
            if "too large" in str(e) or n == tentativas:
                raise
            print(f"  Falha no CDS ({type(e).__name__}); nova tentativa {n + 1}/{tentativas} em {espera} s...")
            logging.warning(f"Falha no CDS, tentativa {n}/{tentativas}: {e}")
            time.sleep(espera)


def download_data(modo="analise", ano_inicio=ANO_INICIO, ano_fim=ANO_FIM, sim=False):
    """Baixa as médias mensais do ERA5 em blocos de anos e junta tudo em
    um arquivo por stepType em datain/raw (analise) ou datain/raw/clima (clima)."""
    if modo == "clima":
        ano_inicio, ano_fim = cm.NORMAL
    dir_out = cm.dir_raw(modo)

    print(f"Modo: {modo}   Anos: {ano_inicio}–{ano_fim}")
    print(f"Diretório de saída:  {dir_out}")
    print('-' * 50)

    area = AREA if (AREA is not None and modo == "analise") else area_dos_boxes()
    if AREA is not None and modo == "analise":
        n, w, s, e = AREA
        caixas = cm.ler_namelist()
        fora = caixas[(caixas.lat_max > n) | (caixas.lat_min < s) | (caixas.lon_min < w) | (caixas.lon_max > e)]
        if not fora.empty:
            sys.exit(f"Boxes fora da AREA {AREA}: {fora[['exp_name', 'name']].values.tolist()}")
    anos = list(range(ano_inicio, ano_fim + 1))
    confirmar_dominio(area, len(anos), sim)

    tempo_inicio = time.time()
    cm.DIR_LOGS.mkdir(parents=True, exist_ok=True)
    dir_out.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=cm.DIR_LOGS / 'download.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    dataset = "reanalysis-era5-single-levels-monthly-means"
    blocos = [anos[i:i + ANOS_POR_PEDIDO] for i in range(0, len(anos), ANOS_POR_PEDIDO)]

    logging.info(f"Iniciando o download dos dados do ERA5 (modo {modo}).")
    logging.info(f"Requisição: {dataset}")
    logging.info("Variáveis solicitadas: " + ", ".join(VARIAVEIS))
    logging.info(f"Período: {ano_inicio}–{ano_fim} em {len(blocos)} pedidos. Área [N, W, S, E]: {area}")
    print(f"{len(blocos)} pedidos ao CDS. Aguarde, isso pode levar alguns minutos...")

    client = cdsapi.Client()
    dir_tmp = dir_out / "_blocos"
    for bloco in blocos:
        dir_bloco = dir_tmp / f"{bloco[0]}_{bloco[-1]}"
        if dir_bloco.exists() and any(dir_bloco.glob("*.nc")):
            print(f"Bloco {bloco[0]}–{bloco[-1]} já baixado, pulando")
            continue
        dir_bloco.mkdir(parents=True, exist_ok=True)

        request = {
            "product_type": ["monthly_averaged_reanalysis"],
            "variable": VARIAVEIS,
            "year": [str(ano) for ano in bloco],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "time": ["00:00"],
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": area,
        }
        print(f"Baixando {bloco[0]}–{bloco[-1]}...")
        logging.info(f"Baixando {bloco[0]}–{bloco[-1]}")
        # Com várias variáveis o CDS devolve um .zip com um .nc por "stepType"
        destino = dir_bloco / "download.tmp"
        baixar_com_tentativas(client, dataset, request, destino)
        if zipfile.is_zipfile(destino):
            with zipfile.ZipFile(destino, 'r') as zip_ref:
                zip_ref.extractall(dir_bloco)
            destino.unlink()
        else:
            destino.rename(dir_bloco / "era5_download.nc")

    # Junta os blocos: um arquivo por nome (stepType)
    nomes = sorted({f.name for f in dir_tmp.glob("*/*.nc")})
    for nome in nomes:
        partes = sorted(dir_tmp.glob(f"*/{nome}"))
        with xr.open_mfdataset(partes, combine="nested", concat_dim="valid_time",
                               data_vars="minimal", coords="minimal", compat="override") as ds:
            ds.sortby("valid_time").to_netcdf(dir_out / nome)
        print(f"✔ {nome} ({len(partes)} blocos) salvo em {dir_out}")
    shutil.rmtree(dir_tmp)
    print("✔ Dados do ERA5 baixados com sucesso.")

    tempo_minutos = (time.time() - tempo_inicio) / 60
    print(f"Tempo total de download: {tempo_minutos:.2f} minutos")
    logging.info(f"Tempo total de download: {tempo_minutos:.2f} minutos")


def baixar_mascara():
    """Baixa a land_sea_mask global do ERA5 (campo fixo: basta um mês, ~4 MB).
    A área explícita mantém a longitude em -180..180, como no namelist."""
    destino = cm.MASCARA_LSM
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    print("Baixando a máscara continente/oceano (land_sea_mask)...")
    cdsapi.Client().retrieve("reanalysis-era5-single-levels-monthly-means", {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["land_sea_mask"],
        "year": ["2020"],
        "month": ["01"],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [90, -180, -90, 180],
    }).download(str(tmp))
    if zipfile.is_zipfile(tmp):
        with zipfile.ZipFile(tmp) as z:
            nc = [n for n in z.namelist() if n.endswith(".nc")][0]
            destino.write_bytes(z.read(nc))
        tmp.unlink()
    else:
        tmp.rename(destino)
    print(f"✔ Máscara salva em {destino}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("modo", nargs="?", default="analise", choices=(*cm.MODOS, "mascara"))
    p.add_argument("ano_inicio", nargs="?", type=int, default=ANO_INICIO)
    p.add_argument("ano_fim", nargs="?", type=int, default=ANO_FIM)
    p.add_argument("--sim", action="store_true", help="não pede confirmação para domínios grandes")
    a = p.parse_args()
    if a.modo == "mascara":
        baixar_mascara()
    else:
        download_data(a.modo, a.ano_inicio, a.ano_fim, a.sim)


if __name__ == "__main__":
    main()

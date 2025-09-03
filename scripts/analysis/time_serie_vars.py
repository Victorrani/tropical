import pandas as pd
import xarray as xr
from pathlib import Path


# DataFrame vazio que vamos preencher
def time_series_var():
    """Gera uma tabela de séries temporais com médias espaciais para cada variável em arquivos NetCDF."""


    DIR_SCRIPT = Path(__file__).resolve().parent
    DIR_ROOT = DIR_SCRIPT.parent.parent
    DIR_DATAIN = DIR_ROOT / "datain" / "processed"

# Lista de arquivos NetCDF
    files = sorted(DIR_DATAIN.glob("*.nc"))

    for file in files:
        df_resultado = pd.DataFrame()
        print(f"Lendo arquivo: {file}")
        ds = xr.open_dataset(file)
        ds = ds.rename({'valid_time': 'time'})
        nome_file = file.stem

        print(f"  Nome do arquivo: {nome_file}")
        # Calcula a média espacial para cada variável em cada tempo
        medias = {}
        for var in ds.data_vars:
            unidade = getattr(ds[var], "units", "unknown")
            nome_completa = getattr(ds[var], "long_name", var)
            nome_coluna = f"{var} ({unidade}) ({nome_completa})"
            print(f"  Processando variável: {var} -> coluna: {nome_coluna}")

            # Reduz em todas as dimensões menos 'time'
            medias[nome_coluna] = ds[var].mean(dim=["latitude", "longitude"])

        # Converte para DataFrame
        df_medias = xr.Dataset(medias).to_dataframe()

        # Junta no DataFrame final
        df_resultado = pd.concat([df_resultado, df_medias])
        df_resultado = df_resultado.drop(columns=["number", "expver"], errors="ignore")

        # Resetar o índice (para garantir que 'time' vire coluna)
        df_resultado = df_resultado.reset_index()

        print(df_resultado.columns)

        # trabalhando nas unidades e sinais das variáveis
        df_resultado['tp_mm (mm) (Total precipitation)'] = df_resultado['tp (m) (Total precipitation)'] * 1000 * 30 
        df_resultado['avg_ie (kg m**-2 s**-1) (Time-mean moisture flux)']
        df_resultado['avg_sdirswrf (W m**-2) (Time-mean surface direct short-wave radiation flux)']
        df_resultado['avg_sdirswrfcs (W m**-2) (Time-mean surface direct short-wave radiation flux, clear sky)']
        df_resultado['avg_sdlwrf (W m**-2) (Time-mean surface downward long-wave radiation flux)']
        df_resultado['avg_sdlwrfcs (W m**-2) (Time-mean surface downward long-wave radiation flux, clear sky)']
        df_resultado['avg_sdswrf (W m**-2) (Time-mean surface downward short-wave radiation flux)']
        df_resultado['avg_sdswrfcs (W m**-2) (Time-mean surface downward short-wave radiation flux, clear sky)']
        df_resultado['avg_sduvrf (W m**-2) (Time-mean surface downward UV radiation flux)']
        df_resultado['avg_slhtf (W m**-2) (Time-mean surface latent heat flux)'] = df_resultado['avg_slhtf (W m**-2) (Time-mean surface latent heat flux)'] * (-1)
        df_resultado['avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)'] = df_resultado['avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)'] * (-1)
        df_resultado['avg_snlwrfcs (W m**-2) (Time-mean surface net long-wave radiation flux, clear sky)']
        df_resultado['avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)'] = df_resultado['avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)']  * (-1)
        df_resultado['avg_snswrfcs (W m**-2) (Time-mean surface net short-wave radiation flux, clear sky)']
        df_resultado['avg_ishf (W m**-2) (Time-mean surface sensible heat flux)'] = df_resultado['avg_ishf (W m**-2) (Time-mean surface sensible heat flux)'] * (-1)
        df_resultado['avg_tdswrf (W m**-2) (Time mean top downward short-wave radiation flux)']
        df_resultado['avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)'] = df_resultado['avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)'] * (-1)
        df_resultado['avg_tnlwrfcs (W m**-2) (Time-mean top net long-wave radiation flux, clear sky)']
        df_resultado['avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)'] = df_resultado['avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)'] * (-1)
        df_resultado['avg_tnswrfcs (W m**-2) (Time-mean top net short-wave radiation flux, clear sky)']
        df_resultado['avg_tprate_W (W m**-2) (Time-mean total precipitation rate)'] = df_resultado['avg_tprate (kg m**-2 s**-1) (Time-mean total precipitation rate)'] * 2500000
        df_resultado['avg_vimdf (kg m**-2 s**-1) (Time-mean total column vertically-integrated moisture divergence flux)']


        #earth balance 
        lw_nettop = df_resultado['avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)']
        sw_nettop = df_resultado['avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)']

        #atmospheric balance
        sw_netsrf = df_resultado['avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)']
        lw_netsrf = df_resultado['avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)']
        lh = df_resultado['avg_slhtf (W m**-2) (Time-mean surface latent heat flux)']
        sh = df_resultado['avg_ishf (W m**-2) (Time-mean surface sensible heat flux)']
        mtpr = df_resultado['avg_tprate_W (W m**-2) (Time-mean total precipitation rate)']

        #surface balance

        df_resultado['balanc_earth (W m**-2) (earth_balance)'] = lw_nettop + sw_nettop

        df_resultado['balanc_atmos (W m**-2) (atmospheric_balance)'] = (-1)*(sw_nettop - sw_netsrf) + (-1)*(lw_nettop - lw_netsrf) + sh + mtpr

        df_resultado['balanc_surface (W m**-2) (surface_balance)'] = (-1) * (sw_netsrf + lw_netsrf) - sh - lh

        print(df_resultado.columns)


        

        # Salvar em CSV
        out_csv = DIR_ROOT / "dataout" / "tables" / f"time_series_{nome_file}.csv"
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df_resultado.to_csv(out_csv, index=False)
        print(f"\nTabela salva em: {out_csv}")

if __name__ == "__main__":
    time_series_var()
    
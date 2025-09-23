import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import re

def desv():

    # Dicionário de limites para cada variável
    limits_dict = {
        'cbh (m) (Cloud base height)': [0, 5000],
        'd2m (K) (2 metre dewpoint temperature)': [280, 310],
        't2m (K) (2 metre temperature)': [260, 310],
        'hcc ((0 - 1)) (High cloud cover)': [0, 1],
        'lcc ((0 - 1)) (Low cloud cover)': [0, 1],
        'mcc ((0 - 1)) (Medium cloud cover)': [0, 1],
        'tcc ((0 - 1)) (Total cloud cover)': [0, 1],
        'tcw (kg m**-2) (Total column water)': [0, 100],
        'tcwv (kg m**-2) (Total column vertically-integrated water vapour)': [0, 100],
        'tp (m) (Total precipitation)': [0, 0.03],
        'avg_ie (kg m**-2 s**-1) (Time-mean moisture flux)': [-1e-4, 0],
        'avg_sdirswrf (W m**-2) (Time-mean surface direct short-wave radiation flux)': [0, 300],
        'avg_sdirswrfcs (W m**-2) (Time-mean surface direct short-wave radiation flux, clear sky)': [0, 300],
        'avg_sdlwrf (W m**-2) (Time-mean surface downward long-wave radiation flux)': [300, 500],
        'avg_sdlwrfcs (W m**-2) (Time-mean surface downward long-wave radiation flux, clear sky)': [300, 450],
        'avg_sdswrf (W m**-2) (Time-mean surface downward short-wave radiation flux)': [100, 300],
        'avg_sdswrfcs (W m**-2) (Time-mean surface downward short-wave radiation flux, clear sky)': [200, 400],
        'avg_sduvrf (W m**-2) (Time-mean surface downward UV radiation flux)': [0, 50],
        'avg_slhtf (W m**-2) (Time-mean surface latent heat flux)': [0, 150],
        'avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)': [0, 200],
        'avg_snlwrfcs (W m**-2) (Time-mean surface net long-wave radiation flux, clear sky)': [-200, 0],
        'avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)': [-500, 0],
        'avg_snswrfcs (W m**-2) (Time-mean surface net short-wave radiation flux, clear sky)': [0, 500],
        'avg_ishf (W m**-2) (Time-mean surface sensible heat flux)': [-5, 100],
        'avg_tdswrf (W m**-2) (Time mean top downward short-wave radiation flux)': [0, 600],
        'avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)': [0, 400],
        'avg_tnlwrfcs (W m**-2) (Time-mean top net long-wave radiation flux, clear sky)': [-400, -200],
        'avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)': [-400, -200],
        'avg_tnswrfcs (W m**-2) (Time-mean top net short-wave radiation flux, clear sky)': [0, 500],
        'avg_tprate (kg m**-2 s**-1) (Time-mean total precipitation rate)': [0, 2e-4],
        'avg_vimdf (kg m**-2 s**-1) (Time-mean total column vertically-integrated moisture divergence flux)': [-2e-4, 2e-4],
        'tp_mm (mm) (Total precipitation)': [0, 500],
        'avg_tprate_W (W m**-2) (Time-mean total precipitation rate)': [0, 500],
        't2m (°C) (2 metre temperature)': [15, 35],
        'd2m (°C) (2 metre dewpoint temperature)': [5, 30],
        'balanc_earth (W m**-2) (earth_balance)': [-250, 250],
        'balanc_atmos (W m**-2) (atmospheric_balance)': [-300, 300],
        'balanc_surface (W m**-2) (surface_balance)': [-10, 10]
    }

    DIR_SCRIPT = Path(__file__).resolve().parent
    DIR_ROOT = DIR_SCRIPT.parent.parent

    # Diretórios importantes
    DIR_FIGS = DIR_ROOT / "dataout"
    DIR_BOX = DIR_ROOT / "dataout" / "tables" 

    print("Raiz do projeto:", DIR_ROOT) 
    print("Diretório do script:", DIR_SCRIPT)
    print("Diretório de saída:", DIR_FIGS)
    print("Preparando os plots de todas as variáveis do dataset gerado pelo namelist.txt...")

    df_box = pd.read_csv(DIR_BOX / "boxes.csv")
    print(df_box.head())

    # Itera sobre todas as combinações de exp_name e name
    for idx, row in df_box.iterrows():
        exp_name = row['exp_name']
        name     = row['name']

        DIR_CSV = DIR_FIGS / "tables" / exp_name 

        clima = pd.read_csv(DIR_CSV / f'{exp_name}_{name}_clima.csv')
        data = pd.read_csv(DIR_CSV / f'time_series_{exp_name}_{name}.csv')

        print(clima.head())
        print(data.head())
        
        # Converter a coluna time para datetime
        data['time'] = pd.to_datetime(data['time'])
        
        # CRIAR A COLUNA 'mes' NO DATA - ESSE ERA O PROBLEMA!
        data['mes'] = data['time'].dt.month
        
        # Garantir que a coluna 'mes' do clima é inteira
        clima['mes'] = clima['mes'].astype(int)
        
        print("Valores únicos de mês no clima:", sorted(clima['mes'].unique()))
        print("Valores únicos de mês no data:", sorted(data['mes'].unique()))
        
        # Agora ambos os DataFrames têm a coluna 'mes'
        print("Colunas do data após criar 'mes':", data.columns.tolist())
        print("Colunas do clima:", clima.columns.tolist())
        
        # Fazer o merge
        df_anomalias = data.merge(clima, on='mes', suffixes=('_serie', '_clima'))
        print('Merge realizado com sucesso')
        
        # Calcular anomalias automaticamente para colunas numéricas comuns
        colunas_serie = [col for col in data.columns if col not in ['time', 'mes']]
        colunas_clima = [col for col in clima.columns if col != 'mes']
        
        # Encontrar colunas comuns (que existem em ambos os datasets)
        colunas_comuns = list(set(colunas_serie) & set(colunas_clima))
        
        print("Colunas para cálculo de anomalias:")
        print(colunas_comuns)
        
        # Calcular anomalias
        for coluna in colunas_comuns:
            df_anomalias[f'{coluna}'] = df_anomalias[f'{coluna}_serie'] - df_anomalias[f'{coluna}_clima']
        
        # Manter apenas colunas relevantes no resultado final
        colunas_finais = ['time', 'mes'] + [f'{col}' for col in colunas_comuns]
        df_resultado = df_anomalias[colunas_finais]

        print("\nResultado final:")
        print(df_resultado.columns)
        df_resultado.to_csv(DIR_CSV / f'anomalias_{exp_name}_{name}.csv', index=False)

if __name__ == "__main__":
    desv()
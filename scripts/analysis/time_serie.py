import pandas as pd
import xarray as xr
from pathlib import Path

DIR_SCRIPT = Path(__file__).resolve().parent
DIR_ROOT = DIR_SCRIPT.parent.parent
DIR_DATAIN = DIR_ROOT / "datain" / "processed"

# Lista de arquivos NetCDF
files = sorted(DIR_DATAIN.glob("*.nc"))

# DataFrame vazio que vamos preencher
df_resultado = pd.DataFrame()

for file in files:
    print(f"Lendo arquivo: {file}")
    ds = xr.open_dataset(file)
    ds = ds.rename({'valid_time': 'time'})
    
    # Calcula a média espacial para cada variável em cada tempo
    medias = {}
    for var in ds.data_vars:
        unidade = getattr(ds[var], "units", "unknown")
        nome_coluna = f"{var} ({unidade})"
        print(f"  Processando variável: {var} -> coluna: {nome_coluna}")
        
        # Reduz em todas as dimensões menos 'time'
        medias[nome_coluna] = ds[var].mean(dim=[d for d in ds[var].dims if d != "time"])
    
    # Converte para DataFrame
    df_medias = xr.Dataset(medias).to_dataframe()
    
    # Junta no DataFrame final
    df_resultado = pd.concat([df_resultado, df_medias])
    df_resultado = df_resultado.drop(columns=["number", "expver"], errors="ignore")

# Resetar o índice (para garantir que 'time' vire coluna)
df_resultado = df_resultado.reset_index()

print("\nPrévia do DataFrame final:")
print(df_resultado.head())

# Salvar em CSV
out_csv = DIR_ROOT / "dataout" / "tables" / "medias_variaveis.csv"
out_csv.parent.mkdir(parents=True, exist_ok=True)
df_resultado.to_csv(out_csv, index=False)
print(f"\nTabela salva em: {out_csv}")

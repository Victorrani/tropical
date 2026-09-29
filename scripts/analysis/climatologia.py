import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm


def ciclo_anual(df):
    """Média de cada mês (1..12) de todas as colunas numéricas."""
    return df.groupby(df['time'].dt.month.rename('mes')).mean(numeric_only=True)


def normal(row):
    """Normal climatológica (common.NORMAL) a partir de time_series_normal_*.csv.
    As coordenadas do box ficam gravadas no topo do arquivo."""
    exp_name, name = row['exp_name'], row['name']
    file = cm.arq_serie(exp_name, name, "clima")
    if not file.exists():
        return
    print(f"Lendo arquivo: {file}")

    df = pd.read_csv(file, parse_dates=['time'])
    ini, fim = cm.NORMAL
    df = df[(df['time'].dt.year >= ini) & (df['time'].dt.year <= fim)]

    esperado = (fim - ini + 1) * 12
    if len(df) < esperado:
        print(f"  Atenção: {len(df)} de {esperado} meses da normal {ini}–{fim} disponíveis")

    out = cm.arq_normal(exp_name, name)
    cm.salvar_com_box(ciclo_anual(df), out, cm.box_de(row))
    print(f"{cm.NORMAL_ROTULO} salva em: {out}")


def climatologia_serie(row):
    """Ciclo anual da série analisada ({exp}_{nome}_clima.csv) e ciclos anuais por
    década ({exp}_{nome}_clima_AAAA_AAAA.csv). As décadas usam a série da normal
    (1991–2020, se existir e for do mesmo box) junto com a série analisada."""
    exp_name, name = row['exp_name'], row['name']
    file = cm.arq_serie(exp_name, name)
    if not file.exists():
        return
    print(f"Lendo arquivo: {file}")

    df = pd.read_csv(file, parse_dates=['time'])
    print(f"Período dos dados: {df['time'].min():%m/%Y}–{df['time'].max():%m/%Y}")
    ciclo_anual(df).to_csv(cm.arq_clima(exp_name, name))
    print(f"Climatologia da série salva em: {cm.arq_clima(exp_name, name)}")

    # junta a série da normal (1991–2020) com a analisada; nos meses repetidos vale a analisada
    arq_normal_serie = cm.arq_serie(exp_name, name, "clima")
    if arq_normal_serie.exists() and cm.ler_normal(row) is not None:
        base = pd.read_csv(arq_normal_serie, parse_dates=['time'])
        df = pd.concat([base, df]).drop_duplicates('time', keep='last').sort_values('time')
    ano = df['time'].dt.year

    # remove tabelas de períodos antigas antes de gravar as novas
    for antigo in cm.dir_tabelas(exp_name).glob(f"{exp_name}_{name}_clima_*.csv"):
        antigo.unlink()

    for ini, fim in cm.decadas(ano):
        sel = (ano >= ini) & (ano <= fim)
        anos = ano[sel].unique()
        if len(anos) < cm.COBERTURA_MINIMA * (fim - ini + 1):
            if len(anos):
                print(f"  {ini}–{fim}: só {len(anos)} ano(s) de dados; década ignorada")
            continue
        # nome do arquivo com os anos que existem de fato (ex.: 2021_2025)
        ciclo_anual(df[sel]).to_csv(cm.arq_clima(exp_name, name, f"{anos.min()}_{anos.max()}"))
        print(f"  Década {anos.min()}–{anos.max()} ({len(anos)} anos)")


def climatologia():
    df_box = cm.ler_boxes()
    print(df_box.head())

    for _, row in df_box.iterrows():
        normal(row)
        climatologia_serie(row)


if __name__ == "__main__":
    climatologia()

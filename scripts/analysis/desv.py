import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm


def referencia(row):
    """Climatologia de referência do box: a normal (se existir e for do mesmo box)
    ou, na falta dela, o ciclo anual da própria série."""
    exp_name, name = row['exp_name'], row['name']

    arq_normal = cm.arq_normal(exp_name, name)
    if arq_normal.exists():
        clima, box = cm.ler_csv_com_box(arq_normal, index_col='mes')
        if not cm.mesmo_box(box, cm.box_de(row)):
            print(f"  ERRO: {arq_normal.name} foi gerada para outro domínio ({box}),\n"
                  f"  mas o box atual é {cm.box_de(row)}. Refaça a normal: python scripts/analysis/normal.py")
            return None, None
        return clima, cm.NORMAL_ROTULO

    arq_clima = cm.arq_clima(exp_name, name)
    if arq_clima.exists():
        print(f"  Atenção: normal não encontrada; usando a média da própria série.\n"
              f"  Para usar a {cm.NORMAL_ROTULO}: python scripts/analysis/normal.py")
        return pd.read_csv(arq_clima, index_col='mes'), "média da série"

    print(f"  Atenção: nenhuma climatologia para {exp_name}/{name}. Rode antes climatologia.py")
    return None, None


def desv():
    """Anomalias mensais: série temporal menos a climatologia do mesmo mês."""

    df_box = cm.ler_boxes()
    print(df_box.head())

    for _, row in df_box.iterrows():
        exp_name = row['exp_name']
        name = row['name']
        print(f"{exp_name}/{name}")

        arq_serie = cm.arq_serie(exp_name, name)
        if not arq_serie.exists():
            print(f"  Atenção: {arq_serie} não encontrado. Rode antes time_serie_vars.py")
            continue

        clima, rotulo = referencia(row)
        if clima is None:
            continue

        data = pd.read_csv(arq_serie, parse_dates=['time'])
        data['mes'] = data['time'].dt.month

        colunas = [c for c in data.columns if c in clima.columns]
        clima_por_linha = clima.loc[data['mes'], colunas].to_numpy()

        df_resultado = data[['time', 'mes']].copy()
        df_resultado[colunas] = data[colunas].to_numpy() - clima_por_linha

        out = cm.arq_anomalias(exp_name, name)
        df_resultado.to_csv(out, index=False)
        print(f"  Anomalias em relação à {rotulo} ({len(colunas)} variáveis) salvas em: {out}")


if __name__ == "__main__":
    desv()

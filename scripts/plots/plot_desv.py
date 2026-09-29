import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm


def plot_desv():
    """Anomalias mensais de cada variável de cada box: barras (vermelho > 0,
    azul < 0) e média móvel de 12 meses.

    O eixo y é simétrico e o mesmo para todos os boxes (automático, ou fixo
    em common.LIMITES_ANOMALIA)."""

    df_box = cm.ler_boxes()
    print(df_box.head())

    dados = []
    for _, row in df_box.iterrows():
        file = cm.arq_anomalias(row['exp_name'], row['name'])
        if not file.exists():
            print(f"Atenção: {file} não encontrado. Rode antes desv.py")
            continue
        dados.append((row, pd.read_csv(file, parse_dates=["time"])))

    variaveis = dict.fromkeys(c for _, df in dados for c in df.columns.drop(["time", "mes"]))
    for var in variaveis:
        ylim = cm.limites(var, [df[var] for _, df in dados if var in df], cm.LIMITES_ANOMALIA, simetrico=True)
        nome_abreviado, unidade, nome_completo = cm.separar_nome_coluna(var)

        for row, df in dados:
            if var not in df:
                continue
            exp_name, name = row['exp_name'], row['name']
            cores = np.where(df[var] >= 0, 'tab:red', 'tab:blue')

            fig, ax = plt.subplots(figsize=(20, 6))
            ax.bar(df["time"], df[var], width=25, color=cores, alpha=0.8)
            ax.plot(df["time"], df[var].rolling(12, center=True).mean(),
                    color='black', linewidth=2, label='Média móvel 12 meses')
            ax.axhline(0, color='black', linewidth=0.8)

            ax.set_title(f'Anomalia de {nome_completo} — {exp_name} {name}')
            ax.set_xlabel('Tempo')
            ax.set_ylabel(unidade)
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.grid(True, alpha=0.4)
            ax.legend(loc='upper left')
            if ylim:
                ax.set_ylim(ylim)

            outdir = cm.dir_figuras(exp_name, name, "anomalias")
            fig.savefig(outdir / f'{exp_name}_{name}_{nome_abreviado}_anomalias_time_series.jpg',
                        dpi=cm.DPI, bbox_inches='tight')
            plt.close(fig)
        print(f'Plotado: {var}')


if __name__ == "__main__":
    plot_desv()

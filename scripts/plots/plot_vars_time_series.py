import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm


def plot_vars_time_series():
    """Série temporal de cada variável de cada box, com a normal climatológica
    (quando existir) e a média móvel de 12 meses.

    O eixo y tem a mesma amplitude em todos os boxes, centrada nos dados de cada
    um: a variabilidade é comparável entre domínios sem achatar as curvas de quem
    tem valores médios diferentes (ex.: temperatura no Sul x Amazônia).
    Limites fixos podem ser definidos em common.LIMITES_SERIE."""

    df_box = cm.ler_boxes()
    print(df_box.head())

    # Lê tudo antes para calcular limites comuns a todos os boxes
    dados = []
    for _, row in df_box.iterrows():
        file = cm.arq_serie(row['exp_name'], row['name'])
        if not file.exists():
            print(f"Atenção: {file} não encontrado. Rode antes time_serie_vars.py")
            continue
        df = pd.read_csv(file, parse_dates=["time"])
        normal = cm.ler_normal(row)
        # normal repetida em cada mês da série (mesmo índice que df)
        normal_serie = normal.loc[df["time"].dt.month].set_index(df.index) if normal is not None else None
        dados.append((row, df, normal_serie))

    variaveis = dict.fromkeys(c for _, df, _ in dados for c in df.columns.drop("time"))
    for var in variaveis:
        # limites automáticos de cada box e a maior amplitude entre eles
        lims = {}
        for i, (_, df, n) in enumerate(dados):
            if var in df:
                lims[i] = cm.limites_auto([df[var]] + ([n[var]] if n is not None and var in n else []))
        amplitude = max((hi - lo for lo, hi in filter(None, lims.values())), default=None)
        nome_abreviado, unidade, nome_completo = cm.separar_nome_coluna(var)

        for i, (row, df, normal_serie) in enumerate(dados):
            if var not in df:
                continue
            ylim = cm.LIMITES_SERIE.get(var)
            if ylim is None and lims.get(i) and amplitude:
                centro = sum(lims[i]) / 2
                ylim = [centro - amplitude / 2, centro + amplitude / 2]
            exp_name, name = row['exp_name'], row['name']

            fig, ax = plt.subplots(figsize=(20, 6))
            ax.plot(df["time"], df[var], marker='o', markersize=3, linewidth=1, label='Mensal')
            ax.plot(df["time"], df[var].rolling(12, center=True).mean(),
                    color='black', linewidth=2, label='Média móvel 12 meses')
            if normal_serie is not None and var in normal_serie:
                ax.plot(df["time"], normal_serie[var], color='gray', linestyle='--',
                        linewidth=1.2, label=cm.NORMAL_ROTULO)

            ax.set_title(f'{nome_completo} — {exp_name} {name}')
            ax.set_xlabel('Tempo')
            ax.set_ylabel(unidade)
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.grid(True, alpha=0.4)
            ax.legend(loc='upper left')
            if ylim:
                ax.set_ylim(ylim)

            out = cm.dir_figuras(exp_name, name) / f'{exp_name}_{name}_{nome_abreviado}_time_series.jpg'
            fig.savefig(out, dpi=cm.DPI, bbox_inches='tight')
            plt.close(fig)
        print(f'Plotado: {var}')


if __name__ == "__main__":
    plot_vars_time_series()

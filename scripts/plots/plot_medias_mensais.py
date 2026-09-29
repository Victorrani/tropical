"""
Plota o ciclo anual (média de cada mês) de uma variável:
  - normal climatológica 1991–2020 (referência, tracejado cinza);
  - cada década (1991–2000, 2001–2010, ...), com cores em ordem temporal;
  - a série analisada, com as datas no rótulo (linha preta).

Uso:
    python scripts/plots/plot_medias_mensais.py            # escolhe a variável no terminal
    python scripts/plots/plot_medias_mensais.py tp_mm      # pelo nome abreviado
    python scripts/plots/plot_medias_mensais.py all        # todas as variáveis
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as cm

MARCADORES = ['s', '^', 'D', 'v', 'P', 'X']
CORES_DECADAS = "cividis"  # sequencial azul -> amarelo, segura para daltonismo
MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


def escolher_variaveis(colunas, escolha=None):
    """Aceita o nome abreviado, o nome completo da coluna, o número da lista ou 'all'."""
    por_abrev = {cm.separar_nome_coluna(c)[0]: c for c in colunas}

    while True:
        if escolha is None:
            for i, c in enumerate(colunas):
                print(f"{i:3d}  {c}")
            escolha = input("Escolha a variável para plotar (número, nome abreviado ou 'all'): ").strip()

        if escolha == "all":
            return list(colunas)
        if escolha.isdigit() and int(escolha) < len(colunas):
            return [colunas[int(escolha)]]
        if escolha in colunas:
            return [escolha]
        if escolha in por_abrev:
            return [por_abrev[escolha]]
        print(f"Variável '{escolha}' não encontrada.")
        escolha = None


def plot_medias(escolha=None):

    df_box = cm.ler_boxes()
    variaveis = None

    for _, row in df_box.iterrows():
        exp_name = row["exp_name"]
        name = row["name"]

        # (rótulo, tabela, estilo da linha)
        tabelas = []
        normal = cm.ler_normal(row)
        if normal is not None:
            tabelas.append((cm.NORMAL_ROTULO, normal,
                            dict(color='gray', linestyle='--', linewidth=3, zorder=3)))

        decadas = cm.arqs_clima_decadas(exp_name, name)
        # até 0.8 da escala: o amarelo do fim da cividis fica claro demais no fundo branco
        cores = plt.get_cmap(CORES_DECADAS)([0.8 * i / max(len(decadas) - 1, 1) for i in range(len(decadas))])
        for (ini, fim, arq), cor, marker in zip(decadas, cores, MARCADORES * 3):
            tabelas.append((f"{ini}–{fim}", pd.read_csv(arq, index_col="mes"),
                            dict(color=cor, marker=marker, linewidth=1.3, markersize=5)))

        arq_serie = cm.arq_serie(exp_name, name)
        if arq_serie.exists() and cm.arq_clima(exp_name, name).exists():
            t = pd.read_csv(arq_serie, usecols=["time"], parse_dates=["time"])["time"]
            rotulo = f"Série {t.min():%m/%Y}–{t.max():%m/%Y}"
            tabelas.append((rotulo, pd.read_csv(cm.arq_clima(exp_name, name), index_col="mes"),
                            dict(color='black', marker='o', linewidth=2.5, zorder=4)))

        if not tabelas:
            print(f"Atenção: nenhuma climatologia para {exp_name}/{name}. Rode antes climatologia.py")
            continue

        # a variável é escolhida uma vez e usada em todos os boxes
        if variaveis is None:
            variaveis = escolher_variaveis(list(tabelas[0][1].columns.drop("ano", errors="ignore")), escolha)

        outdir = cm.dir_figuras(exp_name, name, "clima")
        for var_name in variaveis:
            nome_abreviado, unidade, nome_var = cm.separar_nome_coluna(var_name)

            fig, ax = plt.subplots(figsize=(20, 6))
            for rotulo, tab, estilo in tabelas:
                if var_name in tab.columns and not tab.empty:
                    ax.plot(tab.index, tab[var_name], label=rotulo, **estilo)

            ax.set_title(f'Ciclo anual de {nome_var} — {exp_name} {name}')
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(MESES)
            ax.set_xlim(0.5, 12.5)
            ax.set_xlabel('Mês')
            ax.set_ylabel(unidade)
            ax.grid(True, alpha=0.4)
            ax.legend(ncol=2)

            out = outdir / f'{exp_name}_{name}_clima_{nome_abreviado}.jpg'
            fig.savefig(out, dpi=cm.DPI, bbox_inches='tight')
            plt.close(fig)
            print(f"Figura salva em: {out}")


if __name__ == "__main__":
    plot_medias(sys.argv[1] if len(sys.argv) > 1 else None)

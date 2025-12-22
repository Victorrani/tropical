# Projeto: Balanços de Radiação em Domínios Específicos

**Disciplina:** Meteorologia Tropical - IAG/USP  
**Autor:** Victor Antunes Ranieri  
**Data:** [2025-12-22]

## 📋 Objetivo
Processar, analisar e visualizar balanços de radiação atmosférica para regiões específicas (boxes), 
utilizando dados de reanálise ERA5.

## 🗂️ Estrutura de Diretórios
```
├── datain/               # Dados de entrada (input)
│   ├── processed/        # Subconjuntos processados (regiões/temporalidades específicas)
│   └── raw/              # Dados brutos completos (originais, imutáveis)
│
├── dataout/              # Resultados e saídas (output)
│   └── tables/           # Tabelas geradas a partir das análises
│
├── env/                  # Configuração do ambiente virtual/conda
│   └── environment.yml   # Especificação das dependências do projeto
│
├── logs/                 # Registros de execução (logs)
│   └── download.log      # Exemplo: log específico do download
│
├── notebooks/            # Jupyter notebooks para exploração e análise interativa
│
├── README.md             # Documentação principal do projeto
│
├── scripts/              # Códigos Python reutilizáveis
│   ├── analysis/         # Processamento e cálculos estatísticos
│   │   ├── box_maps.py      # Geração de mapas por região/box
│   │   ├── climatologia.py  # Cálculo de climatologias
│   │   ├── desv.py          # Cálculo de desvios/anomalias
│   │   ├── namelist.txt     # Configurações/parâmetros para análises
│   │   ├── slice.py         # Extração de subconjuntos espaciais/temporais
│   │   └── time_serie_vars.py # Geração de séries temporais
│   │
│   ├── download/         # Obtenção de dados de fontes externas
│   │   └── get_data.py   # Script principal de download
│   │
│   └── plots/            # Visualizações e gráficos
│       ├── nome_variavel.py        # Plots específicos por variável
│       ├── plot_balanc_box.py      # Balanços por região
│       ├── plot_balanc.py          # Gráficos de balanço geral
│       ├── plot_desv.py            # Visualização de desvios/anomalias
│       ├── plot_medias_mensais.py  # Médias mensais
│       ├── plot_vars.py            # Plots genéricos de variáveis
│       └── plot_vars_time_series.py # Séries temporais gráficas
│
└── shapefiles/           # Arquivos geoespaciais (formato Shapefile)
├── continentes.shp # Delimitação continental
└── regioes.shp # Regiões de estudo específicas
```

## Instruçôes para uso

1. Faça o clone do repositório https://github.com/Victorrani/tropical.git
```
git clone https://github.com/Victorrani/tropical.git
```
2. Entre no diretório env para criar o ambiente conda estável
```
cd env
```
```
conda env create -f environment.yml
```
```
conda activate tropical-env
```

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

## Instruções para uso

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
## Download dos dados
1. Antes de executar o script, é necessário instalar a biblioteca cdsapi e configurar sua chave de API do CDS. Para instruções detalhadas de configuração, consulte o guia oficial e a documentação do usuário: https://cds.climate.copernicus.eu/how-to-api
2. Entre no diretório scripts/download você encontrará o script python get_data.py
```
python get_data.py
```
<img width="1360" height="276" alt="image" src="https://github.com/user-attachments/assets/ed786152-6813-4df2-9703-1ca78b0c767d" />

Antes de executar o script, é necessário instalar a biblioteca cdsapi e configurar sua chave de API do CDS. Para instruções detalhadas de configuração, consulte o guia oficial e a documentação do usuário: https://cds.climate.copernicus.eu/how-to-api
Pode acontece de aparecer o erro “Your request is too large, please reduce your selection” dessa, forma você deverá fazer o download alterando o dimínio temporal e espacial do dado. Use um editor de texto para alterar o trecho a seguir do código
<img width="783" height="154" alt="image" src="https://github.com/user-attachments/assets/a9e80744-9d19-4bb4-95fd-1f9e222e9fa6" />
Após o final do download deverá ser encontrado no diretório datain/raw três arquivos no formato netCDF. Não altere o nome desses arquivos.
<img width="963" height="40" alt="image" src="https://github.com/user-attachments/assets/13c3589c-15ec-4e25-9d3f-cbda028f5853" />


## Seleção dos domínios

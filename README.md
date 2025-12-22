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
python scripts/download/get_data.py
```
<img width="1360" height="276" alt="image" src="https://github.com/user-attachments/assets/ed786152-6813-4df2-9703-1ca78b0c767d" />

Antes de executar o script, é necessário instalar a biblioteca cdsapi e configurar sua chave de API do CDS. Para instruções detalhadas de configuração, consulte o guia oficial e a documentação do usuário: https://cds.climate.copernicus.eu/how-to-api
Pode acontece de aparecer o erro “Your request is too large, please reduce your selection” dessa, forma você deverá fazer o download alterando o dimínio temporal e espacial do dado. Use um editor de texto para alterar o trecho a seguir do código
<img width="783" height="154" alt="image" src="https://github.com/user-attachments/assets/a9e80744-9d19-4bb4-95fd-1f9e222e9fa6" />

Após o final do download deverá ser encontrado no diretório datain/raw três arquivos no formato netCDF. Não altere o nome desses arquivos.

<img width="963" height="40" alt="image" src="https://github.com/user-attachments/assets/13c3589c-15ec-4e25-9d3f-cbda028f5853" />

## 📍 Seleção dos Domínios

### 1. Configure o Namelist
Edite `scripts/analysis/namelist.txt` com seus experimentos:

![Formato do Namelist](https://github.com/user-attachments/assets/61ab468e-579e-4f32-90b3-8ae407abe14b)

⚠️ **Atenção:** Use coordenadas dentro dos limites espaciais dos dados brutos.

### 2. Execute o Recorte
```
python scripts/analysis/slice.py
````

<img width="1027" height="562" alt="image" src="https://github.com/user-attachments/assets/eeb4219e-5235-40fb-8d7e-cbd43e34f58b" />

O novo conjunto de dados poderá ser encontrado no diretório datain/processed

<img width="653" height="40" alt="image" src="https://github.com/user-attachments/assets/853dbee8-aad3-4a7c-a07f-d6a65345c7df" />

<img width="810" height="40" alt="image" src="https://github.com/user-attachments/assets/67f008e1-d550-42cf-b90f-74c5781e2e50" />

O arquivo boxes.csv contém a descrição da localização da região selecionada além de ter dados netCDF com informação sobre altura das nuvens, radiação e precipitação

<img width="810" height="40" alt="image" src="https://github.com/user-attachments/assets/373b881b-1973-4454-8b10-53ca7612e65b" />

## Produzindo resultados

## 📈 Equações de Balanço

### 🌍 Balanço Global (TOA)
**TOA = -(Radiação Solar Líquida + Radiação Térmica Líquida)**

### 🌡️ Balanço na Superfície  
**Superfície = -(Rad. Solar + Rad. Térmica) - Calor Sensível - Calor Latente**

### ☁️ Balanço Atmosférico
**Atmosfera = -(Variação de Radiação) + Calor Sensível + Calor Latente da Precipitação**



1. No diretório script/analysis há um script chamado time_serie_vars.py. Ele será o responsável por extrair as informações de todos os arquivos netCDF e transforma-los em tabelas. Isso é feito para cada experimento separadamente.
```
python scripts/analysis/time_serie_vars.py
```

As tabelas dos resultados poderá ser encontrado no diretório dataout/tables 

<img width="630" height="40" alt="image" src="https://github.com/user-attachments/assets/a6d161e8-e5a0-4f0f-86df-8b380c4f5413" />

## Plot dos resultados

No diretório scripts/plots há o script plot_vars_time_series.py. Ele irá produzir os plots básicos de todas as variáveis e criará também já algumas conversões de unidades. Criará também os balanços de superfície, atmosfera e terrestre.

É nesse script que poderá ser alterado os limites para o eixo y dos resultados. Altere os limites se necessário.

Os resultados ficarão no diretório dataout/ separados por experimento e nome

<img width="1166" height="241" alt="image" src="https://github.com/user-attachments/assets/31a7b471-d3b3-488b-9c41-e57f79191692" />

<img width="1169" height="385" alt="image" src="https://github.com/user-attachments/assets/de03d6b7-88c7-460a-acd3-227c806545e5" />


## Gerando a climatologia e desvios da média

No diretório script/analysis há um script chamado climatologia.py. Caso tenha sido necessário alterar o período analisado a climatologia pode ficar ruim. O script foi pensado para utilizar a série de 1980 até 2024.
Rode esse script para gerar as tabelas com as médias dos períodos pré definidos. Os resultados estão em dataout/tables
```
python scripts/analysis/climatologia.py
```

Para calcular os desvios da média utilize o script desv.py 
```
python scripts/analysis/desv.py
```
Importante: Rode os scripts nessa ordem. Podem ocorrer erros se feitos em ordem errada.

Para plotar os resultados comparativos da climatologia e do desvio da média, vá para o diretório scripts/plots

```
python scripts/plots/plot_desv.py
```
<img width="1148" height="375" alt="image" src="https://github.com/user-attachments/assets/69b42bce-90c6-414c-b623-4f200c3d46ac" />

```
python scripts/plots/plot_medias_mensais.py
```
Para esse script é necessário copiar e colar o nome completo. Veja o exemplo a seguir:

<img width="1031" height="274" alt="image" src="https://github.com/user-attachments/assets/212a7798-c476-43af-8560-008d458bfd57" />


<img width="1146" height="382" alt="image" src="https://github.com/user-attachments/assets/c17fe35c-3014-4a85-8aa1-3cc8a69bfff1" />

Como dito anteriormente, esse código foi pensado para uma série longa de 1980 até 2024. Caso seu dado for menor que esse período, algumas series mensais podem não aparecer.

## Variáveis. Nome no arquivo, unidade e nome completo:
```
'cbh (m) (Cloud base height)',
'd2m (K) (2 metre dewpoint temperature)',
't2m (K) (2 metre temperature)', 'hcc ((0 - 1)) (High cloud cover)',
'lcc ((0 - 1)) (Low cloud cover)', 'mcc ((0 - 1)) (Medium cloud cover)',
'tcc ((0 - 1)) (Total cloud cover)',
'tcw (kg m**-2) (Total column water)',
'tcwv (kg m**-2) (Total column vertically-integrated water vapour)',
'tp (m) (Total precipitation)',
'avg_ie (kg m**-2 s**-1) (Time-mean moisture flux)',
'avg_sdirswrf (W m**-2) (Time-mean surface direct short-wave radiation flux)',
'avg_sdirswrfcs (W m**-2) (Time-mean surface direct short-wave radiation flux, clear sky)',
'avg_sdlwrf (W m**-2) (Time-mean surface downward long-wave radiation flux)',
'avg_sdlwrfcs (W m**-2) (Time-mean surface downward long-wave radiation flux, clear sky)',
'avg_sdswrf (W m**-2) (Time-mean surface downward short-wave radiation flux)',
'avg_sdswrfcs (W m**-2) (Time-mean surface downward short-wave radiation flux, clear sky)',
'avg_sduvrf (W m**-2) (Time-mean surface downward UV radiation flux)',
'avg_slhtf (W m**-2) (Time-mean surface latent heat flux)',
'avg_snlwrf (W m**-2) (Time-mean surface net long-wave radiation flux)',
'avg_snlwrfcs (W m**-2) (Time-mean surface net long-wave radiation flux, clear sky)',
'avg_snswrf (W m**-2) (Time-mean surface net short-wave radiation flux)',
'avg_snswrfcs (W m**-2) (Time-mean surface net short-wave radiation flux, clear sky)',
'avg_ishf (W m**-2) (Time-mean surface sensible heat flux)',
'avg_tdswrf (W m**-2) (Time mean top downward short-wave radiation flux)',
'avg_tnlwrf (W m**-2) (Time-mean top net long-wave radiation flux)',
'avg_tnlwrfcs (W m**-2) (Time-mean top net long-wave radiation flux, clear sky)',
'avg_tnswrf (W m**-2) (Time-mean top net short-wave radiation flux)',
'avg_tnswrfcs (W m**-2) (Time-mean top net short-wave radiation flux, clear sky)',
'avg_tprate (kg m**-2 s**-1) (Time-mean total precipitation rate)',
'avg_vimdf (kg m**-2 s**-1) (Time-mean total column vertically-integrated moisture divergence flux)',
'tp_mm (mm) (Total precipitation)',
'avg_tprate_W (W m**-2) (Time-mean total precipitation rate)',
't2m (°C) (2 metre temperature)',
'd2m (°C) (2 metre dewpoint temperature)',
'balanc_earth (W m**-2) (earth_balance)',
'balanc_atmos (W m**-2) (atmospheric_balance)',
'balanc_surface (W m**-2) (surface_balance)'
```

## O que ainda está em desenvolvimento? 

Ainda está em fase de implementação os plots espaciais onde será possível ver a região delimitada pelo arquivo original e as regiões selecionadas pelo usuário para todas as variáveis, balanços e passos de tempo. Essa aplicação não está 100% boa, evite usar. Caso queira utilizar fazer mapas, utilize os dados recortados ou o dado bruto junto com a delimitação das caixas que estão no diretório /tables.

<img width="963" height="345" alt="image" src="https://github.com/user-attachments/assets/ed6b5b11-94bf-4896-a98f-04ea5883ff73" />
Exemplo do que está sendo produzido. Balanços atmosféricos, terrestre e superfície para cada passo de tmepo.

## Próximos passos: 

Desenvolver plots espaciais
Melhorias nas unidades de cada variável e escala dos gráficos
Criação de arquivos de log para outros processos de analises e plots.

## Dúvidas?? 
Entre em contato comigo pelos emails victor.ranieri@usp.br ou victor.ranieri90@gmail.com 


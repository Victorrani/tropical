# Metodologia

Este documento descreve os dados, a normal climatológica, as equações de balanço de energia
e as variáveis usadas no projeto. O passo a passo de uso dos scripts está no [README](../README.md).

## 1. Dados

### 1.1 Reanálise ERA5
São usadas as **médias mensais da reanálise ERA5** do ECMWF (Hersbach et al., 2020), conjunto
`reanalysis-era5-single-levels-monthly-means`, produto `monthly_averaged_reanalysis`, obtidas pelo
Copernicus Climate Data Store (CDS).

| Característica | Valor |
|---|---|
| Resolução horizontal | 0,25° × 0,25° (~28 km no equador) |
| Resolução temporal | médias mensais |
| Grade | regular em latitude/longitude, longitude entre −180° e 180° |
| Formato | netCDF, um arquivo por tipo de estatística do ERA5 (`stepType`: `avgad`, `avgid`, `avgua`) |

Nas médias mensais, as variáveis do tipo "taxa média" (prefixo `avg_`, em W m⁻² ou kg m⁻² s⁻¹)
representam a média do fluxo no mês. A precipitação acumulada (`tp`) é a **acumulação média diária**
do mês, em metros.

### 1.2 Dois conjuntos de dados
O mesmo conjunto de variáveis é baixado para dois períodos:

| Conjunto | Período | Área | Uso |
|---|---|---|---|
| **Normal** (`clima`) | 1991–2020 | retângulo que envolve os boxes (+1°) | cálculo da normal climatológica; os netCDF são apagados depois |
| **Análise** (`analise`) | escolhido pelo usuário | `AREA` do `get_data.py` ou a área dos boxes | séries, anomalias e mapas |

Como os dois conjuntos estão na **mesma grade do ERA5**, a média de um box é calculada exatamente
sobre os mesmos pontos nos dois períodos, independentemente da área baixada.

O CDS limita o tamanho de cada pedido (número de variáveis × meses). Por isso o período é baixado
em blocos de anos (`ANOS_POR_PEDIDO`) que depois são concatenados no tempo.

### 1.3 Máscara continente/oceano
A variável `land_sea_mask` (`lsm`) do ERA5 é a fração de continente em cada ponto de grade (0 a 1).
Por ser um campo fixo, é baixada uma única vez para o globo. Um ponto é classificado como:

$$\text{continente: } lsm \ge 0{,}5 \qquad \text{oceano (água): } lsm < 0{,}5$$

A máscara é usada (i) nas médias dos boxes com `superficie=terra` ou `superficie=oceano` e
(ii) nos mapas, para usar escalas de cor separadas para continente e oceano.

## 2. Domínios e médias espaciais

Cada domínio (box) é um retângulo em latitude/longitude definido no `namelist.txt`. A média
espacial de uma variável $X$ no box, para cada mês, é ponderada pela área de cada ponto de grade,
proporcional ao cosseno da latitude $\varphi$:

$$\langle X \rangle = \frac{\sum_i w_i\, m_i\, X_i}{\sum_i w_i\, m_i}, \qquad w_i = \cos\varphi_i$$

em que $m_i = 1$ para os pontos incluídos e $m_i = 0$ para os excluídos:
- `superficie=todos`: $m_i = 1$ em todos os pontos;
- `superficie=terra`: $m_i = 1$ só onde $lsm \ge 0{,}5$;
- `superficie=oceano`: $m_i = 1$ só onde $lsm < 0{,}5$.

Em boxes com litoral recomenda-se `superficie=terra`: sobre o oceano o balanço de superfície e os
fluxos turbulentos têm magnitudes muito diferentes das do continente e contaminam a média.

## 3. Normal climatológica e anomalias

### 3.1 Normal
Adota-se a **normal climatológica padrão da OMM, 1991–2020** (WMO, 2017). Para cada box e cada mês
do ano $m$, a normal é a média dos 30 valores mensais:

$$\overline{X}_m = \frac{1}{30}\sum_{a=1991}^{2020} \langle X \rangle_{a,m}, \qquad m = 1, \dots, 12$$

O resultado é um ciclo anual de 12 valores por variável
(`dataout/tables/EXP/EXP_nome_normal_91_20.csv`).

A normal só é comparável com dados do **mesmo domínio**. Por isso, as coordenadas e a opção
`superficie` do box ficam gravadas na primeira linha do arquivo da normal, e o cálculo das anomalias
é interrompido se o box do namelist for diferente do box da normal.

### 3.2 Anomalias
A anomalia de um mês $m$ do ano $a$ do período de análise é a diferença em relação à normal do
mesmo mês, o que remove o ciclo anual:

$$X'_{a,m} = \langle X \rangle_{a,m} - \overline{X}_m$$

Se a normal ainda não tiver sido gerada, o `desv.py` usa como referência o ciclo anual da própria
série analisada e avisa. Essa referência só é adequada para séries longas.

### 3.3 Ciclo anual por década
Para ver mudanças de longo prazo, o ciclo anual também é calculado por década, com as décadas
começando em anos terminados em 1 (1991–2000, 2001–2010, ...), como nas normais da OMM. Usa-se a
série da normal (1991–2020) junto com a série analisada, que estão no mesmo box e na mesma grade.
Uma década só é calculada se houver dados em pelo menos metade dos anos (`COBERTURA_MINIMA`), e
é identificada pelos anos efetivamente disponíveis (ex.: 2021–2025).

### 3.4 Média móvel
Nas figuras de séries e anomalias é mostrada a média móvel centrada de 12 meses, que filtra o ciclo
anual e destaca a variabilidade interanual (por exemplo, El Niño e La Niña):

$$\tilde{X}_t = \frac{1}{12}\sum_{k=-6}^{5} X_{t+k}$$

## 4. Equações de balanço de energia

### 4.1 Convenção de sinais
No ERA5, **todos os fluxos são positivos para baixo** (energia entrando no sistema abaixo do nível
considerado). Assim, o saldo de onda longa e os fluxos de calor sensível e latente são normalmente
negativos (energia saindo da superfície para a atmosfera). Os balanços são calculados nessa
convenção.

| Símbolo | Variável ERA5 | Significado |
|---|---|---|
| $S_{t}$ | `avg_tnswrf` | saldo de onda curta no topo da atmosfera |
| $L_{t}$ | `avg_tnlwrf` | saldo de onda longa no topo da atmosfera |
| $S_{s}$ | `avg_snswrf` | saldo de onda curta na superfície |
| $L_{s}$ | `avg_snlwrf` | saldo de onda longa na superfície |
| $H$ | `avg_ishf` | fluxo de calor sensível na superfície |
| $LE$ | `avg_slhtf` | fluxo de calor latente na superfície |
| $P$ | `avg_tprate` | taxa de precipitação (kg m⁻² s⁻¹) |
| $L_v$ | — | calor latente de vaporização, $2{,}5\times10^{6}$ J kg⁻¹ |

Os saldos radiativos no topo e na superfície são:

$$R_{t} = S_{t} + L_{t} \qquad R_{s} = S_{s} + L_{s}$$

### 4.2 Balanço da Terra (topo da atmosfera)
$$B_{\text{Terra}} = R_{t} = S_{t} + L_{t}$$

Positivo quando a coluna (atmosfera + superfície) ganha energia por radiação. Nos trópicos é
tipicamente positivo; o excedente é exportado para latitudes mais altas pela circulação.

### 4.3 Balanço da superfície
$$B_{\text{sup}} = R_{s} + H + LE$$

Com $H$ e $LE$ negativos (perda para a atmosfera), é o saldo de energia disponível para
aquecer o solo ou o oceano. Em médias mensais sobre o **continente**, $B_{\text{sup}} \approx 0$,
pois o solo armazena pouco calor. Sobre o **oceano**, $|B_{\text{sup}}|$ chega a centenas de W m⁻²,
porque o oceano armazena calor e o transporta pelas correntes. Por isso os mapas usam escalas
separadas para continente e oceano.

### 4.4 Balanço da atmosfera
$$B_{\text{atm}} = \underbrace{(R_{t} - R_{s})}_{\text{convergência radiativa}} \; \underbrace{-\,H}_{\text{calor sensível recebido}} \; + \underbrace{L_v P}_{\text{calor latente liberado}}$$

- $R_t - R_s$: saldo radiativo da coluna atmosférica (normalmente negativo: a atmosfera perde
  energia por radiação);
- $-H$: calor sensível transferido da superfície para a atmosfera;
- $L_v P$: calor latente liberado na condensação que produz a precipitação.

### 4.5 Relação entre os balanços
Somando os balanços da atmosfera e da superfície, e escrevendo $LE = -L_v E$ (evaporação $E$):

$$B_{\text{atm}} + B_{\text{sup}} = R_t + L_v\,(P - E) \quad\Longrightarrow\quad B_{\text{Terra}} = B_{\text{atm}} + B_{\text{sup}} - L_v\,(P - E)$$

O termo $L_v(P-E)$ é o calor latente importado pela convergência de umidade: onde chove mais do
que evapora, a atmosfera recebe energia latente de outras regiões. Em média, $P - E$ é equilibrado
pela convergência do fluxo de umidade integrado na coluna (`avg_vimdf` com sinal trocado). Um
$B_{\text{atm}}$ diferente de zero indica exportação (ou importação) de energia pela circulação
atmosférica. Na reanálise, os balanços não fecham exatamente, porque a assimilação de dados
introduz pequenos incrementos de energia.

## 5. Variáveis

### 5.1 Variáveis baixadas
| Nome no CDS | Abreviação | Unidade no ERA5 | Unidade nas tabelas |
|---|---|---|---|
| `2m_temperature` | `t2m` | K | K e °C |
| `2m_dewpoint_temperature` | `d2m` | K | K e °C |
| `total_cloud_cover` | `tcc` | 0–1 | 0–1 |
| `high_cloud_cover` | `hcc` | 0–1 | 0–1 |
| `medium_cloud_cover` | `mcc` | 0–1 | 0–1 |
| `low_cloud_cover` | `lcc` | 0–1 | 0–1 |
| `cloud_base_height` | `cbh` | m | m |
| `total_column_water` | `tcw` | kg m⁻² | kg m⁻² |
| `total_column_water_vapour` | `tcwv` | kg m⁻² | kg m⁻² |
| `total_precipitation` | `tp` | m (por dia) | mm dia⁻¹ |
| `mean_total_precipitation_rate` | `avg_tprate` | kg m⁻² s⁻¹ | kg m⁻² dia⁻¹ |
| `mean_evaporation_rate` | `avg_ie` | kg m⁻² s⁻¹ | kg m⁻² dia⁻¹ |
| `mean_vertically_integrated_moisture_divergence` | `avg_vimdf` | kg m⁻² s⁻¹ | kg m⁻² dia⁻¹ |
| `mean_surface_latent_heat_flux` | `avg_slhtf` | W m⁻² | W m⁻² ⁽*⁾ |
| `mean_surface_sensible_heat_flux` | `avg_ishf` | W m⁻² | W m⁻² ⁽*⁾ |
| `mean_surface_net_short_wave_radiation_flux` | `avg_snswrf` | W m⁻² | W m⁻² ⁽*⁾ |
| `mean_surface_net_long_wave_radiation_flux` | `avg_snlwrf` | W m⁻² | W m⁻² ⁽*⁾ |
| `mean_surface_downward_short_wave_radiation_flux` | `avg_sdswrf` | W m⁻² | W m⁻² |
| `mean_surface_downward_long_wave_radiation_flux` | `avg_sdlwrf` | W m⁻² | W m⁻² |
| `mean_surface_direct_short_wave_radiation_flux` | `avg_sdirswrf` | W m⁻² | W m⁻² |
| `mean_surface_downward_uv_radiation_flux` | `avg_sduvrf` | W m⁻² | W m⁻² |
| `mean_top_net_short_wave_radiation_flux` | `avg_tnswrf` | W m⁻² | W m⁻² ⁽*⁾ |
| `mean_top_net_long_wave_radiation_flux` | `avg_tnlwrf` | W m⁻² | W m⁻² ⁽*⁾ |
| `mean_top_downward_short_wave_radiation_flux` | `avg_tdswrf` | W m⁻² | W m⁻² |
| `land_sea_mask` (baixada à parte) | `lsm` | 0–1 | — |

As variáveis de céu claro (*clear sky*) não são baixadas.

⁽*⁾ **Sinal invertido nas tabelas e figuras** (positivo para cima), para facilitar a leitura:
calor latente, calor sensível e saldo de onda longa aparecem positivos quando a superfície perde
energia. Os balanços da seção 4 são calculados **antes** dessa inversão, na convenção do ERA5.

### 5.2 Variáveis derivadas
| Coluna | Cálculo | Unidade |
|---|---|---|
| `t2m`, `d2m` em °C | $T - 273{,}15$ | °C |
| `tp` | $tp \times 1000$ | mm dia⁻¹ |
| `tp_mm` | $tp \times 1000 \times n_{\text{dias do mês}}$ | mm (total mensal) |
| `avg_tprate_W` | $L_v\,P$, com $P$ em kg m⁻² s⁻¹ | W m⁻² |
| taxas em kg m⁻² dia⁻¹ | taxa em kg m⁻² s⁻¹ $\times 86400$ | kg m⁻² dia⁻¹ (= mm dia⁻¹) |
| `balanc_earth` | $B_{\text{Terra}}$ (seção 4.2) | W m⁻² |
| `balanc_surface` | $B_{\text{sup}}$ (seção 4.3) | W m⁻² |
| `balanc_atmos` | $B_{\text{atm}}$ (seção 4.4) | W m⁻² |

Para água líquida, 1 kg m⁻² equivale a uma lâmina de 1 mm, então as taxas em kg m⁻² dia⁻¹ podem ser
lidas diretamente em mm dia⁻¹.

## 6. Limitações
- O ERA5 é uma reanálise: combina modelo e observações, e seus fluxos de superfície e de radiação
  dependem das parametrizações do modelo, principalmente em regiões com poucas observações.
- Os balanços não fecham exatamente por causa dos incrementos da assimilação de dados.
- $L_v$ é considerado constante ($2{,}5\times10^6$ J kg⁻¹), sem dependência com a temperatura e sem
  o calor latente de fusão.
- A resolução de 0,25° não resolve bem litorais estreitos, lagos e rios. Pontos de grande rio ou
  estuário podem aparecer como "água" na máscara.
- Os meses mais recentes do ERA5 vêm da versão preliminar (ERA5T), que pode ser revisada.

## Referências
- Hersbach, H., et al. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal
  Meteorological Society*, 146(730), 1999–2049. https://doi.org/10.1002/qj.3803
- WMO (2017). *WMO Guidelines on the Calculation of Climate Normals* (WMO-No. 1203). World
  Meteorological Organization, Genebra.

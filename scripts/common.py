"""
Configurações e funções compartilhadas por todos os scripts do projeto.

Os scripts em analysis/, download/ e plots/ importam este módulo com:

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import common as cm
"""
import os
import re
from pathlib import Path

import pandas as pd

# ============================================================
# Diretórios
# ============================================================
# A raiz pode ser sobrescrita pela variável de ambiente TROPICAL_ROOT
# (útil para testar o pipeline em uma cópia do projeto).
DIR_ROOT = Path(os.environ.get("TROPICAL_ROOT", Path(__file__).resolve().parent.parent))

DIR_RAW = DIR_ROOT / "datain" / "raw"
DIR_PROCESSED = DIR_ROOT / "datain" / "processed"
DIR_DATAOUT = DIR_ROOT / "dataout"
DIR_TABLES = DIR_DATAOUT / "tables"
DIR_LOGS = DIR_ROOT / "logs"
SHAPE_BR = DIR_ROOT / "shapefiles" / "BR_UF_2019.shp"

NAMELIST = DIR_ROOT / "scripts" / "analysis" / "namelist.txt"
# Máscara continente/oceano do ERA5 (global, baixada uma vez: get_data.py mascara)
MASCARA_LSM = DIR_ROOT / "datain" / "mascara" / "land_sea_mask.nc"
BOXES_CSV = DIR_TABLES / "boxes.csv"

# ============================================================
# Constantes físicas e períodos da climatologia
# ============================================================
L_V = 2.5e6  # calor latente de vaporização (J kg-1)

DPI = 250  # resolução das figuras salvas

# Normal climatológica (OMM) usada como referência para as anomalias
NORMAL = (1991, 2020)
NORMAL_ROTULO = f"Normal {NORMAL[0]}–{NORMAL[1]}"

# Ciclos anuais por década (1991–2000, 2001–2010, ...), como nas normais da OMM.
# Uma década só é calculada se houver dados em pelo menos COBERTURA_MINIMA dos anos.
COBERTURA_MINIMA = 0.5


def decadas(anos):
    """Décadas (ano inicial, ano final) que contêm os anos dados, começando em anos terminados em 1."""
    anos = sorted(set(int(a) for a in anos))
    if not anos:
        return []
    ini = (anos[0] - 1) // 10 * 10 + 1
    return [(d, d + 9) for d in range(ini, anos[-1] + 1, 10)]

# ============================================================
# Modos: 'analise' (período de estudo) e 'clima' (período da normal)
# Os dados da normal ficam em subpastas próprias e são apagados
# depois que a tabela da normal é gerada (ver scripts/analysis/normal.py).
# ============================================================
MODOS = ("analise", "clima")


def _checa_modo(modo):
    if modo not in MODOS:
        raise ValueError(f"modo deve ser um de {MODOS}, não '{modo}'")


def dir_raw(modo="analise"):
    _checa_modo(modo)
    return DIR_RAW if modo == "analise" else DIR_RAW / "clima"


def dir_processed(modo="analise"):
    _checa_modo(modo)
    return DIR_PROCESSED if modo == "analise" else DIR_PROCESSED / "clima"

# ============================================================
# Arquivos de saída
# ============================================================
def dir_tabelas(exp_name):
    return DIR_TABLES / exp_name


def arq_serie(exp_name, name, modo="analise"):
    _checa_modo(modo)
    prefixo = "time_series" if modo == "analise" else "time_series_normal"
    return dir_tabelas(exp_name) / f"{prefixo}_{exp_name}_{name}.csv"


def arq_normal(exp_name, name):
    return dir_tabelas(exp_name) / f"{exp_name}_{name}_normal_{str(NORMAL[0])[2:]}_{str(NORMAL[1])[2:]}.csv"


def arq_clima(exp_name, name, periodo=None):
    """Ciclo anual da série analisada (periodo=None) ou de um período, ex. periodo='1991_2000'."""
    sufixo = f"_{periodo}" if periodo else ""
    return dir_tabelas(exp_name) / f"{exp_name}_{name}_clima{sufixo}.csv"


def arqs_clima_decadas(exp_name, name):
    """Tabelas das décadas já calculadas, em ordem: [(ano_ini, ano_fim, caminho), ...]."""
    saida = []
    for p in dir_tabelas(exp_name).glob(f"{exp_name}_{name}_clima_*_*.csv"):
        partes = p.stem.split("_")[-2:]
        if all(x.isdigit() and len(x) == 4 for x in partes):
            saida.append((int(partes[0]), int(partes[1]), p))
    return sorted(saida)


def arq_anomalias(exp_name, name):
    return dir_tabelas(exp_name) / f"anomalias_{exp_name}_{name}.csv"


def dir_figuras(exp_name, name, *sub):
    outdir = DIR_DATAOUT.joinpath(exp_name, name, *sub)
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir

# ============================================================
# Namelist / boxes
# ============================================================
CAMPOS_NUMERICOS = ("lat_max", "lat_min", "lon_max", "lon_min")

# superficie: quais pontos entram na média do box
#   todos  -> todos os pontos (padrão)
#   terra  -> só continente (land_sea_mask >= 0.5)
#   oceano -> só oceano     (land_sea_mask <  0.5)
SUPERFICIES = ("todos", "terra", "oceano")


def ler_namelist(path=NAMELIST):
    """Lê o namelist.txt e devolve um DataFrame com uma linha por box.

    Linhas vazias ou iniciadas por '#' são ignoradas.
    """
    boxes = []
    with open(path, "r") as f:
        for n, linha in enumerate(f, start=1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            try:
                d = dict(item.split("=", 1) for item in linha.split(";") if item)
                d = {k.strip(): v.strip() for k, v in d.items()}
                for k in CAMPOS_NUMERICOS:
                    d[k] = float(d[k])
            except (ValueError, KeyError) as e:
                raise ValueError(f"{path}:{n}: linha inválida no namelist ({e}): {linha}")

            if d["lat_min"] >= d["lat_max"] or d["lon_min"] >= d["lon_max"]:
                raise ValueError(f"{path}:{n}: lat_min/lon_min devem ser menores que lat_max/lon_max")
            d.setdefault("superficie", "todos")
            if d["superficie"] not in SUPERFICIES:
                raise ValueError(f"{path}:{n}: superficie deve ser um de {SUPERFICIES}")
            boxes.append(d)

    if not boxes:
        raise ValueError(f"Nenhum box definido em {path}")
    df = pd.DataFrame(boxes, columns=["exp_name", "name", *CAMPOS_NUMERICOS, "superficie"])
    duplicados = df[df.duplicated(["exp_name", "name"])]
    if not duplicados.empty:
        raise ValueError(f"Boxes repetidos no namelist: {duplicados[['exp_name', 'name']].values.tolist()}")
    return df


def superficie_de(row):
    s = row.get("superficie", "todos")
    return s if isinstance(s, str) else "todos"  # boxes.csv antigo: coluna ausente/NaN


def box_de(row):
    """Coordenadas e superfície de um box (linha do boxes.csv)."""
    box = {k: float(row[k]) for k in CAMPOS_NUMERICOS}
    box["superficie"] = superficie_de(row)
    return box


def salvar_com_box(df, path, box, **to_csv_kw):
    """Salva um CSV com as coordenadas do box numa linha de comentário no topo."""
    with open(path, "w") as f:
        f.write("# box " + " ".join(f"{k}={v}" for k, v in box.items()) + "\n")
        df.to_csv(f, **to_csv_kw)


def ler_box_do_csv(path):
    """Lê as coordenadas gravadas por salvar_com_box (None se não houver)."""
    with open(path) as f:
        primeira = f.readline().strip()
    if not primeira.startswith("# box "):
        return None
    box = dict(item.split("=") for item in primeira[6:].split())
    for k in CAMPOS_NUMERICOS:
        box[k] = float(box[k])
    box.setdefault("superficie", "todos")
    return box


def ler_csv_com_box(path, **read_csv_kw):
    """Lê um CSV salvo por salvar_com_box. Devolve (DataFrame, box ou None)."""
    box = ler_box_do_csv(path)
    return pd.read_csv(path, skiprows=1 if box else 0, **read_csv_kw), box


def mesmo_box(a, b, tol=1e-6):
    return (a is not None and b is not None
            and all(abs(a[k] - b[k]) < tol for k in CAMPOS_NUMERICOS)
            and a.get("superficie", "todos") == b.get("superficie", "todos"))


def ler_normal(row):
    """Normal do box (index 'mes') ou None se não existir ou for de outro domínio."""
    path = arq_normal(row["exp_name"], row["name"])
    if not path.exists():
        return None
    df, box = ler_csv_com_box(path, index_col="mes")
    if not mesmo_box(box, box_de(row)):
        print(f"Atenção: {path.name} é de outro domínio; ignorada")
        return None
    return df


def ler_boxes():
    """Lê a tabela de boxes gerada pelo slice.py."""
    if not BOXES_CSV.exists():
        raise FileNotFoundError(f"{BOXES_CSV} não encontrado. Rode antes: python scripts/analysis/slice.py")
    return pd.read_csv(BOXES_CSV)

# ============================================================
# Colunas no formato "abrev (unidade) (nome completo)"
# ============================================================
_RE_COLUNA = re.compile(r"^(\S+) \((.*)\) \((.*?)\)$")


def nome_coluna(abrev, unidade, nome):
    return f"{abrev} ({unidade}) ({nome})"


def separar_nome_coluna(col):
    """'hcc ((0 - 1)) (High cloud cover)' -> ('hcc', '(0 - 1)', 'High cloud cover')."""
    m = _RE_COLUNA.match(col)
    if m:
        return m.groups()
    return col, "", col


SEGUNDOS_POR_DIA = 86400


def por_segundo_para_dia(df):
    """Converte as colunas com unidade 's**-1' para 'day**-1' (x 86400), mantendo a ordem.
    Ex.: kg m**-2 s**-1 -> kg m**-2 day**-1 (= mm/dia). Não altera colunas já convertidas."""
    df = df.copy()
    novos = {}
    for c in df.columns:
        abrev, unidade, nome = separar_nome_coluna(c)
        if "s**-1" in unidade:
            df[c] = df[c] * SEGUNDOS_POR_DIA
            novos[c] = nome_coluna(abrev, unidade.replace("s**-1", "day**-1"), nome)
    return df.rename(columns=novos)


def converter_unidades(df):
    """Unidades usadas nas tabelas:
    - fluxos por segundo -> por dia (x 86400)
    - tp: m (acumulação média diária do ERA5 mensal) -> mm day**-1 (x 1000)
    Não altera colunas já convertidas."""
    df = por_segundo_para_dia(df)
    novos = {}
    for c in df.columns:
        abrev, unidade, nome = separar_nome_coluna(c)
        if abrev == "tp" and unidade == "m":
            df[c] = df[c] * 1000
            novos[c] = nome_coluna(abrev, "mm day**-1", nome)
    return df.rename(columns=novos)


def colunas_por_abrev(df):
    """Mapeia o nome abreviado de cada variável para o nome completo da coluna."""
    return {separar_nome_coluna(c)[0]: c for c in df.columns}

# ============================================================
# Balanços de energia
# ============================================================
def calcula_balancos(tnswrf, tnlwrf, snswrf, snlwrf, ishf, slhtf, tprate):
    """Balanços de energia a partir das variáveis ERA5 na convenção ORIGINAL
    (fluxos positivos para baixo). Funciona com pandas ou xarray.

    earth   = saldo radiativo no topo (TOA)
    surface = saldo radiativo na superfície + calor sensível + calor latente
    atmos   = convergência radiativa na coluna + calor sensível recebido da
              superfície + calor latente liberado pela precipitação (L*P)
    """
    rad_toa = tnswrf + tnlwrf
    rad_srf = snswrf + snlwrf
    return {
        "earth": rad_toa,
        "surface": rad_srf + ishf + slhtf,
        "atmos": (rad_toa - rad_srf) - ishf + L_V * tprate,
    }

# ============================================================
# netCDF e mapas
# ============================================================
def abrir_netcdfs(files, variaveis=None):
    """Abre e junta vários netCDF do ERA5 em um único Dataset com dimensão 'time'.

    Se `variaveis` for dada, mantém só essas (as ausentes são ignoradas).
    """
    import xarray as xr

    partes = []
    for f in files:
        ds = xr.open_dataset(f)
        if "valid_time" in ds.dims:
            ds = ds.rename({"valid_time": "time"})
        # coordenadas auxiliares (number, expver) variam entre arquivos e impedem o merge
        ds = ds.drop_vars([c for c in ds.coords if c not in ds.dims])
        if variaveis is not None:
            ds = ds[[v for v in variaveis if v in ds.data_vars]]
        if ds.data_vars:
            partes.append(ds)
    if not partes:
        raise FileNotFoundError(f"Nenhuma variável encontrada em {[str(f) for f in files]}")
    ds = xr.merge(partes, compat="override", join="outer")
    faltando = set(variaveis or []) - set(ds.data_vars)
    if faltando:
        raise KeyError(f"Variáveis ausentes nos arquivos: {sorted(faltando)}")
    return ds


def ler_mascara():
    """land_sea_mask do ERA5 (fração de continente, 0..1) ou None se não baixada."""
    if not MASCARA_LSM.exists():
        return None
    import xarray as xr
    with xr.open_dataset(MASCARA_LSM) as ds:
        lsm = ds["lsm"].load()
    return lsm.squeeze(drop=True)  # remove dimensão de tempo de tamanho 1


def mascara_superficie(lsm, superficie, latitude, longitude):
    """1 nos pontos da superfície pedida e 0 nos demais, na grade (latitude, longitude)."""
    if superficie == "todos":
        return None
    lsm = lsm.sel(latitude=latitude, longitude=longitude, method="nearest")
    lsm = lsm.assign_coords(latitude=latitude, longitude=longitude)
    terra = lsm >= 0.5
    return (terra if superficie == "terra" else ~terra).astype(float)


# Cores do oceano nos mapas com máscara. O continente usa azul-vermelho (RdBu_r);
# o oceano usa teal (frio) e laranja (quente): distinguíveis entre si e do azul
# do continente para daltonismo vermelho-verde (evita verde x vermelho e azul x roxo).
_TEAL = ["#003c30", "#01665e", "#35978f", "#80cdc1", "#d8f0ec"]
_LARANJA = ["#fde0b6", "#fdb863", "#e08214", "#b35806", "#7f3b08"]


def cmap_oceano_divergente():
    """Teal (negativo) -> branco -> laranja (positivo)."""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("teal_laranja", _TEAL + ["#f7f7f7"] + _LARANJA)


def cmap_oceano_sequencial():
    """Teal escuro (valores mais baixos) -> claro."""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("teal", _TEAL)


def contourf_terra_oceano(fig, ax, campo, lsm, terra, oceano, unidade):
    """Plota `campo` com escalas de cor separadas para continente e oceano.

    terra/oceano: dicts com 'levels' e 'cmap'. Cada parte ganha sua barra de cor:
    continente embaixo (como nos outros painéis) e oceano na vertical, à direita.
    """
    import cartopy.crs as ccrs

    eh_terra = mascara_superficie(lsm, "terra", campo["latitude"], campo["longitude"]) == 1
    partes = ((campo.where(eh_terra), terra, "Continente", dict(orientation="horizontal", shrink=0.8, pad=0.05)),
              (campo.where(~eh_terra), oceano, "Oceano", dict(orientation="vertical", shrink=0.8, pad=0.03)))
    for parte, cfg, rotulo, barra in partes:
        if int(parte.notnull().sum()) == 0:
            continue
        im = ax.contourf(parte['longitude'], parte['latitude'], parte, transform=ccrs.PlateCarree(),
                         levels=cfg["levels"], cmap=cfg["cmap"], extend="both")
        cbar = fig.colorbar(im, ax=ax, **barra)
        cbar.set_label(f"{rotulo} ({unidade})")


def decorar_mapa(ax, geometrias, passo_grade=2.5):
    """Linhas de costa, estados, fronteiras, rios e grade em um eixo cartopy."""
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np

    ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=0)
    ax.coastlines()
    ax.add_geometries(geometrias, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=0.3)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax.add_feature(cfeature.RIVERS, edgecolor='blue', linewidth=0.7)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), color='black', alpha=1.0, linestyle='--', linewidth=0.4,
                      xlocs=np.arange(-180, 181, passo_grade), ylocs=np.arange(-90, 91, passo_grade),
                      draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False


def ler_geometrias(shape=SHAPE_BR, tolerancia=0.01):
    """Contornos do shapefile, simplificados (tolerância em graus, ~1 km).
    O shapefile original tem ~900 mil vértices, detalhe invisível nos mapas,
    e desenhá-lo era a parte mais lenta de cada figura."""
    from cartopy.io import shapereader as shpreader
    return [g.simplify(tolerancia, preserve_topology=True) for g in shpreader.Reader(shape).geometries()]

# ============================================================
# Limites do eixo y dos gráficos
# Por padrão os limites são automáticos (a partir dos dados, iguais
# para todos os boxes). Para fixar um limite, adicione a coluna aqui:
#     'tp_mm (mm) (Total precipitation)': [0, 600],
# Obs.: nas tabelas, slhtf, snlwrf, snswrf, ishf, tnlwrf e tnswrf
# estão com o sinal invertido (positivo para cima) — ver time_serie_vars.py
# ============================================================
LIMITES_SERIE = {}
LIMITES_ANOMALIA = {}


def limites_auto(valores, simetrico=False, margem=0.1):
    """Limites [min, max] cobrindo todos os valores, com `margem` (fração) de folga.
    simetrico=True centra em zero (para anomalias)."""
    import numpy as np

    v = np.concatenate([np.asarray(x, dtype=float).ravel() for x in valores])
    v = v[np.isfinite(v)]
    if v.size == 0:
        return None
    if simetrico:
        m = np.abs(v).max() * (1 + margem) or 1.0
        return [-m, m]
    lo, hi = v.min(), v.max()
    folga = (hi - lo) * margem or abs(hi) * margem or 1.0
    return [lo - folga, hi + folga]


def limites(var, valores, fixos, simetrico=False):
    """Limite fixo do dicionário, se houver; senão, automático."""
    return fixos.get(var) or limites_auto(valores, simetrico)

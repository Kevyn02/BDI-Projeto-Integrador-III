import numpy as np
import pandas as pd
from pathlib import Path

# ============================================================
# Configurações
# ============================================================
np.random.seed(42)

N_LINHAS = 250
PASTA_DADOS_BRUTO = Path("dados/bruto")
ARQUIVO_SAIDA = Path("dados/bruto").resolve() / "dados_industriais_brutos.csv"

Path(PASTA_DADOS_BRUTO).mkdir(parents=True, exist_ok=True)

# ============================================================
# Geração dos dados-base
# ============================================================
fim = pd.Timestamp.now().floor("s")
inicio = fim - pd.Timedelta(days=30)

timestamps = pd.date_range(
    start=inicio,
    end=fim,
    periods=N_LINHAS
)

maquinas = np.random.choice(
    ["M_01", "M_02", "M_03", "M_04"],
    size=N_LINHAS,
    p=[0.25, 0.25, 0.25, 0.25]
)

temperaturas = np.random.normal(
    loc=72,
    scale=8,
    size=N_LINHAS
)

vibracoes = np.random.normal(
    loc=3.2,
    scale=0.8,
    size=N_LINHAS
)

pecas_produzidas = np.random.poisson(
    lam=18,
    size=N_LINHAS
).astype(int)

pecas_refugadas = np.random.poisson(
    lam=1.5,
    size=N_LINHAS
).astype(int)

status = np.random.choice(
    ["OPERANDO", "PARADA", "EM MANUTENÇÃO", "SETUP"],
    size=N_LINHAS,
    p=[0.72, 0.10, 0.10, 0.08]
)

# ============================================================
# Criação do DataFrame
# ============================================================
df = pd.DataFrame({
    "Timestamp Registro": timestamps,
    "ID Maquina": maquinas,
    "Temp (°C)": temperaturas,
    "Vibração mm/s": vibracoes,
    "Pecas Produzidas": pecas_produzidas,
    "Pecas Refugadas": pecas_refugadas,
    "Status Operacao": status
})

# ============================================================
# Defeito 1 e 2: datas como texto em formatos mistos
# ============================================================
df["Timestamp Registro"] = df["Timestamp Registro"].dt.strftime(
    "%Y-%m-%d %H:%M:%S"
)

indices_data_mista = np.random.choice(
    df.index,
    size=int(len(df) * 0.30),
    replace=False
)

datas = pd.to_datetime(
    df.loc[indices_data_mista, "Timestamp Registro"],
    errors="coerce"
)

df.loc[indices_data_mista, "Timestamp Registro"] = datas.dt.strftime(
    "%d/%m/%Y %H:%M"
)

# ============================================================
# Defeito 3: duplicatas de chave de negócio
# Aproximadamente 4% de linhas duplicadas
# ============================================================
quantidade_duplicatas = int(len(df) * 0.04)

indices_duplicados = np.random.choice(
    df.index,
    size=quantidade_duplicatas,
    replace=False
)

duplicatas = df.loc[indices_duplicados].copy()

# Para garantir que a combinação máquina + timestamp seja
# efetivamente duplicada, as linhas são copiadas integralmente.
df = pd.concat(
    [df, duplicatas],
    ignore_index=True
)

# ============================================================
# Defeito 4: valores ausentes
# ============================================================
rng = np.random.default_rng(42)

for coluna, percentual in [
    ("Temp (°C)", 0.035),
    ("Vibração mm/s", 0.035),
    ("Pecas Refugadas", 0.04)
]:
    quantidade_nulos = max(1, int(len(df) * percentual))

    indices_nulos = rng.choice(
        df.index,
        size=quantidade_nulos,
        replace=False
    )

    df.loc[indices_nulos, coluna] = np.nan

# ============================================================
# Defeito 5: inconsistências categóricas em máquinas
# ============================================================
mapa_maquinas_inconsistentes = {
    "M_01": ["M_01", " M_01 ", "m_01", "M-01"],
    "M_02": ["M_02", " M_02 ", "m_02", "M-02"],
    "M_03": ["M_03", " M_03 ", "m_03", "M-03"],
    "M_04": ["M_04", " M_04 ", "m_04", "M-04"]
}

for idx in df.index:
    maquina = df.at[idx, "ID Maquina"]

    if maquina in mapa_maquinas_inconsistentes and rng.random() < 0.15:
        df.at[idx, "ID Maquina"] = rng.choice(
            mapa_maquinas_inconsistentes[maquina]
        )

# Inconsistências categóricas no status
mapa_status_inconsistente = {
    "OPERANDO": [
        "OPERANDO",
        " operando",
        "OPERANDO ",
        "operando",
        " Operando "
    ],
    "PARADA": [
        "PARADA",
        " parada",
        "PARADA ",
        "parada",
        " Parada "
    ],
    "EM MANUTENÇÃO": [
        "EM MANUTENÇÃO",
        " em manutenção",
        "EM MANUTENÇÃO ",
        "em manutenção",
        " EM MANUTENÇÃO "
    ],
    "SETUP": [
        "SETUP",
        " setup",
        "SETUP ",
        "setup",
        " Setup "
    ]
}

for idx in df.index:
    status_atual = df.at[idx, "Status Operacao"]

    if status_atual in mapa_status_inconsistente and rng.random() < 0.20:
        df.at[idx, "Status Operacao"] = rng.choice(
            mapa_status_inconsistente[status_atual]
        )

# ============================================================
# Defeito 6: outliers e limites físicos impossíveis
# ============================================================

# Temperaturas negativas impossíveis
indices_temp_negativa = rng.choice(
    df.index,
    size=12,
    replace=False
)

df.loc[indices_temp_negativa, "Temp (°C)"] = rng.choice(
    [-50, -40, -25, -10],
    size=len(indices_temp_negativa)
)

# Picos extremos de temperatura
indices_temp_extrema = rng.choice(
    df.index.difference(indices_temp_negativa),
    size=10,
    replace=False
)

df.loc[indices_temp_extrema, "Temp (°C)"] = rng.choice(
    [300, 350, 400, 450],
    size=len(indices_temp_extrema)
)

# Outliers de vibração
indices_vibracao_extrema = rng.choice(
    df.index,
    size=12,
    replace=False
)

df.loc[indices_vibracao_extrema, "Vibração mm/s"] = rng.choice(
    [15, 20, 30, 50],
    size=len(indices_vibracao_extrema)
)

# Peças refugadas maiores que peças produzidas
indices_refugo_maior = rng.choice(
    df.index,
    size=15,
    replace=False
)

for idx in indices_refugo_maior:
    produzidas = df.at[idx, "Pecas Produzidas"]

    if pd.notna(produzidas):
        df.at[idx, "Pecas Refugadas"] = int(produzidas) + rng.integers(1, 15)

# Ciclos com produção zero e refugo positivo
indices_producao_zero = rng.choice(
    df.index,
    size=15,
    replace=False
)

df.loc[indices_producao_zero, "Pecas Produzidas"] = 0
df.loc[indices_producao_zero, "Pecas Refugadas"] = rng.integers(
    1,
    8,
    size=len(indices_producao_zero)
)

# Alguns valores inteiros extremos adicionais
indices_producao_alta = rng.choice(
    df.index,
    size=8,
    replace=False
)

df.loc[indices_producao_alta, "Pecas Produzidas"] = rng.integers(
    80,
    150,
    size=len(indices_producao_alta)
)

# ============================================================
# Pequena desordenação para tornar o dataset mais realista
# ============================================================
df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

# ============================================================
# Garantir que tipos numéricos mantenham aparência bruta
# ============================================================
df["Temp (°C)"] = pd.to_numeric(
    df["Temp (°C)"],
    errors="coerce"
).round(2)

df["Vibração mm/s"] = pd.to_numeric(
    df["Vibração mm/s"],
    errors="coerce"
).round(3)

df["Pecas Produzidas"] = pd.to_numeric(
    df["Pecas Produzidas"],
    errors="coerce"
).astype("Int64")

df["Pecas Refugadas"] = pd.to_numeric(
    df["Pecas Refugadas"],
    errors="coerce"
).astype("Int64")

# ============================================================
# Exportação para CSV
# ============================================================
df.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)

print(f"Dataset gerado com sucesso: {ARQUIVO_SAIDA}")
print(f"Linhas: {len(df)}")
print(f"Colunas: {len(df.columns)}")
print("\nColunas:")
print(df.columns.tolist())

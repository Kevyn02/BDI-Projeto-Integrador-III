# Gerador Dados Industriais Bruto com IA

Crie um script em Python utilizando a biblioteca `pandas` e `numpy` para gerar um conjunto de dados brutos industriais em formato CSV (`dados_industriais_brutos.csv`) para um projeto prático de engenharia de dados.

## Requisitos Estruturais do Dataset

1. **Volume mínimo:** 1.200 linhas e 7 colunas.
2. **Colunas obrigatórias:**
   - `timestamp` (Temporal): datas/horas cobrindo os últimos 30 dias.
   - `id_maquina` (Categórica): identificadores de máquinas (ex: M_01, M_02, M_03, M_04).
   - `temperatura_c` (Numérica contínua): leituras de temperatura de sensores.
   - `vibracao_mm_s` (Numérica contínua): leituras de vibração.
   - `pecas_produzidas` (Numérica inteira): quantidade produzida por ciclo.
   - `pecas_refugadas` (Numérica inteira): quantidade de peças com defeito.
   - `status_operacao` (Categórica): status do equipamento.

## Defeitos de Qualidade a Inserir Deliberadamente (para podermos limpar depois)

1. **Nomes de colunas inconsistentes:** Use nomes com maiúsculas, espaços e acentos (ex: `Timestamp Registro`, `ID Maquina`, `Temp (°C)`, `Vibração mm/s`, `Pecas Produzidas`, `Pecas Refugadas`, `Status Operacao`).
2. **Datas/Horas como texto:** Formate algumas datas em strings com padrões mistos (ex: `YYYY-MM-DD HH:MM:SS` e `DD/MM/YYYY HH:MM`).
3. **Duplicatas de Chave de Negócio:** Introduza cerca de 3% a 5% de linhas duplicadas considerando a combinação de `id_maquina` + `timestamp`.
4. **Valores Ausentes (NaN/Nulos):** Insira valores nulos em `temperatura_c`, `vibracao_mm_s` e `pecas_refugadas`.
5. **Inconsistências Categóricas:** Alterne valores na coluna de status e máquina com espaços extras e caixas diferentes (ex: `" M_01 "`, `"m_01"`, `"M-01"`, `" OPERANDO "`, `"operando"`, `"EM MANUTENÇÃO"`).
6. **Outliers e Limites Físicos Impossíveis:**
   - Temperaturas negativas impossíveis (ex: `-50 °C`) e picos anômalos extremos (ex: `450 °C`).
   - Peças refugadas maiores do que as peças produzidas.
   - Ciclos com `pecas_produzidas = 0` mas com refugo positivo.

Forneça APENAS o código Python completo e executável para gerar e salvar esse arquivo `.csv`.

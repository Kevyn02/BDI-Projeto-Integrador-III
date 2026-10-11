# Pipeline OO para Tratamento de Dados Industriais em Python & Visualização no Power BI

> **Projeto Integrador em Big Data para Indústria III (3º Ciclo)**  
> **Instituição:** Fatec São Carlos  
> **Curso:** Curso Superior de Tecnologia em Big Data para Indústria  
> **Docente Responsável:** Prof. Dr. Wellington da Rocha Gouveia  
> **Estudante:** Kevyn Aparecido  

---

## 📌 Sobre o Projeto

Este projeto consiste na modelagem, implementação e documentação de um **pipeline de tratamento de dados industriais orientado a objetos (POO)** desenvolvido em Python com `pandas`, associado à criação de um dashboard de exploração analítica no **Power BI** e à reflexão crítica sobre o uso de assistentes de inteligência artificial.

O objetivo principal é transformar dados industriais brutos (com ruídos, nulos, duplicatas e inconsistências categóricas) em um conjunto de dados limpo, auditável, padronizado e enriquecido com métricas de negócio, garantindo reprodutibilidade e conformidade com boas práticas de engenharia de software.

---

## 🛠️ Arquitetura e Estrutura de Diretórios

O sistema adere aos princípios **SOLID** (com ênfase em Responsabilidade Única e Aberto/Fechado), abstração, herança e polimorfismo. Todos os estágios do pipeline derivam do contrato abstrato `EstagioBase`.

```text
projeto_pi3/
├── dados/
│   ├── bruto/          # Arquivo original de dados industriais (somente leitura)
│   └── tratado/        # Dataset final processado, agregados e dicionario_dados.csv
├── src/
│   ├── carga.py        # CarregadorBase e CarregadorCSV com validação de esquema
│   ├── limpeza.py      # LimpadorDados (padronização, nulos, duplicatas e outliers)
│   ├── transformacao.py# TransformadorDados (decomposição temporal, binnings e KPIs)
│   ├── pipeline.py     # Contrato abstrato EstagioBase e orquestrador PipelineDados
│   ├── excecoes.py     # Hierarquia de exceções de domínio (PipelineError)
│   └── exportacao.py   # ExportadorDados (salvamento utf-8-sig e pós-verificação)
├── logs/               # Registros estruturados de execução (pipeline.log)
├── relatorio/          # Relatório Técnico-Reflexivo em PDF (normas ABNT)
├── main.py             # Ponto de entrada executável do pipeline
├── pyproject.toml      # Configuração de dependências do projeto
├── uv.lock             # Lockfile do gerenciador de ambiente uv
└── README.md           # Documentação do repositório
```

---

## ⚙️ Tecnologias e Ferramentas

- **Linguagem de Programação:** Python 3.10+
- **Manipulação de Dados:** `pandas` 2.x, `numpy`
- **Persistência & Formatos:** CSV (`utf-8-sig`)
- **Gerenciamento de Pacotes:** `uv` / `pyproject.toml`
- **Robustez & Governança:** `logging` nativo e Exceções Personalizadas de Domínio
- **Visualização Analítica:** Power BI Desktop

---

## 🚀 Como Executar o Projetos

### 1. Pré-requisitos

Certifique-se de ter o arquivo bruto posicionado em:
`dados/bruto/dados_industriais_brutos.csv`

### 2. Execução via `uv` (Recomendado)

```bash
# Executa a suíte e o pipeline principal
uv run main.py
```

### 3. Execução Tradicional via Python

```bash
# Instalar dependências necessárias
pip install pandas numpy

# Executar o pipeline de ponta a ponta
python main.py
```

---

## 📊 Estágios do Pipeline de Dados

1. **Carga (`carga.py`):** Validação de existência de arquivo e checagem de colunas obrigatórias via `CarregadorBase` / `CarregadorCSV`.
2. **Limpeza (`limpeza.py`):** Conversão de nomes em `snake_case`, remoção de duplicatas por chave de negócio (`id_maquina` + `timestamp`), tratamento de ausentes e sinalização de outliers via IQR (coluna booleana `flag_outlier_*`).
3. **Transformação (`transformacao.py`):** Extração de componentes de data/hora, classificação de turnos, cálculo de taxas de refugo/eficiência e geração de agregações.
4. **Orquestração (`pipeline.py`):** Execução sequencial polimórfica dos estágios respeitando o princípio Aberto/Fechado.
5. **Robustez (`excecoes.py` e `main.py`):** Captura de exceções específicas com gravação simultânea em console e arquivo `logs/pipeline.log`.
6. **Exportação (`exportacao.py`):** Salvamento com `utf-8-sig`, checagem pós-escrita e emissão do `dicionario_dados.csv`.
7. **Visualização no Power BI:** Dashboard exploratório contendo 4 cartões de KPI, série temporal com médias móveis, gráfico categórico, distribuição e matrizes.

---

## 📄 Entregáveis Obrigatórios

- **Código-fonte comentado:** Todos os módulos em `src/` e `main.py` com _docstrings_ e _type hints_.
- **Conjunto de Dados Tratado:** Salvo em `dados/tratado/` juntamente com a tabela agregada e o `dicionario_dados.csv`.
- **Relatório Técnico-Reflexivo (PDF):** Documento ABNT (12 a 20 páginas) com as 12 seções obrigatórias e o registro de uso da IA na Seção 7.
- **Arquivo `.pbix` e Capturas do Power BI:** Incluídos no arquivo compactado final de entrega.

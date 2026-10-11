"""
Ponto de entrada do pipeline de tratamento de dados industriais.

Este módulo coordena a execução do processo de tratamento dos dados,
desde a leitura do arquivo CSV bruto até a aplicação dos estágios de
limpeza, transformação e exportação.

Responsabilidades:
    - Definir os caminhos dos arquivos de entrada e saída.
    - Configurar o registro de logs.
    - Carregar os dados industriais.
    - Montar e executar o pipeline de tratamento.
    - Tratar exceções previstas durante a execução.
    - Informar o resultado final do processamento.

A função main() retorna um código de saída que indica o resultado
da execução: 0 para sucesso e 1 para falhas controladas.
"""

from src.carga import CarregadorCSV
from src.excecoes import (
    ArquivoNaoEncontradoError,
    EsquemaInvalidoError,
    PipelineError,
)
from src.exportacao import ExportadorDados
from src.limpeza import LimpadorDados
from src.pipeline import PipelineDados
from src.transformacao import TransformadorDados
import logging
from pathlib import Path
import pandas as pd

# Define os diretórios utilizados pelo pipeline.
CAMINHO_BRUTO = Path("dados/bruto").resolve()
CAMINHO_TRATADO = Path("dados/tratado").resolve()

# Define o caminho completo do arquivo CSV de origem.
CAMINHO_CSV_ORIGINAL = Path(CAMINHO_BRUTO / "dados_industriais_brutos.csv").resolve()

# Define as colunas que devem existir no arquivo de origem.
# Quando None, a validação de colunas obrigatórias não é aplicada.
COLS_OBRIGATORIAS = None

# Configura o formato básico das mensagens de log.
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

# Cria o logger utilizado neste módulo.
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Executa o pipeline de tratamento dos dados industriais.

    O processo carrega o arquivo CSV de origem, configura os estágios
    de tratamento e executa o pipeline sequencialmente.

    Returns:
        int: Retorna 0 quando o processamento é concluído com sucesso
        ou 1 quando ocorre uma falha controlada.

    Raises:
        PipelineError: Pode propagar erros de leitura de CSV malformado,
            preservando a exceção original como causa.
    """

    # configurar_logging()

    try:
        # Carrega os dados brutos e valida as colunas configuradas.
        df = CarregadorCSV(
            CAMINHO_CSV_ORIGINAL,
            COLS_OBRIGATORIAS,
        ).carregar()

        # Define a sequência de estágios do pipeline.
        pipeline = PipelineDados(
            [
                LimpadorDados(
                    ["Timestamp Registro"],
                    "Timestamp Registro",
                    [
                        "Temp (°C)",
                        "Vibração mm/s",
                        "Pecas Produzidas",
                        "Pecas Refugadas",
                    ],
                    ["ID Maquina", "Status Operacao"],
                ),
                # TransformadorDados(),
                # ExportadorDados(CAMINHO_TRATADO),
            ]
        )

        # Executa os estágios habilitados e obtém os dados processados.
        df_final = pipeline.rodar(df)

    except ArquivoNaoEncontradoError as e:
        """Registra falhas relacionadas à ausência do arquivo de origem."""
        logger.error("Falha na origem dos dados: %s", e)
        return 1

    except EsquemaInvalidoError as e:
        """Registra falhas relacionadas às colunas obrigatórias ausentes."""
        logger.error("Esquema incompatível. Ausentes: %s", e.faltantes)
        return 1

    except pd.errors.ParserError as e:
        """Converte erros de análise do CSV em erros do pipeline."""
        # Preserva a causa original para facilitar a depuração.
        raise PipelineError("CSV malformado — verifique separador e aspas") from e

    except PipelineError as e:
        """Registra erros controlados durante a execução do pipeline."""
        logger.exception("Erro controlado do pipeline: %s", e)
        return 1

    else:
        """Registra o resultado quando todos os estágios são concluídos."""
        logger.info(
            "Pipeline concluído com sucesso: %d registros",
            len(df_final),
        )
        return 0

    finally:
        """Registra o encerramento da execução."""
        logger.info("Execução finalizada — log disponível em logs/pipeline.log")


if __name__ == "__main__":
    main()

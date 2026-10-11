from src.carga import CarregadorCSV
from src.excecoes import ArquivoNaoEncontradoError, EsquemaInvalidoError, PipelineError
from src.exportacao import ExportadorDados
from src.limpeza import LimpadorDados
from src.pipeline import PipelineDados
from src.transformacao import TransformadorDados
import logging
from pathlib import Path
import pandas as pd

CAMINHO_BRUTO = Path("dados/bruto").resolve()
CAMINHO_TRATADO = Path("dados/tratado").resolve()
CAMINHO_CSV_ORIGINAL = Path(
    CAMINHO_BRUTO.resolve() / "dados_industriais_brutos.csv"
).resolve()
COLS_OBRIGATORIAS = None
# ["Timestamp Registro","ID Maquina","Temp (°C)","Vibração mm/s","Pecas Produzidas","Pecas Refugadas","Status Operacao"]

CAMINHO_LOG = Path("logs/pipeline.log").resolve()
CAMINHO_LOG.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(CAMINHO_LOG, mode="w", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def main() -> int:
    # configurar_logging()
    try:
        df = CarregadorCSV(CAMINHO_CSV_ORIGINAL, COLS_OBRIGATORIAS).carregar()
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
                TransformadorDados("Timestamp Registro"),
                ExportadorDados(
                    CAMINHO_TRATADO,
                    formato="csv",
                    versionar=True,
                ),
            ]
        )
        df_final = pipeline.rodar(df)

    except ArquivoNaoEncontradoError as e:
        logger.error("Falha na origem dos dados: %s", e)
        return 1
    except EsquemaInvalidoError as e:
        logger.error("Esquema incompatível. Ausentes: %s", e.faltantes)
        return 1
    except pd.errors.ParserError as e:
        # preserva a causa original para depuração posterior
        raise PipelineError("CSV malformado — verifique separador e aspas") from e
    except PipelineError as e:
        logger.exception("Erro controlado do pipeline: %s", e)
        return 1
    else:
        logger.info("Pipeline concluído com sucesso: %d registros", len(df_final))
        return 0
    finally:
        logger.info("Execução finalizada — log disponível em logs/pipeline.log")


main()

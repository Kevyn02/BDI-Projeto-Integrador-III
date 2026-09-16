from abc import ABC, abstractmethod
from pathlib import Path
from .excecoes import ArquivoNaoEncontradoError,EsquemaInvalidoError
import logging
import pandas as pd


logger = logging.getLogger(__name__)


class CarregadorBase(ABC):
    """Contrato comum a todas as fontes de dados do pipeline.

    Attributes:
        caminho: Caminho do arquivo de origem.
        colunas_obrigatorias: Colunas que devem existir após a leitura.
    """

    def __init__(self, caminho: str, colunas_obrigatorias: list[str] | None = None) -> None:
        self.caminho = Path(caminho)
        self.colunas_obrigatorias = colunas_obrigatorias or []

    @abstractmethod
    def _ler(self) -> pd.DataFrame:
        """Leitura específica de cada formato. Implementar nas subclasses."""

    def carregar(self) -> pd.DataFrame:
        """Executa leitura e validação de esquema.

        Returns:
            DataFrame validado.
        """
        if not self.caminho.exists():
            raise ArquivoNaoEncontradoError(self.caminho)

        df = self._ler()
        self._validar_esquema(df)
        logger.info("Carga concluída: %d linhas, %d colunas", *df.shape)
        return df

    def _validar_esquema(self, df: pd.DataFrame) -> None:
        faltantes = set(self.colunas_obrigatorias) - set(df.columns)
        if faltantes:
            raise EsquemaInvalidoError(sorted(faltantes))


class CarregadorCSV(CarregadorBase):
    """Carrega dados industriais a partir de arquivo CSV."""

    def __init__(self, caminho, colunas_obrigatorias=None,
                 sep: str = ",", encoding: str = "utf-8", decimal: str = "."):
        super().__init__(caminho, colunas_obrigatorias)
        self.sep, self.encoding, self.decimal = sep, encoding, decimal

    def _ler(self) -> pd.DataFrame:
        return pd.read_csv(self.caminho, sep=self.sep,
                           encoding=self.encoding, decimal=self.decimal)

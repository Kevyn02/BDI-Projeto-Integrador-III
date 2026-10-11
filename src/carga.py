from abc import ABC, abstractmethod
from pathlib import Path
import logging
import pandas as pd

from .excecoes import ArquivoNaoEncontradoError, EsquemaInvalidoError

logger = logging.getLogger(__name__)


class CarregadorBase(ABC):
    """Contrato comum a todas as fontes de dados do pipeline."""

    def __init__(
        self,
        caminho: str | Path,
        colunas_obrigatorias: list[str] | None = None,
    ) -> None:
        self.caminho = Path(caminho)
        self.colunas_obrigatorias = colunas_obrigatorias or []

    @abstractmethod
    def _ler(self) -> pd.DataFrame:
        """Realiza a leitura específica da fonte de dados."""

    def carregar(self) -> pd.DataFrame:
        """Carrega os dados e valida o esquema."""

        if not self.caminho.is_file():
            raise ArquivoNaoEncontradoError(self.caminho)

        df = self._ler()
        self._validar_esquema(df)

        logger.info(
            "Carga concluída: %d linhas, %d colunas",
            *df.shape,
        )

        return df

    def _validar_esquema(self, df: pd.DataFrame) -> None:
        """Verifica se as colunas obrigatórias estão presentes."""

        faltantes = set(self.colunas_obrigatorias) - set(df.columns)

        if faltantes:
            raise EsquemaInvalidoError(sorted(faltantes))


class CarregadorCSV(CarregadorBase):
    """Carrega dados industriais a partir de um arquivo CSV."""

    def __init__(
        self,
        caminho: str | Path,
        colunas_obrigatorias: list[str] | None = None,
        sep: str = ",",
        encoding: str = "utf-8",
        decimal: str = ".",
    ) -> None:
        super().__init__(caminho, colunas_obrigatorias)

        self.sep = sep
        self.encoding = encoding
        self.decimal = decimal

    def _ler(self) -> pd.DataFrame:
        """Lê o arquivo CSV utilizando as configurações definidas."""

        return pd.read_csv(
            self.caminho,
            sep=self.sep,
            encoding=self.encoding,
            decimal=self.decimal,
        )

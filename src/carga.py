"""
Módulo responsável pelo carregamento dos dados de origem.

Define uma classe base para padronizar o carregamento de diferentes
fontes de dados e uma implementação específica para arquivos CSV.

Responsabilidades:
    - Verificar a existência do arquivo de origem.
    - Ler os dados utilizando pandas.
    - Validar a presença das colunas obrigatórias.
    - Registrar informações sobre a carga realizada.

Classes:
    CarregadorBase: Define o contrato comum para os carregadores.
    CarregadorCSV: Implementa o carregamento de arquivos CSV.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import logging
import pandas as pd

from .excecoes import ArquivoNaoEncontradoError, EsquemaInvalidoError

logger = logging.getLogger(__name__)


class CarregadorBase(ABC):
    """
    Define o contrato comum para carregadores de dados.

    Esta classe abstrata estabelece as operações necessárias para
    carregar dados de diferentes fontes. As classes derivadas devem
    implementar o método _ler().

    Attributes:
        caminho (Path): Caminho do arquivo que será carregado.
        colunas_obrigatorias (list[str]): Colunas que devem existir
            nos dados carregados.
    """

    def __init__(
        self,
        caminho: str | Path,
        colunas_obrigatorias: list[str] | None = None,
    ) -> None:
        """
        Inicializa o carregador com o caminho e as colunas esperadas.

        Args:
            caminho: Caminho do arquivo de origem.
            colunas_obrigatorias: Lista de colunas exigidas no arquivo.
                Se None ou vazia, a validação de colunas será dispensada.
        """

        self.caminho = Path(caminho)
        self.colunas_obrigatorias = colunas_obrigatorias or []

    @abstractmethod
    def _ler(self) -> pd.DataFrame:
        """
        Lê os dados da fonte especificada.

        Este método deve ser implementado pelas classes derivadas.

        Returns:
            pd.DataFrame: Dados lidos da fonte de origem.
        """

    def carregar(self) -> pd.DataFrame:
        """
        Carrega os dados e valida sua estrutura.

        Verifica se o caminho informado corresponde a um arquivo,
        realiza a leitura dos dados e valida a presença das colunas
        obrigatórias configuradas.

        Returns:
            pd.DataFrame: Dados carregados e validados.

        Raises:
            ArquivoNaoEncontradoError: Se o arquivo não existir.
            EsquemaInvalidoError: Se houver colunas obrigatórias ausentes.
        """

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
        """
        Verifica se as colunas obrigatórias estão presentes.

        Compara as colunas esperadas com as colunas disponíveis no
        DataFrame. Se houver colunas ausentes, interrompe o processo
        por meio de uma exceção específica.

        Args:
            df: DataFrame cujas colunas serão verificadas.

        Raises:
            EsquemaInvalidoError: Se uma ou mais colunas obrigatórias
                não forem encontradas.
        """

        faltantes = set(self.colunas_obrigatorias) - set(df.columns)

        if faltantes:
            raise EsquemaInvalidoError(sorted(faltantes))


class CarregadorCSV(CarregadorBase):
    """
    Implementa o carregamento de dados a partir de arquivos CSV.

    Utiliza pandas.read_csv() para ler o arquivo e permite configurar
    o separador, a codificação de caracteres e o símbolo decimal.

    Attributes:
        sep (str): Separador utilizado entre os campos do CSV.
        encoding (str): Codificação de caracteres do arquivo.
        decimal (str): Símbolo utilizado como separador decimal.
    """

    def __init__(
        self,
        caminho: str | Path,
        colunas_obrigatorias: list[str] | None = None,
        sep: str = ",",
        encoding: str = "utf-8",
        decimal: str = ".",
    ) -> None:
        """
        Inicializa o carregador de arquivos CSV.

        Args:
            caminho: Caminho do arquivo CSV.
            colunas_obrigatorias: Colunas que devem existir no arquivo.
            sep: Separador dos campos. O padrão é vírgula.
            encoding: Codificação de caracteres. O padrão é UTF-8.
            decimal: Símbolo separador decimal. O padrão é ponto.
        """

        super().__init__(caminho, colunas_obrigatorias)

        self.sep = sep
        self.encoding = encoding
        self.decimal = decimal

    def _ler(self) -> pd.DataFrame:
        """
        Lê o arquivo CSV e converte seu conteúdo em um DataFrame.

        Utiliza as configurações definidas na inicialização do objeto.

        Returns:
            pd.DataFrame: Dados contidos no arquivo CSV.

        Raises:
            pandas.errors.ParserError: Se ocorrer um erro de análise
                da estrutura do CSV.
            UnicodeDecodeError: Se o arquivo não puder ser decodificado
                com a codificação informada.
        """

        return pd.read_csv(
            self.caminho,
            sep=self.sep,
            encoding=self.encoding,
            decimal=self.decimal,
        )

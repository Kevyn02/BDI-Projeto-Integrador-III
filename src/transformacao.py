"""
Módulo responsável pela transformação e pelo enriquecimento dos dados.

Define a classe TransformadorDados, que adiciona informações derivadas
ao DataFrame após a etapa de limpeza, preparando os dados para análise
e utilização em ferramentas de visualização.

Responsabilidades:
    - Decompor a data de registro em informações temporais.
    - Classificar os registros conforme o turno de operação.
    - Calcular a taxa de refugo da produção.
    - Categorizar os registros de acordo com a taxa de refugo.

Classes:
    TransformadorDados: Executa as transformações dos dados industriais.
"""

import logging
import pandas as pd

from .pipeline import EstagioBase

logger = logging.getLogger(__name__)


class TransformadorDados(EstagioBase):
    """
    Enriquece os dados industriais com variáveis derivadas e temporais.

    Esta classe implementa o contrato EstagioBase e realiza
    transformações no DataFrame recebido, preservando os dados
    originais por meio da criação de uma cópia.

    Attributes:
        nome (str): Identificador do estágio no histórico do pipeline.
        col_data (str): Nome da coluna que contém as datas dos registros.
    """

    nome = "transformacao"

    TURNOS = {
        "1º Turno": range(6, 14),
        "2º Turno": range(14, 22),
    }

    def __init__(
        self,
        col_data: str = "Timestamp Registro",
    ) -> None:
        """
        Inicializa o transformador de dados.

        Args:
            col_data: Nome da coluna que contém a data e a hora
                dos registros. O padrão é "Timestamp Registro".
        """

        self.col_data = col_data

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa sequencialmente as transformações dos dados.

        Cria uma cópia do DataFrame e aplica a decomposição da data,
        a criação de indicadores e a categorização dos registros.

        Args:
            df: DataFrame limpo que será transformado.

        Returns:
            pd.DataFrame: DataFrame enriquecido com as novas variáveis.
        """

        df = df.copy()
        df = self._decompor_data(df)
        df = self._criar_indicadores(df)
        df = self._categorizar(df)

        logger.info(
            "Transformação concluída: %d linhas, %d colunas",
            *df.shape,
        )

        return df

    def _decompor_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai informações temporais da coluna de data.

        Converte a coluna configurada para o tipo datetime e cria
        colunas derivadas para o ano, o mês, o dia da semana e o turno
        correspondente à hora do registro.

        Args:
            df: DataFrame que contém a coluna de data.

        Returns:
            pd.DataFrame: DataFrame acrescido das colunas temporais.
        """

        df[self.col_data] = pd.to_datetime(
            df[self.col_data],
            errors="coerce",
        )

        d = df[self.col_data].dt

        df["ano"] = d.year
        df["mes"] = d.month
        df["dia_semana"] = d.day_name()
        df["turno"] = d.hour.map(self._classificar_turno)

        return df

    @staticmethod
    def _classificar_turno(hora: int) -> str:
        """
        Classifica uma hora do dia conforme o turno de operação.

        A classificação utilizada é:
            - 1º Turno: das 06h às 13h59.
            - 2º Turno: das 14h às 21h59.
            - 3º Turno: das 22h às 05h59.

        Args:
            hora: Hora do registro, entre 0 e 23.

        Returns:
            str: Nome do turno correspondente.
        """

        if 6 <= hora < 14:
            return "1º Turno"

        if 14 <= hora < 22:
            return "2º Turno"

        return "3º Turno"

    def _criar_indicadores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores derivados da produção industrial.

        Cria a coluna taxa_refugo, que representa a proporção de peças
        refugadas em relação à quantidade de peças produzidas.
        Quando a produção é zero, a taxa resultante é definida como zero.

        Args:
            df: DataFrame que contém as colunas de produção e refugo.

        Returns:
            pd.DataFrame: DataFrame acrescido da coluna taxa_refugo.
        """

        df["taxa_refugo"] = (
            df["Pecas Refugadas"]
            .div(df["Pecas Produzidas"].replace(0, pd.NA))
            .fillna(0)
            .round(4)
        )

        return df

    def _categorizar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categoriza os registros conforme a taxa de refugo.

        Utiliza faixas de valores para classificar a taxa como Baixo,
        Moderado ou Alto.

        Faixas utilizadas:
            - Baixo: taxa menor ou igual a 2%.
            - Moderado: taxa maior que 2% e menor ou igual a 5%.
            - Alto: taxa superior a 5%.

        Args:
            df: DataFrame que contém a coluna taxa_refugo.

        Returns:
            pd.DataFrame: DataFrame acrescido da coluna categoria_refugo.
        """

        df["categoria_refugo"] = pd.cut(
            df["taxa_refugo"],
            bins=[-float("inf"), 0.02, 0.05, float("inf")],
            labels=["Baixo", "Moderado", "Alto"],
        )

        return df

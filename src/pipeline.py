"""
Módulo responsável pela estrutura e execução do pipeline de dados.

Define uma classe abstrata que estabelece o contrato dos estágios
de processamento e uma classe responsável por executar esses estágios
em sequência.

Responsabilidades:
    - Definir um contrato comum para os estágios do pipeline.
    - Organizar os estágios na ordem de execução.
    - Permitir adicionar novos estágios ao pipeline.
    - Executar cada estágio sobre o DataFrame recebido.
    - Registrar o histórico das operações realizadas.
    - Registrar informações sobre a quantidade de linhas processadas.

Classes:
    EstagioBase: Define o contrato comum dos estágios.
    PipelineDados: Coordena a execução dos estágios de processamento.
"""

from abc import ABC, abstractmethod
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class EstagioBase(ABC):
    """
    Define o contrato comum para todos os estágios do pipeline.

    Esta classe abstrata estabelece a estrutura que deve ser seguida
    pelos estágios de limpeza, transformação e exportação. Cada estágio
    concreto deve implementar o método executar(), recebendo um
    DataFrame e retornando o resultado do processamento.

    Attributes:
        nome (str): Identificador do estágio, utilizado nos registros
            de log e no histórico de execução.
    """

    nome: str = "estagio"

    @abstractmethod
    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa o processamento específico do estágio.

        Este método deve ser implementado pelas classes derivadas.

        Args:
            df: DataFrame que será processado pelo estágio.

        Returns:
            pd.DataFrame: DataFrame resultante do processamento.
        """


class PipelineDados:
    """
    Orquestra a execução sequencial dos estágios de processamento.

    Recebe uma lista de estágios e executa cada um na ordem definida.
    O resultado de um estágio é utilizado como entrada do estágio
    seguinte, permitindo encadear operações de limpeza, transformação
    e exportação.

    Attributes:
        estagios (list[EstagioBase]): Estágios que serão executados,
            organizados na ordem de processamento.
        historico (list[dict[str, int | str]]): Registros das execuções
            dos estágios, incluindo nome, quantidade de linhas antes
            e depois do processamento e quantidade de colunas.
    """

    def __init__(self, estagios: list[EstagioBase]) -> None:
        """
        Inicializa o pipeline com os estágios de processamento.

        Args:
            estagios: Lista de objetos que implementam EstagioBase,
                organizados na ordem em que devem ser executados.
        """

        self.estagios = list(estagios)
        self.historico: list[dict[str, int | str]] = []

    def adicionar(self, estagio: EstagioBase) -> "PipelineDados":
        """
        Adiciona um estágio ao final do pipeline.

        Retorna a própria instância para permitir o encadeamento
        de chamadas ao método adicionar().

        Args:
            estagio: Estágio que será incluído na sequência.

        Returns:
            PipelineDados: A própria instância do pipeline.
        """

        if not isinstance(estagio, EstagioBase):
            raise TypeError("O estágio deve ser uma instância de EstagioBase.")

        self.estagios.append(estagio)

        return self

    def rodar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa todos os estágios na ordem definida.

        Cada estágio recebe o DataFrame resultante do estágio anterior.
        Após cada execução, registra no histórico o nome do estágio,
        a quantidade de linhas antes e depois do processamento e
        a quantidade de colunas resultantes.

        O histórico é reiniciado no início de cada execução para
        representar apenas o processamento mais recente.

        Args:
            df: DataFrame inicial que será processado pelo pipeline.

        Returns:
            pd.DataFrame: DataFrame resultante da execução de todos
                os estágios.

        Raises:
            TypeError: Se a entrada não for um DataFrame ou se algum
                estágio não retornar um DataFrame.
            Exception: Exceções não tratadas pelos estágios podem
                interromper a execução e ser propagadas ao chamador.
        """

        if not isinstance(df, pd.DataFrame):
            raise TypeError("A entrada do pipeline deve ser um DataFrame.")

        self.historico.clear()

        for estagio in self.estagios:
            linhas_antes = len(df)

            df = estagio.executar(df)

            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"O estágio '{estagio.nome}' " "não retornou um DataFrame."
                )

            self.historico.append(
                {
                    "estagio": estagio.nome,
                    "linhas_antes": linhas_antes,
                    "linhas_depois": len(df),
                    "colunas": df.shape[1],
                }
            )

            logger.info(
                "[%s] %d → %d linhas",
                estagio.nome,
                linhas_antes,
                len(df),
            )

        return df

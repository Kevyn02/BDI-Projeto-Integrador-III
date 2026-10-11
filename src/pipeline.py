from abc import ABC, abstractmethod
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class EstagioBase(ABC):
    """Contrato único de todo estágio do pipeline."""

    nome: str = "estagio"

    @abstractmethod
    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Recebe um DataFrame e devolve o DataFrame processado."""


class PipelineDados:
    """Orquestra a execução sequencial dos estágios de tratamento."""

    def __init__(self, estagios: list[EstagioBase]) -> None:
        self.estagios = list(estagios)
        self.historico: list[dict[str, int | str]] = []

    def adicionar(self, estagio: EstagioBase) -> "PipelineDados":
        """Adiciona um estágio ao pipeline."""

        if not isinstance(estagio, EstagioBase):
            raise TypeError("O estágio deve ser uma instância de EstagioBase.")

        self.estagios.append(estagio)
        return self

    def rodar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Executa os estágios em sequência e registra o histórico."""

        if not isinstance(df, pd.DataFrame):
            raise TypeError("A entrada do pipeline deve ser um DataFrame.")

        self.historico.clear()

        for estagio in self.estagios:
            linhas_antes = len(df)

            df = estagio.executar(df)

            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"O estágio '{estagio.nome}' não retornou um DataFrame."
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

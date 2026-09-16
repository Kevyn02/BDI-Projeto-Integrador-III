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
    """Orquestra a execução sequencial de estágios de tratamento.

    Example:
        >>> pipe = PipelineDados([LimpadorDados(...), TransformadorDados(...)])
        >>> df_final = pipe.rodar(df_bruto)
    """

    def __init__(self, estagios: list[EstagioBase]) -> None:
        self.estagios = estagios
        self.historico: list[dict] = []

    def adicionar(self, estagio: EstagioBase) -> "PipelineDados":
        """Permite encadeamento fluente: pipe.adicionar(a).adicionar(b)."""
        self.estagios.append(estagio)
        return self

    def rodar(self, df: pd.DataFrame) -> pd.DataFrame:
        # Polimorfismo: o pipeline desconhece o tipo concreto de cada estágio
        for estagio in self.estagios:
            linhas_antes = len(df)
            df = estagio.executar(df)
            self.historico.append({
                "estagio": estagio.nome,
                "linhas_antes": linhas_antes,
                "linhas_depois": len(df),
                "colunas": df.shape[1],
            })
            logger.info("[%s] %d → %d linhas", estagio.nome, linhas_antes, len(df))
        return df

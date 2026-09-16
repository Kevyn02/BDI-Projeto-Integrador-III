from pathlib import Path
import logging
import pandas as pd
from .excecoes import PipelineError, DadosVaziosError
from .pipeline import  EstagioBase

logger = logging.getLogger(__name__)

class ExportadorDados(EstagioBase):
    """Persiste o conjunto tratado em formato consumível por ferramentas de BI."""
    nome = "exportacao"

    def __init__(self, destino: str, formato: str = "csv", versionar: bool = True):
        self.destino, self.formato, self.versionar = Path(destino), formato, versionar

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise DadosVaziosError("Nada a exportar: DataFrame vazio.")

        self.destino.parent.mkdir(parents=True, exist_ok=True)
        caminho = self._resolver_caminho()

        try:
            if self.formato == "csv":
                df.to_csv(caminho, index=False, sep=",",
                          encoding="utf-8-sig",          # acentos corretos no Power BI
                          date_format="%Y-%m-%d %H:%M:%S")
            elif self.formato == "xlsx":
                df.to_excel(caminho, index=False, sheet_name="dados_tratados")
            else:
                raise ValueError(f"Formato não suportado: {self.formato}")
        except PermissionError as e:
            raise PipelineError(
                f"Sem permissão de escrita em {caminho}. Feche o arquivo se estiver aberto."
            ) from e

        self._verificar(caminho, df)
        logger.info("Exportado: %s (%d linhas)", caminho, len(df))
        return df

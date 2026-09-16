import logging
import pandas as pd
from .pipeline import  EstagioBase

logger = logging.getLogger(__name__)

class LimpadorDados(EstagioBase):
    """Aplica limpeza estrutural e de conteúdo ao DataFrame industrial."""

    def __init__(self, chave_negocio: list[str],
                 col_data: str, cols_numericas: list[str],
                 cols_categoricas: list[str], limite_iqr: float = 1.5):
        self.chave_negocio = chave_negocio
        self.col_data = col_data
        self.cols_numericas = cols_numericas
        self.cols_categoricas = cols_categoricas
        self.limite_iqr = limite_iqr
        self.relatorio: dict[str, int] = {}   # auditoria da limpeza

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encadeia as rotinas de limpeza preservando o DataFrame de entrada."""
        df = df.copy()                          # não altera a origem
        df = self._padronizar_colunas(df)
        df = self._converter_tipos(df)
        df = self._remover_duplicatas(df)
        df = self._tratar_ausentes(df)
        df = self._padronizar_categorias(df)
        df = self._marcar_outliers(df)
        logger.info("Limpeza: %s", self.relatorio)
        return df

    def _remover_duplicatas(self, df):
        antes = len(df)
        df = df.drop_duplicates(subset=self.chave_negocio, keep="last")
        self.relatorio["duplicatas_removidas"] = antes - len(df)
        return df

    def _marcar_outliers(self, df):
        """Sinaliza outliers por IQR sem descartá-los: em contexto industrial,
        a anomalia pode ser o próprio evento de interesse."""
        for col in self.cols_numericas:
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            inf, sup = q1 - self.limite_iqr * iqr, q3 + self.limite_iqr * iqr
            df[f"flag_outlier_{col}"] = ~df[col].between(inf, sup)
            self.relatorio[f"outliers_{col}"] = int(df[f"flag_outlier_{col}"].sum())
        return df

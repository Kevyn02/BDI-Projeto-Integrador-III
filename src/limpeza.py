import logging
import pandas as pd
from .pipeline import EstagioBase

logger = logging.getLogger(__name__)


class LimpadorDados(EstagioBase):
    """Aplica limpeza estrutural e de conteúdo ao DataFrame industrial."""

    def __init__(
        self,
        chave_negocio: list[str],
        col_data: str,
        cols_numericas: list[str],
        cols_categoricas: list[str],
        limite_iqr: float = 1.5,
    ):
        self.chave_negocio = chave_negocio
        self.col_data = col_data
        self.cols_numericas = cols_numericas
        self.cols_categoricas = cols_categoricas
        self.limite_iqr = limite_iqr
        self.relatorio: dict[str, int] = {}  # auditoria da limpeza

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encadeia as rotinas de limpeza preservando o DataFrame de entrada."""
        df = df.copy()  # não altera a origem
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

    def _padronizar_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove espaços extras dos nomes das colunas."""
        df.columns = df.columns.astype(str).str.strip()
        return df

    def _converter_tipos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converte as colunas para os tipos esperados."""
        df[self.col_data] = pd.to_datetime(df[self.col_data], errors="coerce")

        for col in self.cols_numericas:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in self.cols_categoricas:
            df[col] = df[col].astype("string").str.strip()

        return df

    def _tratar_ausentes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove registros sem chave de negócio ou data."""
        antes = len(df)

        df = df.dropna(subset=self.chave_negocio + [self.col_data])

        self.relatorio["registros_sem_chave_ou_data"] = antes - len(df)

        return df

    def _padronizar_categorias(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove espaços e padroniza categorias em maiúsculas."""
        for col in self.cols_categoricas:
            df[col] = df[col].str.strip().str.upper()

        return df

import logging
import pandas as pd
from .pipeline import EstagioBase

logger = logging.getLogger(__name__)


class TransformadorDados(EstagioBase):
    """Enriquece o conjunto limpo com variáveis derivadas e temporais."""

    TURNOS = {
        "1º Turno": range(6, 14),
        "2º Turno": range(14, 22),
    }

    def __init__(self, col_data: str):
        self.col_data = col_data

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria variáveis temporais, indicadores e categorias."""
        df = df.copy()
        df = self._decompor_data(df)
        df = self._criar_indicadores(df)
        df = self._categorizar(df)

        logger.info("Transformação concluída: %d registros", len(df))
        return df

    def _decompor_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrai informações temporais da coluna de data."""
        d = pd.to_datetime(df[self.col_data], errors="coerce")

        df["ano"] = d.dt.year
        df["mes"] = d.dt.month
        df["dia_semana"] = d.dt.day_name()
        df["turno"] = d.dt.hour.map(self._classificar_turno)

        return df

    @staticmethod
    def _classificar_turno(hora: int) -> str:
        """Classifica a hora nos três turnos."""
        if pd.isna(hora):
            return None
        if 6 <= hora < 14:
            return "1º Turno"
        if 14 <= hora < 22:
            return "2º Turno"
        return "3º Turno"

    def _criar_indicadores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula a proporção de peças refugadas."""
        produzidas = pd.to_numeric(df["Pecas Produzidas"], errors="coerce")
        refugadas = pd.to_numeric(df["Pecas Refugadas"], errors="coerce")

        taxa = refugadas.div(produzidas.where(produzidas.ne(0)))
        df["taxa_refugo"] = taxa.round(4)

        return df

    def _categorizar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classifica a taxa de refugo em categorias."""
        df["categoria_refugo"] = pd.cut(
            df["taxa_refugo"],
            bins=[-float("inf"), 0.02, 0.05, float("inf")],
            labels=["Baixo", "Moderado", "Alto"],
            right=True,
        )

        return df

import logging
import pandas as pd
from .pipeline import EstagioBase

logger = logging.getLogger(__name__)

class TransformadorDados(EstagioBase):
    """Enriquece o conjunto limpo com variáveis derivadas e temporais."""

    TURNOS = {"1º Turno": range(6, 14), "2º Turno": range(14, 22)}

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = self._decompor_data(df)
        df = self._criar_indicadores(df)
        df = self._categorizar(df)
        return df

    def _decompor_data(self, df):
        d = df[self.col_data].dt
        df["ano"], df["mes"] = d.year, d.month
        df["dia_semana"] = d.day_name()
        df["turno"] = d.hour.map(self._classificar_turno)
        return df

    @staticmethod
    def _classificar_turno(hora: int) -> str:
        if 6 <= hora < 14: return "1º Turno"
        if 14 <= hora < 22: return "2º Turno"
        return "3º Turno"

    def _criar_indicadores(self, df):
        # divisão protegida: evita inf/NaN quando o denominador é zero
        df["taxa_refugo"] = (df["pecas_refugadas"]
                              .div(df["pecas_produzidas"].replace(0, pd.NA))
                              .fillna(0).round(4))
        return df

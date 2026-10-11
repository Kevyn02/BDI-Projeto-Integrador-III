from pathlib import Path
import logging
import pandas as pd

from .excecoes import PipelineError, DadosVaziosError
from .pipeline import EstagioBase

logger = logging.getLogger(__name__)


class ExportadorDados(EstagioBase):
    """Persiste os dados tratados em CSV ou Excel."""

    nome = "exportacao"

    def __init__(
        self,
        destino: str | Path,
        formato: str = "csv",
        versionar: bool = True,
    ) -> None:
        self.destino = Path(destino)
        self.formato = formato.lower()
        self.versionar = versionar

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Exporta os dados e verifica o arquivo gerado."""

        if df.empty:
            raise DadosVaziosError("Nada a exportar: DataFrame vazio.")

        caminho = self._resolver_caminho()
        caminho.parent.mkdir(parents=True, exist_ok=True)

        try:
            if self.formato == "csv":
                df.to_csv(
                    caminho,
                    index=False,
                    sep=",",
                    encoding="utf-8-sig",
                    date_format="%Y-%m-%d %H:%M:%S",
                )

            elif self.formato == "xlsx":
                df.to_excel(
                    caminho,
                    index=False,
                    sheet_name="dados_tratados",
                )

        except PermissionError as e:
            raise PipelineError(
                f"Sem permissão de escrita em {caminho}. "
                "Verifique se o arquivo está aberto."
            ) from e

        self._verificar(caminho, df)

        logger.info(
            "Exportação concluída: %s (%d registros)",
            caminho,
            len(df),
        )

        return df

    def _resolver_caminho(self) -> Path:
        """Define o nome do arquivo e evita sobrescritas."""

        extensoes = {
            "csv": ".csv",
            "xlsx": ".xlsx",
        }

        if self.formato not in extensoes:
            raise ValueError(f"Formato não suportado: {self.formato}")

        extensao = extensoes[self.formato]
        destino = self.destino

        # Se o destino for uma pasta, define um nome padrão.
        if destino.suffix.lower() not in {".csv", ".xlsx"}:
            destino = destino / f"dados_tratados{extensao}"

        # Ajusta a extensão para corresponder ao formato escolhido.
        elif destino.suffix.lower() != extensao:
            destino = destino.with_suffix(extensao)

        if not self.versionar or not destino.exists():
            return destino

        contador = 1

        while True:
            versionado = destino.with_name(f"{destino.stem}_{contador}{destino.suffix}")

            if not versionado.exists():
                return versionado

            contador += 1

    def _verificar(
        self,
        caminho: Path,
        df_original: pd.DataFrame,
    ) -> None:
        """Confere se o arquivo exportado pode ser lido."""

        if not caminho.is_file() or caminho.stat().st_size == 0:
            raise PipelineError(f"O arquivo exportado está ausente ou vazio: {caminho}")

        try:
            if self.formato == "csv":
                df_exportado = pd.read_csv(
                    caminho,
                    encoding="utf-8-sig",
                )

            else:
                df_exportado = pd.read_excel(caminho)

        except (OSError, ValueError, ImportError) as e:
            raise PipelineError(
                f"Não foi possível verificar o arquivo: {caminho}"
            ) from e

        if df_exportado.shape != df_original.shape:
            raise PipelineError(
                "A verificação da exportação falhou: "
                f"esperado {df_original.shape}, "
                f"obtido {df_exportado.shape}."
            )

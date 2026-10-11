"""
Módulo responsável pela exportação dos dados tratados.

Define a classe ExportadorDados, responsável por persistir os dados
processados pelo pipeline em arquivos CSV ou Excel.

Responsabilidades:
    - Verificar se existem dados para exportação.
    - Definir o caminho e o nome do arquivo de saída.
    - Evitar a sobrescrita de arquivos quando o versionamento está ativo.
    - Exportar os dados no formato selecionado.
    - Verificar a estrutura básica do arquivo gerado.
    - Registrar informações sobre a exportação realizada.

Classes:
    ExportadorDados: Exporta e verifica os dados tratados.
"""

from pathlib import Path
import logging
import pandas as pd

from .excecoes import PipelineError, DadosVaziosError
from .pipeline import EstagioBase

logger = logging.getLogger(__name__)


class ExportadorDados(EstagioBase):
    """
    Exporta os dados tratados para arquivos CSV ou Excel.

    Esta classe implementa o contrato EstagioBase e permite que a
    exportação seja executada como uma etapa do pipeline de dados.

    Attributes:
        nome (str): Identificador do estágio no histórico do pipeline.
        destino (Path): Caminho do arquivo ou diretório de destino.
        formato (str): Formato de saída, podendo ser CSV ou XLSX.
        versionar (bool): Define se novos arquivos devem receber
            numeração para evitar sobrescritas.
    """

    nome = "exportacao"

    def __init__(
        self,
        destino: str | Path,
        formato: str = "csv",
        versionar: bool = True,
    ) -> None:
        """
        Inicializa o exportador de dados.

        Args:
            destino: Caminho do arquivo ou diretório de saída.
            formato: Formato de exportação. Aceita "csv" ou "xlsx".
                O padrão é "csv".
            versionar: Quando True, evita sobrescrever arquivos
                existentes criando versões numeradas. O padrão é True.
        """

        self.destino = Path(destino)
        self.formato = formato.lower()
        self.versionar = versionar

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Exporta os dados e verifica o arquivo gerado.

        Cria o diretório de destino quando necessário, exporta o
        DataFrame no formato selecionado e verifica se o arquivo
        resultante possui a estrutura esperada.

        Args:
            df: DataFrame com os dados que serão exportados.

        Returns:
            pd.DataFrame: O próprio DataFrame recebido, permitindo
                a continuidade da execução do pipeline.

        Raises:
            DadosVaziosError: Se o DataFrame não possuir registros.
            ValueError: Se o formato informado não for suportado.
            PipelineError: Se ocorrer uma falha de permissão ou
                de verificação do arquivo exportado.
        """

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
        """
        Determina o caminho final do arquivo de saída.

        Se o destino informado for um diretório ou não possuir uma
        extensão reconhecida, utiliza o nome padrão "dados_tratados"
        com a extensão correspondente ao formato escolhido.

        Quando o versionamento está habilitado e o arquivo já existe,
        procura o próximo nome numerado disponível.

        Returns:
            Path: Caminho final definido para a exportação.

        Raises:
            ValueError: Se o formato de exportação não for suportado.
        """

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
        """
        Verifica se o arquivo exportado pode ser lido e mantém
        a mesma quantidade de linhas e colunas do DataFrame original.

        Reabre o arquivo usando pandas e compara suas dimensões com
        as do DataFrame recebido. Essa verificação não garante que
        todos os valores tenham sido preservados sem alterações.

        Args:
            caminho: Caminho do arquivo que será verificado.
            df_original: DataFrame utilizado como referência.

        Raises:
            PipelineError: Se o arquivo estiver ausente, vazio,
                não puder ser lido ou apresentar dimensões diferentes.
        """

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

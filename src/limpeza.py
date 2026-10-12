"""
Módulo responsável pela limpeza dos dados industriais.

Implementa operações de limpeza estrutural e de conteúdo em um
DataFrame, preparando os dados para as etapas seguintes do pipeline.

As operações incluem:
    - Remoção de espaços extras nos nomes das colunas.
    - Conversão dos dados para os tipos esperados.
    - Remoção de registros duplicados.
    - Exclusão de registros sem chave de negócio ou data.
    - Padronização dos valores categóricos.
    - Identificação de valores atípicos (outliers) pelo método IQR.

Classes:
    LimpadorDados: Executa as operações de limpeza e mantém um
        relatório das alterações realizadas.
"""

import logging
import pandas as pd

from .pipeline import EstagioBase

logger = logging.getLogger(__name__)


class LimpadorDados(EstagioBase):
    """
    Executa a limpeza estrutural e de conteúdo dos dados industriais.

    A classe implementa o contrato EstagioBase e organiza as operações
    de limpeza em uma sequência definida. O DataFrame original é
    preservado por meio da criação de uma cópia.

    Attributes:
        nome (str): Identificador do estágio no histórico do pipeline.
        chave_negocio (list[str]): Colunas utilizadas para identificar
            registros duplicados e validar a presença da chave.
        col_data (str): Nome da coluna que contém a data do registro.
        cols_numericas (list[str]): Colunas convertidas para valores
            numéricos e utilizadas na identificação de outliers.
        cols_categoricas (list[str]): Colunas cujos valores são
            convertidos para texto e padronizados em maiúsculas.
        cols_padronizar: Colunas cujos valores terão espaços externos removidos,
            letras convertidas para maiúsculas e hífens e sublinhados removidos.
        limite_iqr (float): Multiplicador do intervalo interquartil
            utilizado para definir os limites dos outliers.
        relatorio (dict[str, int]): Quantidades de registros removidos
            e de outliers identificados durante a limpeza.
    """

    nome = "limpeza"

    def __init__(
        self,
        chave_negocio: list[str],
        col_data: str,
        cols_numericas: list[str],
        cols_categoricas: list[str],
        cols_padronizar: list[str],
        limite_iqr: float = 1.5,
    ) -> None:
        """
        Inicializa o limpador com as colunas e os critérios de limpeza.

        Args:
            chave_negocio: Colunas que identificam os registros e
                serão utilizadas na remoção de duplicatas.
            col_data: Nome da coluna que contém as datas dos registros.
            cols_numericas: Colunas que devem ser convertidas para
                valores numéricos e analisadas quanto a outliers.
            cols_categoricas: Colunas categóricas que serão convertidas
                para texto e padronizadas.
            cols_padronizar: Colunas cujos valores terão espaços externos removidos,
                letras convertidas para maiúsculas e hífens e sublinhados removidos.
            limite_iqr: Multiplicador do intervalo interquartil usado
                no cálculo dos limites dos outliers. O padrão é 1.5.
        """

        self.chave_negocio = chave_negocio
        self.col_data = col_data
        self.cols_numericas = cols_numericas
        self.cols_categoricas = cols_categoricas
        self.cols_padronizar = cols_padronizar
        self.limite_iqr = limite_iqr

        # Armazena as quantidades de alterações para fins de auditoria.
        self.relatorio: dict[str, int] = {}

    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa sequencialmente todas as operações de limpeza.

        Cria uma cópia do DataFrame recebido e aplica a padronização
        dos nomes das colunas, a conversão dos tipos, a remoção de
        duplicatas, o tratamento de registros ausentes, a padronização
        categórica e a identificação de outliers.

        Args:
            df: DataFrame original que será submetido à limpeza.

        Returns:
            pd.DataFrame: DataFrame após as operações de limpeza.

        Observação:
            As quantidades de registros removidos e de outliers
            identificados são armazenadas no atributo relatorio.
        """

        df = df.copy()
        df = self._padronizar_colunas(df)
        df = self._converter_tipos(df)
        df = self._remover_duplicatas(df)
        df = self._tratar_ausentes(df)
        df = self._padronizar_categorias(df)
        df = self._padronizar_valores_coluna(df)
        df = self._marcar_outliers(df)

        logger.info("Limpeza: %s", self.relatorio)

        return df

    def _remover_duplicatas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove registros duplicados conforme a chave de negócio.

        Compara os valores das colunas definidas em chave_negocio
        e mantém a última ocorrência de cada combinação.

        Args:
            df: DataFrame que terá as duplicatas removidas.

        Returns:
            pd.DataFrame: DataFrame sem as duplicatas identificadas.

        Observação:
            A quantidade de registros removidos é armazenada no
            relatório sob a chave "duplicatas_removidas".
        """

        antes = len(df)

        df = df.drop_duplicates(
            subset=self.chave_negocio,
            keep="last",
        )

        self.relatorio["duplicatas_removidas"] = antes - len(df)

        return df

    def _marcar_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica e sinaliza possíveis valores atípicos nas colunas
        numéricas usando o intervalo interquartil (IQR).

        Para cada coluna, calcula o primeiro quartil (Q1), o terceiro
        quartil (Q3) e o intervalo interquartil (IQR = Q3 - Q1).
        Os valores fora dos limites calculados são sinalizados em uma
        nova coluna booleana, sem serem removidos do DataFrame.

        Args:
            df: DataFrame cujas colunas numéricas serão analisadas.

        Returns:
            pd.DataFrame: DataFrame acrescido das colunas indicadoras
                de outliers.

        Observação:
            As colunas indicadoras recebem o prefixo "flag_outlier_".
            A quantidade de outliers identificados em cada coluna
            é registrada no atributo relatorio.
        """

        for col in self.cols_numericas:
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1

            inf = q1 - self.limite_iqr * iqr
            sup = q3 + self.limite_iqr * iqr

            df[f"flag_outlier_{col}"] = ~df[col].between(inf, sup)

            self.relatorio[f"outliers_{col}"] = int(df[f"flag_outlier_{col}"].sum())

        return df

    def _padronizar_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove espaços extras no início e no final dos nomes das colunas.

        Converte os nomes das colunas para texto e remove espaços
        desnecessários nas extremidades, facilitando o acesso posterior
        aos campos do DataFrame.

        Args:
            df: DataFrame cujos nomes de colunas serão padronizados.

        Returns:
            pd.DataFrame: DataFrame com os nomes das colunas ajustados.
        """

        df.columns = df.columns.astype(str).str.strip()

        return df

    def _converter_tipos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte as colunas para os tipos de dados esperados.

        A coluna de data é convertida para datetime, as colunas
        numéricas são convertidas para valores numéricos e as colunas
        categóricas são convertidas para texto com espaços externos
        removidos.

        Args:
            df: DataFrame cujos tipos de dados serão ajustados.

        Returns:
            pd.DataFrame: DataFrame com os tipos de dados convertidos.

        Observação:
            O parâmetro errors="coerce" transforma valores inválidos
            em NaT nas datas e NaN nos dados numéricos. Esses valores
            podem ser tratados nas etapas seguintes da limpeza.
        """

        df[self.col_data] = pd.to_datetime(
            df[self.col_data],
            errors="coerce",
        )

        for col in self.cols_numericas:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

        for col in self.cols_categoricas:
            df[col] = df[col].astype("string").str.strip()

        return df

    def _tratar_ausentes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove registros sem chave de negócio ou data válida.

        Descarta as linhas que possuem valores ausentes em qualquer
        coluna da chave de negócio ou na coluna de data.

        Args:
            df: DataFrame que terá os registros incompletos removidos.

        Returns:
            pd.DataFrame: DataFrame sem registros que não possuem
                todos os valores necessários para identificar o
                registro e determinar sua data.

        Observação:
            A quantidade de registros removidos é armazenada no
            relatório sob a chave "registros_sem_chave_ou_data".
        """

        antes = len(df)

        df = df.dropna(subset=self.chave_negocio + [self.col_data])

        self.relatorio["registros_sem_chave_ou_data"] = antes - len(df)

        return df

    def _padronizar_categorias(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Padroniza os valores das colunas categóricas.

        Remove espaços externos e converte os valores para letras
        maiúsculas, reduzindo diferenças de representação textual,
        como "Ativa", "ativa" e " ATIVA ".

        Args:
            df: DataFrame cujas categorias serão padronizadas.

        Returns:
            pd.DataFrame: DataFrame com os valores categóricos
                padronizados.
        """

        for col in self.cols_categoricas:
            df[col] = df[col].str.strip().str.upper()

        return df

    def _padronizar_valores_coluna(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza os valores das colunas configuradas na classe.

        Para cada coluna existente no DataFrame, remove espaços externos,
        converte letras para maiúsculas e remove hífens e sublinhados.

        Colunas configuradas que não existirem no DataFrame serão ignoradas.

        Args:
            df: DataFrame que contém os dados a serem padronizados.

        Returns:
            DataFrame com os valores das colunas configuradas padronizados.
        """
        for coluna in self.cols_padronizar:
            if coluna in df.columns:
                df[coluna] = (
                    df[coluna]
                    .astype("string")
                    .str.strip()
                    .str.upper()
                    .str.replace(r"[-_]", "", regex=True)
                )

        return df

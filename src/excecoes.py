class PipelineError(Exception):
    """Exceção-raiz do projeto: permite capturar qualquer falha do pipeline."""


class ArquivoNaoEncontradoError(PipelineError):
    def __init__(self, caminho):
        super().__init__(f"Arquivo de origem inexistente: {caminho}")


class EsquemaInvalidoError(PipelineError):
    def __init__(self, faltantes: list[str]):
        self.faltantes = faltantes
        super().__init__(f"Colunas obrigatórias ausentes: {faltantes}")


class DadosVaziosError(PipelineError):
    """Levantada quando um estágio produz um DataFrame sem registros."""

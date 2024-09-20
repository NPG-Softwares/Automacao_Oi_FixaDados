class FaturaInfo:
    def __init__(self):
        self.files: list
        self.AnoReferencia: str
        self.ArquivoAzurePdf: str
        self.ArquivoAzureDigital: str
        self.CodigoBarra: str
        self.CodigoPagamento: str
        self.ContaId: int
        self.CicloInicio: str
        self.CicloFim: str
        self.ClienteId: int
        self.DownloadArquivo: str
        self.Emissao: str
        self.DownloadArquivoCliente: str
        self.FornecedorClasseId: int
        self.FornecedorId: int
        self.Id: int
        self.Lancamento: str
        self.Liberacao: str
        self.LoginId: int
        self.MedicaoString: str
        self.MesReferencia: str
        self.NomeArquivoDigital: str
        self.NomeArquivoPdf: str
        self.NumeroConta: str
        self.ProcessamentoArquivo: str
        self.ValorDocumentoDigital: float
        self.Vencimento: str
        self.Status: str
        self.TipoContaId: int
        self.Protocolo: str
        self.UnidadeId: int
        self.ValorDocumentoPDF: float

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(f'FaturaInfo(conta={self.NumeroConta})')

    def get_dict(self) -> dict:
        return self.__dict__

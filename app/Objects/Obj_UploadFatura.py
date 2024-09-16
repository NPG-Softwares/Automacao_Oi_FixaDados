class FaturaInfo:
    def __init__(self):
        self.files: list
        self.FornecedorId: int
        self.ValorDocumentoPDF: float
        self.Liberacao: str
        self.LoginId: int
        self.NomeArquivoDigital: str
        self.DownloadArquivo: str
        self.CicloInicio: str
        self.ValorDocumentoDigital: float
        self.UnidadeId: int
        self.CodigoBarra: str
        self.CodigoPagamento: str
        self.ContaId: int
        self.CicloFim: str
        self.Vencimento: str
        self.FornecedorClasseId: int
        self.MesReferencia: str
        self.ProcessamentoArquivo: str
        self.Emissao: str
        self.ArquivoAzurePdf: str
        self.Status: str
        self.NumeroConta: str
        self.AnoReferencia: str
        self.MedicaoString: str
        self.ClienteId: int
        self.DownloadArquivoCliente: str
        self.TipoContaId: int
        self.ArquivoAzureDigital: str
        self.Protocolo: str
        self.Lancamento: str
        self.Id: int
        self.NomeArquivoPdf: str

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def get_dict(self) -> dict:
        return self.__dict__

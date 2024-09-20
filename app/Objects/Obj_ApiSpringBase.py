class BaseClient:
    def __init__(self, data: dict) -> None:
        self.id = data.get("id")
        self.status = data.get("status")
        self.cliente_id = data.get("clienteId")
        self.fornecedor_classe_id = data.get("fornecedorClasseId")
        self.unidade_id = data.get("unidadeId")
        self.fornecedor_id = data.get("fornecedorId")
        self.cnpj_login = data.get("cnpjLogin")
        self.cpf_gestor = data.get("cpfGestor")
        self.email_gestor = data.get("emailGestor")
        self.senha = data.get("senha").strip()
        self.login = data.get("login").strip()
        self.fatura_enviada_por_email = data.get("faturaEnviadaPorEmail")
        self.email_recebimento_fatura = data.get("emailRecebimentoFatura")
        self.dia_verificacao = data.get("diaVerificacao")
        self.nome_configuracao = data.get("nomeConfiguracao")
        self.observacao = data.get("observacao")
        self.contas: list[BaseInvoice] = []  # Empty list for potential future use

    def __repr__(self) -> str:
        return f"BaseClient(ControleDownloadId={self.id}, ClienteId={self.cliente_id}, status={self.status})"


class BaseInvoice:
    def __init__(self, data: dict) -> None:
        self.status = data.get("status")
        self.numero_conta = data.get("numeroConta")
        self.tipo_conta_id = data.get("tipoContaId")
        self.codigo_fornecedor = data.get("codigoFornecedor")
        self.fornecedor_classe_id = data.get("fornecedorClasseId")
        self.fornecedor_id = data.get("fornecedorId")
        self.conta_id = data.get("contaId")
        self.arquivo_azure_digital = data.get("arquivoAzureDigital")
        self.vencimento = data.get("vencimento")
        self.cliente_id = data.get("clienteId")
        self.unidade_id = data.get("unidadeId")
        self.id = data.get("id")
        self.login_id = data.get("loginId")

    def __repr__(self) -> str:
        return f"BaseInvoice(conta={self.numero_conta}, contaId={self.conta_id}, status={self.status})"

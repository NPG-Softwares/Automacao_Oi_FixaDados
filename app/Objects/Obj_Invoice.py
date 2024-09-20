import pandas as pd


class Invoice:
    def __init__(self,
                 conta=None,
                 fatura=None,
                 valor=None,
                 emissao=None,
                 vencimento=None,
                 arquivo=None,
                 designacao=None,
                 mesref=None,
                 ) -> None:

        self.conta = conta
        self.fatura = fatura
        self.valor = valor
        self.emissao = emissao
        self.vencimento = vencimento
        self.arquivo = arquivo
        self.designacao = designacao
        self.mesref = mesref
        self.inicio_periodo = None
        self.fim_periodo = None
        self.boleto = None

    def __str__(self) -> str:
        atributos = []
        for atributo, valor in self.__dict__.items():
            atributos.append(f'{atributo} = {valor}')
        return '\n'.join(atributos)

    def create_dataframe(self):
        data = {key: [value] for key, value in self.__dict__.items()}
        return pd.DataFrame.from_dict(data)

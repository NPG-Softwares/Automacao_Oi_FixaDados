import os
import dotenv
import requests as req
from typing import Literal
from functools import cache
from datetime import datetime as dt
from datetime import timedelta as td

from Objects.Obj_ApiSpringBase import BaseClient, BaseInvoice

dotenv.load_dotenv()


# ------------------------------------------------- Exceções
class AmbientError(Exception):
    pass


class LoginError(Exception):
    pass


# ------------------------------------------------- Classes
class API_Spring:
    _token = {}

    def __init__(self, ambient: Literal['prod', 'hml']) -> None:
        self.ambient = ambient
        self.__get_envs__()

        if API_Spring._token.get(self.ambient):
            self.token = API_Spring._token.get(self.ambient)

        else:
            self.token = API_Spring._token.get(self.ambient) or self.get_token()
            API_Spring._token.setdefault(self.ambient, self.token)

    def __get_envs__(self) -> None:
        if self.ambient == 'hml':
            self.email = os.getenv('hml_login_email')
            self.password = os.getenv('hml_login_password')
            self.end_token = os.getenv('hml_end_get_token')
            self.end_logins = os.getenv('hml_end_logins')
            self.end_get_invoices = os.getenv('hml_end_get_invoices')
            self.end_up_invoice = os.getenv('hml_end_up_invoice')
            self.end_get_fornecedores_id = os.getenv('hml_end_get_fornecedores_id')

        elif self.ambient == 'prod':
            self.email = os.getenv('prod_login_email')
            self.password = os.getenv('prod_login_password')
            self.end_token = os.getenv('prod_end_get_token')
            self.end_logins = os.getenv('prod_end_logins')
            self.end_up_invoice = os.getenv('prod_end_up_invoice')
            self.end_get_invoices = os.getenv('prod_end_get_invoices')
            self.end_get_fornecedores_id = os.getenv('prod_end_get_fornecedores_id')

        else:
            raise AmbientError('Ambiente inválido, utilize os ambientes '
                               '[hml | prod] sendo "hml" (homologação) ou '
                               '"prod" (produção).')

    def get_logins(self, fornecedor_id: str = None) -> dict:
        url = self.end_logins
        headers = {}
        headers['Authorization'] = self.token

        params = {}

        if fornecedor_id:
            params['fornecedorId'] = fornecedor_id

        r = req.get(url, headers=headers, params=params)

        return r.json()

    def get_fornecedores_by_name(self, name: str) -> list:
        url = self.end_get_fornecedores_id
        headers = {}
        headers['Authorization'] = self.token

        params = {}
        params['NomeFantasia'] = name

        r = req.get(url, headers=headers, params=params)

        return [x['id'] for x in r.json()['data']]

    @cache
    def get_token(self) -> str:
        """
        Retrieves the bearer token for the specified email and password.

        Args:
            self (API_Spring): The API_Spring instance.

        Returns:
            str: The bearer token.

        Raises:
            LoginError: If there was an error during the login process.
        """

        r = req.post(self.end_token, json={
            'email': self.email,
            'password': self.password
        })

        if r.status_code == 200:
            return "Bearer " + r.json()['token']
        else:
            raise LoginError(f'Erro [{r.status_code}]: {r.text}')

    def get_accounts(self, client: BaseClient) -> dict:
        now = dt.now()
        url = self.end_get_invoices
        headers = {}
        headers['Authorization'] = self.token
        headers['Status'] = 'PENDENTE'

        params = {}
        params['clientId'] = client.cliente_id
        params['fornecedorId'] = client.fornecedor_id
        params['vencimentoMinimo'] = now.strftime('%Y-%m-%d')
        params['vencimentoMaximo'] = (now + td(days=60)).strftime('%Y-%m-%d')

        r = req.get(url, headers=headers, params=params)

        return r.json()

    def up_invoice(self, payload: dict, files: list[tuple]) -> None:
        """
        Uploads an invoice to the API using the provided payload and files.

        Args:
            payload (dict): The payload containing the invoice data.
            files (dict): The files to be uploaded along with the invoice.

        Raises:
            TypeError: If an invalid or unknown file type is found.
            req.exceptions.ContentDecodingError: If a file is too large to be sent.
            req.exceptions.RequestException: If there is an error during the upload process.
        """
        url = self.end_up_invoice
        headers = {}
        headers['Authorization'] = self.token

        for file in files:
            f = {'files': file}
            temp_payload = payload.copy()

            if file[0] == temp_payload['ArquivoAzurePdf']:
                temp_payload['ArquivoAzureDigital'] = None
                temp_payload['NomeArquivoDigital'] = None
            else:
                temp_payload['ArquivoAzurePdf'] = None
                temp_payload['NomeArquivoPdf'] = None

            r = req.post(url, headers=headers, data=temp_payload, files=f)

            if r.status_code == 200:
                print(f'Arquivo {f.get("files")[0]} enviado com sucesso.')
            elif r.status_code == 413:
                raise req.exceptions.ContentDecodingError(f'{file[0]}: Arquivo muito grande para ser enviado.')
            elif r.status_code != 200:
                raise req.exceptions.RequestException(f'Erro [{r.status_code}]: {r.text}')
        print('Fatura enviada com sucesso.')


def filter_logins(api: API_Spring, logins: dict) -> list[BaseClient]:
    filtered_accounts: list[str] = []
    filtered_logins: list[BaseClient] = []

    assert len(logins) > 0, 'Nenhum login encontrado.'
    for login in logins:

        if login['login'] == '' or login['login'] is None:
            continue

        if login['senha'] == '' or login['senha'] is None:
            continue

        if login['login'] in ['00000000000', '000.000.000.00']:
            continue

        client = BaseClient(login)
        accounts = api.get_accounts(client)['data']

        for account in accounts:
            obj_account = BaseInvoice(account)
            if obj_account.numero_conta in filtered_accounts:
                continue

            client.contas.append(obj_account)
            filtered_accounts.append(obj_account.numero_conta)

        filtered_logins.append(client)

    return filtered_logins


def get_logins(name: str, ambient: Literal['prod', 'hml'] = 'prod') -> list[BaseClient]:
    """
    Retrieves all logins for the given ambient (environment) and filters out
    invalid logins.

    Args:
        ambient (Literal['prod', 'hml'], optional): The ambient to retrieve
            logins from. Defaults to 'prod'.

    Returns:
        list: A list of filtered logins.
    """

    api = API_Spring(ambient)
    fornecedores_ids = api.get_fornecedores_by_name(name)
    logins = []
    for fornecedor_id in fornecedores_ids:
        logins += api.get_logins(fornecedor_id)['data']

    logins = filter_logins(api, logins)
    return logins


if __name__ == '__main__':
    get_logins('hml')

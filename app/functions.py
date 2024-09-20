import os
import locale
import pandas as pd

from datetime import datetime as dt
from datetime import timedelta as td
from tempfile import TemporaryDirectory

from Objects.Obj_ApiSpringBase import BaseClient

from Automations.Download_OI_Files import down_oi, get_drivers, do_auth
from Objects.Obj_ApiSpring import API_Spring
from Objects.Obj_UploadFatura import FaturaInfo
from Readers.Leitor_Boleto_OI import ler_boleto_oi
from Readers.Leitor_Detalhamentos_OI import leitor_detalhamento_oi

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def Oi_Process(login: BaseClient, oi_path: str | TemporaryDirectory):
    now = dt.now()

    init_date = (dt(now.year, now.month, 1))
    match now.month:
        case 12:
            final_date = dt(now.year + 1, 2, 1) - td(1)
        case 11:
            final_date = dt(now.year + 1, 1, 1) - td(1)
        case _:
            final_date = dt(now.year, now.month + 2, 1) - td(1)

    os.chdir(os.path.dirname(__file__))

    # Abaixa o datalhamento das faturas OI
    driver, webdriver = get_drivers(oi_path)

    print('Logando na OI...')
    do_auth(driver, webdriver, login)
    print('Logado!')

    print('Baixando PDFs...')
    down_oi(driver, webdriver, oi_path, init_date, final_date, 'PDF')

    print('Baixando detalhamentos...')
    down_oi(driver, webdriver, oi_path, init_date, final_date, 'CSV')

    webdriver.quit()

    print('Lendo boletos Oi')
    df_invoices = ler_boleto_oi(os.path.join(oi_path, "PDF"))

    print('Lendo detalhamentos Oi')
    main_df = leitor_detalhamento_oi(os.path.join(oi_path, "CSV"), df_invoices)

    main_df = tratar_df(main_df)

    faturas = criar_fatura(main_df, login)

    print('Subindo faturas no SC...')
    try:
        upload_fatura(faturas)
    except Exception as e:
        raise e
    finally:
        for _, files in faturas:
            for file in files:
                file[1].close()

    print('Finalizado!')


def tratar_df(df: pd.DataFrame):
    filtrar_colunas = [
        'FATURA', 'VALOR_DET', 'FILE_DET', 'CONTA',
        'VALOR_PDF', 'EMISSAO', 'VENCIMENTO', 'ARQUIVO',
        'MESREF', 'FULL_PATH_FILE_PDF', 'FULL_PATH_FILE_DET',
        'INICIO_PERIODO', 'FIM_PERIODO', 'BOLETO', 'TIPO_LEITURA'
    ]

    df = df[filtrar_colunas]
    filtrar_colunas.remove('VALOR_DET')
    df.loc[:, 'VALOR_PDF'] = pd.to_numeric(df['VALOR_PDF'].str.replace('.', '').str.replace(',', '.'))

    non_related_df = df[df['VALOR_DET'] == 'nan']
    if not non_related_df.empty:
        print(f'\033[1;33m{non_related_df.shape[0]} linhas sem detalhamento\033[m')
        print(non_related_df)
        df = df[df['FILE_DET'] != 'nan']

    df.loc[:, 'VALOR_DET'] = pd.to_numeric(df['VALOR_DET'])
    df = df.groupby(filtrar_colunas).sum().reset_index()
    return df


def criar_fatura(df: pd.DataFrame, login: BaseClient) -> list[tuple[FaturaInfo, list[tuple]]]:
    def formatar_data(data: str, input_format='%d/%m/%Y', output_format='%Y-%m-%d'):
        if data is None or data == '' or data.lower() == 'none':
            return None

        return dt.strptime(data.lower(), input_format).strftime(output_format)

    def limpar_texto(texto):
        ignore_chars = ['.', ',', ' ', '-', '/']
        texto = "".join([char for char in texto if char not in ignore_chars])
        return texto

    faturas = []

    for _, row in df.iterrows():
        acc = None
        for conta in login.contas:
            if limpar_texto(row['CONTA']) == limpar_texto(conta.numero_conta):
                acc = conta
                print('Conta localizada:', acc)

        if not acc:
            continue

        inv = FaturaInfo()
        now = dt.now()

        num_conta = limpar_texto(acc.numero_conta)
        format_det = row["FILE_DET"].lower().split(".")[-1]

        nome_arquivo_pdf = f'OI_{formatar_data(row["VENCIMENTO"], output_format="%d%m%y")}_{num_conta}.pdf'
        nome_arquivo_digital = f'OI_{formatar_data(row["VENCIMENTO"], output_format="%d%m%y")}_{num_conta}.{format_det}'

        try:
            inv.CicloInicio = formatar_data(row['INICIO_PERIODO'], input_format='%d/%m/%Y')
            inv.CicloFim = formatar_data(row['FIM_PERIODO'], input_format='%d/%m/%Y')
        except ValueError:
            inv.CicloInicio = formatar_data(row['INICIO_PERIODO'], input_format='%d/%m/%y')
            inv.CicloFim = formatar_data(row['FIM_PERIODO'], input_format='%d/%m/%y')

        inv.AnoReferencia = formatar_data(row['MESREF'], input_format='%b-%Y', output_format='%Y')
        inv.ArquivoAzurePdf = nome_arquivo_pdf
        inv.ArquivoAzureDigital = nome_arquivo_digital
        inv.CodigoBarra = row['BOLETO']
        inv.ContaId = acc.conta_id
        inv.ClienteId = acc.cliente_id
        inv.DownloadArquivo = now.strftime('%Y-%m-%dT%H:%M:%S')
        inv.Emissao = formatar_data(row['EMISSAO'])
        inv.DownloadArquivoCliente = now.strftime('%Y-%m-%dT%H:%M:%S')
        inv.FornecedorClasseId = acc.fornecedor_classe_id if acc.fornecedor_classe_id else login.fornecedor_classe_id
        inv.FornecedorId = acc.fornecedor_id
        inv.LoginId = 1
        inv.MesReferencia = formatar_data(row['MESREF'], input_format='%b-%Y', output_format='%m')
        inv.NomeArquivoDigital = nome_arquivo_digital
        inv.NomeArquivoPdf = nome_arquivo_pdf
        inv.NumeroConta = acc.numero_conta
        inv.ValorDocumentoDigital = row['VALOR_DET']
        inv.ValorDocumentoPDF = row['VALOR_PDF']
        inv.Vencimento = formatar_data(row['VENCIMENTO'])
        inv.Status = 'PENDENTE'
        inv.TipoContaId = acc.tipo_conta_id
        inv.UnidadeId = acc.unidade_id

        # 'files': (fat_name, byte_file, 'application/pdf')
        file_pdf = (nome_arquivo_pdf, open(row['FULL_PATH_FILE_PDF'], 'rb'), 'application/pdf')

        type_det = 'text/plain' if format_det == 'txt' else 'text/csv'
        file_det = (nome_arquivo_digital, open(row['FULL_PATH_FILE_DET'], 'rb'), type_det)

        files = [file_pdf, file_det]

        faturas.append((inv, files))

    return faturas


def upload_fatura(faturas: list[tuple[FaturaInfo, list[tuple]]]) -> None:
    api = API_Spring('hml')
    for fatura, files in faturas:
        payload = fatura.__dict__

        api.up_invoice(payload, files)

# <-- encoding: utf-8 -->
"""
Este arquivo é responsável por ler os arquivos de detalhamentos
das faturas de telefonia da Oi.

Args:

Raises:
    AttributeError: Acontece quando o tipo do detalhamento não é reconhecido

Returns:
    Cria um arquivo .csv com os dados de faturas detalhadas.
    """

import locale
import os
import re
from datetime import datetime as dt
from datetime import timedelta as td

import pandas as pd

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def __reader_1__(df: pd.DataFrame) -> pd.DataFrame:
    df = df[[
        'FATURA',
        'FONE-ORIG',
        'VALOR',
        'BLOCO'
    ]]

    df = df.rename(columns={
        'FONE-ORIG': 'ORIGEM',
        'BLOCO': 'DESCRICAO',
    })

    return df


def __reader_2__(df: pd.DataFrame) -> pd.DataFrame:
    df = df[[
        'FATURA',
        'Nº Origem',
        'Valor (R$)',
        'Descrição'
    ]]

    df = df.rename(columns={
        'Nº Origem': 'ORIGEM',
        'Valor (R$)': 'VALOR',
        'Descrição': 'DESCRICAO',
    })

    return df


def __reader_3__(df: pd.DataFrame) -> pd.DataFrame:
    df = df[[
        'NUMERO DA FATURA',
        'TELEFONE',
        'VALOR BRUTO',
        'DESCRICAO DO SERVICO'
    ]]

    df = df.rename(columns={
        'NUMERO DA FATURA': 'FATURA',
        'TELEFONE': 'ORIGEM',
        'VALOR BRUTO': 'VALOR',
        'DESCRICAO DO SERVICO': 'DESCRICAO',
    })

    return df


def __encontrar_correspondencia__(valor, lista_valores):
    for item in lista_valores:
        if re.search(valor, item):
            return True
    return False


def __preencher_correspondencia__(valor, lista_valores):
    for item in lista_valores:
        if valor in item:
            return item

    return False


def read_files(details_path: str) -> pd.DataFrame:
    """
    Lê os arquivos da pasta details_path, processa as colunas importante
    e retorna um dataframe Pandas com as informações

    Args:
        details_path (str): Pasta onde se encontra os detalhamentos

    Raises:
        AttributeError: Retorna um erro quando o arquivo não é reconhecido

    Returns:
        pd.DataFrame: Retorna um dataframe com as informações dos detalhamentos
    """
    df = pd.DataFrame()
    det_files = os.listdir(details_path)

    if len(det_files) == 0:
        raise FileNotFoundError(
            "Nenhum arquivo encontrado na pasta de detalhamentos")

    # Lê os arquivos
    for filename in det_files:
        # Ignora arquivos que não terminam em .csv e .txt
        f = os.path.join(details_path, filename)
        if (not filename.lower().endswith('.csv')
                and not filename.lower().endswith('.txt')):
            print('jump')
            continue

        # Cria um DF temporário lendo o pdf
        temp_df = pd.read_csv(f, sep=';', encoding='utf-8',
                              decimal=',', dtype=str)

        if filename.endswith('.TXT'):
            temp_df = __reader_1__(temp_df)

        elif 'DetalhamentoFaturaExcel' in filename:
            temp_df = __reader_2__(temp_df)

        elif 'Fatura_Excel' in filename:
            temp_df = __reader_3__(temp_df)

        else:
            print("Arquivo", f)
            raise AttributeError("Tipo de arquivo não reconhecido")

        if not temp_df.empty:
            temp_df['FATURA'] = temp_df['FATURA'].astype(str).str.strip()
            temp_df['ORIGEM'] = temp_df['ORIGEM'].astype(str).str.strip()
            temp_df['DESCRICAO'] = temp_df['DESCRICAO'].astype(str).str.strip()
            temp_df['VALOR'] = (temp_df['VALOR']
                                .str.replace(',', '.')
                                .astype(float))

            temp_df = temp_df.groupby(['FATURA', 'ORIGEM', 'DESCRICAO']).sum()
            temp_df = temp_df.reset_index()

            temp_df['FILE_DET'] = filename
            df = pd.concat([df, temp_df], ignore_index=True)

    return df


def concat_with_db() -> pd.DataFrame:
    worksheet = "HISTÓRICO V1.xlsx"
    worksheet_path = "Clientes/COMERCIAL/ICATU/GESTÃO/01 - ARQUIVOS MENSAIS"
    history_path_file = os.path.join(
        os.environ['OneDrive'],
        worksheet_path,
        worksheet
    )

    df_history = pd.read_excel(history_path_file, 'DESIGNAÇÕES (OPERADORA)')

    df_history_oi = df_history[df_history['OPERADORA'] == 'Oi']

    df_history_oi.loc[(df_history_oi['DESIGNAÇÃO'] != "-")
                      & (df_history_oi['OPERADORA'] == 'Oi'), 'DESIGNAÇÃO'] = (df_history_oi['DESIGNAÇÃO']
                                                                               .astype(str)
                                                                               .str.replace('-', '')
                                                                               .str.replace(' ', ''))

    df_history_oi

    # Encontrar correspondências aproximadas entre os DataFrames
    correspondencias = df_ordenado['ORIGEM'].apply(
        lambda x: encontrar_correspondencia(x, df_history_oi['DESIGNAÇÃO']))

    # Filtrar linhas onde não há correspondência
    df_com_correspondencia = df_ordenado[correspondencias]
    df_sem_correspondencia = df_ordenado[~correspondencias]

    df_relativo = df_com_correspondencia['ORIGEM'].apply(
        lambda x: preencher_correspondencia(x, df_history_oi['DESIGNAÇÃO']))

    df_com_correspondencia.loc[:, 'ORIGEM_FULL'] = df_relativo

    df_final = df_com_correspondencia.merge(df_history_oi,
                                            how='left',
                                            left_on='ORIGEM_FULL',
                                            right_on='DESIGNAÇÃO')

    df_final[df_final['ORIGEM_FULL'].isin(df_history_oi['DESIGNAÇÃO'])]

    df_final.to_csv('final.csv', sep=';', encoding='utf-8')


def leitor_detalhamento_oi(details_path: str,
                           df_invoices: pd.DataFrame) -> None:
    """
    Função principal onde é lido os detalhamentos, concatenado com as
    informações das faturas e no final é gerado um arquivo com essas
    informações.

    Args:
        details_path (str): Pasta onde se localiza os detalhamentos dos arquivos.
        df_invoices (pd.DataFrame): Dataframe com as informações das faturas
    """
    df = read_files(details_path=details_path)
    df = df.loc[df['VALOR'] != 0]

    # Transforma as colunas em uppercase
    df_invoices.columns = df_invoices.columns.map(str.upper)

    # Remove os '0' à esquerda das faturas, para prevenção de erros com nomes
    df_invoices['FATURA'] = df_invoices['FATURA'].str.lstrip('0')
    df['FATURA'] = df['FATURA'].str.lstrip('0')

    # Agrupa o df de detalhamento com o df das faturas lidas
    df = df.merge(df_invoices, how='right', on='FATURA',
                  suffixes=('_DET', '_PDF'))

    # Remove os espaçamentos em branco em todas as células
    df = df.map(lambda x: str(x).strip())

    # Ordena e filtra as colunas do dataframe
    df_ordenado = df[[
        "CONTA",
        "FATURA",
        "VALOR_PDF",
        "EMISSAO",
        "VENCIMENTO",
        "ARQUIVO",
        "MESREF",
        "OPERADORA",
        "CLIENTE",
        "DDD",
        "TIPO_LEITURA",
        "ORIGEM",
        "VALOR_DET",
        "DESCRICAO",
        "FILE_DET"]]

    df_ordenado.loc[:, 'VALOR_DET'] = (df_ordenado['VALOR_DET']
                                       .str.replace('.', ','))

    df_ordenado.to_excel('Logs/OI_DET.xlsx',
                         na_rep=None,
                         index=False)

    print('Detalhamento gerado com sucesso!')


if __name__ == '__main__':
    mesref = (dt.now() + td(10)).strftime('%Y-%m')
    details_path = os.path.join(os.environ['OneDrive'],
                                "Clientes/COMERCIAL/ICATU/GESTÃO/02 - AUTOMACOES/",
                                f"PARA TRATAR/{mesref}/OI/DETALHAMENTOS")

    df_invoices = fr"{os.environ['OneDrive']}\Publico\NYCOLAS\01 - PROJETOS\Automacao Spring Control\Logs\oi_files.csv"
    df_invoices = pd.read_csv(df_invoices,
                              sep=';',
                              encoding='utf-8',
                              dtype=str,
                              index=False,
                              )

    leitor_detalhamento_oi(details_path, df_invoices)

import os

from datetime import datetime as dt
from datetime import timedelta as td

try:
    from Automations.Download_OI_Files import down_oi
    from Readers.Leitor_Boleto_OI import ler_boleto_oi
    from Readers.Leitor_Detalhamentos_OI import leitor_detalhamento_oi
except ModuleNotFoundError as mnfe:
    os.system(f'python -m pip install {mnfe.name}')
    os.system(f'python "{__file__}"')
    quit()


def Oi_Process(mes: dt):
    mesref = mes.strftime('%Y-%m')
    oi_path = os.path.join(os.environ['OneDrive'],
                           "Clientes/COMERCIAL/ICATU/GESTÃO/02 - AUTOMACOES",
                           f"PARA TRATAR/OI/{mesref}")
    if not os.path.exists(oi_path):
        os.makedirs(oi_path)

    details_path = os.path.join(oi_path, "DETALHAMENTOS")
    if not os.path.exists(details_path):
        os.mkdir(details_path)

    init_date = (dt(mes.year, mes.month, 1))
    final_date = (dt(mes.year, mes.month + 1, 1) - td(1))

    os.chdir(os.path.dirname(__file__))

    # Abaixa o datalhamento das faturas OI
    print('\n|', '=' * 100, '|')
    print("Baixando detalhamentos da Oi...")
    down_oi(oi_path, init_date, final_date, 'PDF')
    down_oi(details_path, init_date, final_date, 'CSV')

    print('\n|', '=' * 100, '|')
    print("Lendo boletos baixados da Oi...")
    df_invoices = ler_boleto_oi(os.path.join(oi_path, "PDF"))

    # # #Lê o df e gera um arquivo com os detalhamentos
    print('\n|', '=' * 100, '|')
    print("Gerando detalhamento da Oi...")
    leitor_detalhamento_oi(os.path.join(details_path, "CSV"), df_invoices)

    print('\n|', '=' * 100, '|')
    print("Processo finalizado com sucesso!")


# Main function execution starts here
if __name__ == "__main__":
    meses: list[dt] = []
    today = (dt.now())
    meses.append(dt(2024, today.month, 1))
    # meses.append(dt(2024, today.month+1, 1))
    # meses.append(dt(2024, today.month+2, 1))

    for mes in meses:
        print(f"\n\nBaixando mês {mes.strftime('%m-%Y')}")
        Oi_Process(mes)

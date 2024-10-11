import re
import os
import locale
from datetime import datetime as dt


import pandas as pd

from Objects.Obj_Invoice import Invoice  # type: ignore
from Objects.Obj_PDF_Reader import PDFReader  # type: ignore


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def __read_format_1__(pdf_object: PDFReader, page_text: str,
                      invoice: Invoice) -> bool:
    """
    This function is used to extract information from a PDF file.

    Parameters:
    pdf_object (PDFReader): An object that contains the PDF file.
    page_text (str): The text of the PDF page.
    invoice (Invoice): An object that contains the invoice information.

    Returns:
    bool: A boolean value indicating whether the extraction was successful.

    """
    invoice.tipo_leitura = 1

    lines = page_text.split('\n')
    for i, line in enumerate(lines):
        # print(i, line.strip())

        if not invoice.emissao:
            if 'DATA DE EMISSAO' in line:
                invoice.emissao = lines[i + 1]

        if not invoice.mesref:
            if invoice.emissao:
                invoice.mesref = dt.strptime(invoice.emissao, '%d/%m/%Y')
                invoice.mesref = invoice.mesref.strftime("%b-%Y")

        if not invoice.conta:
            if 'TELEFONE/CONTRATO:' in line:
                invoice.conta = line.split()
                if len(invoice.conta) == 1:
                    invoice.conta = lines[i + 1]

                elif len(invoice.conta) == 2:
                    invoice.conta = invoice.conta[-1]

                else:
                    line = line + lines[i + 1]
                    invoice.conta = pdf_object.find_element(
                        line, '[0-9]+-[0-9]+', regex=True)

                    if not invoice.conta:
                        invoice.conta = pdf_object.find_element(
                            line, '[0-9]{7}', regex=True)

                    if not invoice.conta:
                        invoice.conta = pdf_object.find_element(
                            line, '[0-9]{8}', regex=True)

                    if not invoice.conta:
                        invoice.conta = pdf_object.find_element(
                            line, '[0-9]{10}', regex=True)

                    if isinstance(invoice.conta, list):
                        invoice.conta = invoice.conta[0]

                if invoice.conta == 'CONTA' or not invoice.conta:
                    raise ValueError('Conta não encontrada')

        if not invoice.fatura:
            if 'FATURA N' in line:
                invoice.fatura = line.split()[-1].strip()

        if not invoice.valor:
            if 'VALOR A PAGAR' in line:
                line = line + "\n" + lines[i + 1]
                invoice.valor = pdf_object.find_element(
                    line, '[0-9]*[.]?[0-9]+,[0-9]+', regex=True)
                if isinstance(invoice.valor, list):
                    if len(invoice.valor) > 0:
                        invoice.valor = invoice.valor[0]

        if not invoice.vencimento:
            if 'VENCIMENTO:' in line:
                invoice.vencimento = line.split()[-1]

        if not invoice.ddd:
            if 'CODIGO DDD' in line:
                invoice.ddd = lines[i + 1]

    return True


def __read_format_2__(pdf_object: PDFReader, page_text: str,
                      invoice: Invoice) -> bool:
    """
    This function is used to extract information from a PDF file.

    Parameters:
    pdf_object (PDFReader): An object that contains the PDF file.
    page_text (str): The text of the PDF page.
    invoice (Invoice): An object that contains the invoice information.

    Returns:
    bool: A boolean value indicating whether the extraction was successful.

    """
    invoice.tipo_leitura = 2

    lines = page_text.split('\n')
    for i, line in enumerate(lines):
        # print(i, line.strip())

        if not invoice.emissao:
            if 'Data de emissão' in line:
                invoice.emissao = pdf_object.find_element(
                    line,
                    'Data de emissão:'
                )

        if not invoice.mesref:
            if (rm_txt := 'Mês de referência:') in line:
                invoice.mesref = line.replace(rm_txt, '').strip()
                invoice.mesref = dt.strptime(invoice.mesref, '%B %Y')
                invoice.mesref = invoice.mesref.strftime("%b-%Y")

        if not invoice.mesref:
            if 'Referência' == line:
                invoice.mesref = lines[i + 1]
                invoice.mesref = dt.strptime(invoice.mesref, '%B/%Y')
                invoice.mesref = invoice.mesref.strftime("%b-%Y")

        if not invoice.conta:
            if (rm_txt := 'Contrato Agrupador:') in line:
                invoice.conta = line.replace(rm_txt, '').strip()

        if not invoice.fatura:
            if 'Fatura: ' in line:
                invoice.fatura = line.split()[-1].strip()

        if not invoice.valor:
            if 'Valor a pagar' in line:
                invoice.valor = lines[i + 1]

        if not invoice.vencimento:
            if 'Data de Vencimento' in line:
                invoice.vencimento = lines[i + 1]

    return True


def __read_format_3__(pdf_object: PDFReader, page_text: str,
                      invoice: Invoice) -> bool:
    """
    This function is used to extract information from a PDF file.

    Parameters:
    pdf_object (PDFReader): An object that contains the PDF file.
    page_text (str): The text of the PDF page.
    invoice (Invoice): An object that contains the invoice information.

    Returns:
    bool: A boolean value indicating whether the extraction was successful.

    """
    invoice.tipo_leitura = 3

    lines = page_text.split('\n')
    for i, line in enumerate(lines):
        pass
        # print(i, line.strip())

        if not invoice.emissao:
            if (rm_text := 'Emissão em ') in line:
                invoice.emissao = line.removeprefix(rm_text).strip()

        if not invoice.mesref:
            if 'FATURA DE' in line:
                invoice.mesref = lines[i + 2]
                invoice.mesref = dt.strptime(invoice.mesref, '%b/%Y')
                invoice.mesref = invoice.mesref.strftime("%b-%Y")

        if not invoice.conta:
            if (rm_txt := 'NÚMERO DO CLIENTE:') in line:
                invoice.conta = line.removeprefix(rm_txt).strip()

        if not invoice.fatura:
            if (rm_txt := 'NÚMERO DA FATURA:') in line:
                invoice.fatura = line.removeprefix(rm_txt).strip()

        if not invoice.valor:
            if 'PAGAR (R$)' in line:
                invoice.valor = lines[i + 1]

        if not invoice.vencimento:
            if 'VENCIMENTO' in line:
                invoice.vencimento = lines[i + 2]

        # if not invoice.servicos:
        #     if '' in line:
        #         invoice.servicos = lines[i+1]

    return True


def ler_boleto_oi(invoices_path):
    """
    This function is used to extract information from OI PDF files.

    Parameters:
    invoices_path (str): The path to the folder containing the PDF files.

    Returns:
    None: The function saves the extracted information to a CSV file.

    """
    files = os.listdir(invoices_path)

    main_df = pd.DataFrame()
    for f in files:
        if os.path.isdir(os.path.join(invoices_path, f)):
            continue

        if not f.endswith('.pdf'):
            continue

        print(f"Lendo o arquivo {f}...")
        obj_pdf = PDFReader(f, invoices_path)
        invoice = Invoice()

        # engine = "PyPDF2"  # PyPDF2 | fitz
        engine = "fitz"  # PyPDF2 | fitz
        pdf = obj_pdf.read_pdf(engine)

        invoice.operadora = "Oi"
        invoice.arquivo = f
        invoice.path = invoices_path
        invoice.full_path_file_pdf = os.path.join(invoices_path, f)
        invoice.ddd = None

        try:
            total_pages = (len(pdf.pages) if engine == "PyPDF2"
                           else pdf.page_count)
            all_pages_text = []
            for pag in range(total_pages):
                # print("Numero da página:", pag + 1)
                page: str = obj_pdf.get_text(pdf, pag)

                all_pages_text.append(page)

            full_text = '\n'.join(all_pages_text)

            cod_barras = re.findall(r'(?:\d{5,}[\s.-]?\d\s+){4}', full_text)
            invoice.boleto = ' '.join(cod_barras[0].split('\n')[0].split(' '))

            periodo = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]+ [aA] [0-9]{2}/[0-9]{2}/[0-9]+', full_text)
            if periodo:
                periodo = periodo[0].lower().split(' a ')
                invoice.inicio_periodo = periodo[0]
                invoice.fim_periodo = periodo[1]

            if 'contrato agrupador:' in full_text.lower():
                __read_format_2__(obj_pdf, full_text, invoice)

            elif 'VALOR REFERENTE A CONTA CUSTOMIZADA' in full_text or \
                    'PLANO LOCAL' in full_text or \
                    'TELEFONE/CONTRATO' in full_text:
                __read_format_1__(obj_pdf, full_text, invoice)

            elif 'CHEGOU SUA FATURA DA OI' in full_text or \
                    'EMPRESAS' in full_text:
                __read_format_3__(obj_pdf, full_text, invoice)

            else:
                print(full_text)
                raise TypeError("Tipo de PDF não reconhecido, "
                                "por favor revisar o PDF")

        except Exception as e:
            raise e
        else:
            main_df = pd.concat([main_df, invoice.create_dataframe()])
        finally:
            obj_pdf.close_pdf()

    main_df['valor'] = main_df['valor'].str.removeprefix('R$ ')
    main_df.reset_index(drop=True, inplace=True)

    return main_df


if __name__ == '__main__':
    invoices_path = fr"{os.environ['OneDrive']}\Clientes\COMERCIAL\ICATU"\
        r"\GESTÃO\02 - AUTOMACOES\PARA TRATAR\2024-05\OI"

    ler_boleto_oi(invoices_path)

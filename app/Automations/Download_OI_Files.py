import os

from zipfile import ZipFile
from datetime import datetime as dt
from datetime import timedelta as td

from Objects.Obj_ApiSpring import LoginError
from Objects.Obj_ApiSpringBase import BaseClient
from Objects.Obj_WebAutomation import Driver, WebDriver, sleep


def mount_url(url_base: str, **kwargs) -> tuple[str, list]:
    """
    Monta a URL com os argumentos.

    Args:
        url_base: A URL base que será concatenada com os argumentos.
        kwargs: Parâmetros a serem concatenados à URL.

    Returns:
        A URL montada e uma lista com os argumentos utilizados.

    """
    args = ""
    for key, value in kwargs.items():
        if isinstance(value, list):
            args += "".join(f"&{key}={item_value}" for item_value in value)
        else:
            args += f"&{key}={value}"

    args = args.removeprefix("&")
    return url_base + args, args.split("&")


def _validacao_url(webdriver, oi_url, url_args) -> None:
    """
    Validação de URL

    Args:
        webdriver: The webdriver object.
        oi_url: The URL to validate.

    Returns:
        None
    """
    # Validação de URL
    while not all(arg in webdriver.current_url for arg in url_args):
        # print([(arg, arg in webdriver.current_url) for arg in url_args])
        sleep(5)
        print("Aplicando filtros novamente...")
        webdriver.get(oi_url)


def _verify_download(download_folder) -> None:
    """
    Verify the completion of a download by checking the presence of temporary or partially downloaded files in the specified download folder.

    Args:
        download_folder (str): The path to the folder where the download is being made.

    Returns:
        None: This function does not return anything. It prints a success message once the download is complete.
    """
    now = dt.now()
    limit = now + td(minutes=3)

    while any((f.endswith(('.crdownload', '.tmp')))
              for f in os.listdir(download_folder)):
        if now >= limit:
            raise TimeoutError("Download inválido")

        sleep(2)

    while not any(f.endswith('.zip')
                  for f in os.listdir(download_folder)):
        if now >= limit:
            raise TimeoutError("Download inválido")
        sleep(2)

    print("Download realizado com sucesso!")


def _extract_files(download_folder: str, format_exit: str) -> None:
    """
    Extracts the contents of a ZIP file in the specified download folder.

    Args:
        download_folder (str): The path to the folder where the ZIP file is located.
        format_exit (str): The format of the extracted files.

    Returns:
        None: This function does not return anything. It prints a success message once the extraction is complete.

    """
    for f in os.listdir(download_folder):
        if f.endswith(".zip"):
            print(f"Arquivo ZIP encontrado: {f}")
            with ZipFile(os.path.join(download_folder, f), "r") as zip_ref:
                new_folder = os.path.join(download_folder, format_exit)
                if not os.path.exists(new_folder):
                    os.mkdir(new_folder)

                zip_ref.extractall(new_folder)

            # remove zip file
            os.remove(os.path.join(download_folder, f))


def _verify_do_auth(driver: Driver, webdriver: WebDriver) -> None:
    sleep(3)
    try:
        warning = driver.find_by_element(webdriver, '//p[@id="aviso_info"]').text
    except Exception:
        return

    if warning and warning != '':
        raise LoginError(f'Login inválido: {warning}')


def get_drivers(download_folder: str) -> tuple[Driver, WebDriver]:
    driver = Driver(download_folder=download_folder)

    safe_sites = ["https://portaloisolucoes.oi.com.br/"]
    webdriver = driver.new_driver(no_window=True, safe_sites=safe_sites)

    return driver, webdriver


def do_auth(driver: Driver, webdriver: WebDriver, login: BaseClient) -> None:
    webdriver.get('https://autenticacao.oi.com.br/nidp/saml2/sso?id=PortalOIContractCorp&sid=0&option=credential&sid=0')

    driver.find_by_element(
        webdriver,
        '//*[@id="usernameinput"]',
        wait=3).send_keys(login.login)

    driver.find_by_element(
        webdriver,
        '//*[@id="passwordinput"]',
        wait=3).send_keys(login.senha)

    driver.click_by_element(webdriver, '//*[@id="loginButtonApp"]', wait=3)

    _verify_do_auth(driver, webdriver)


def down_oi(driver: Driver, webdriver: WebDriver,
            download_folder, init_date: dt, final_date: dt, tipo_arquivo: str):
    base_url = 'https://portaloisolucoes.oi.com.br/todas-as-contas?'
    limit = 30
    offset = 0
    payment_status = ['em_aberto', 'sem_status', 'pago', 'cancelado']

    document_type = [
        'Invoice',
        # 'InvoiceExtract',
        # 'AdjustedInvoice'
    ]  # warning: Primeira letra maiúscula

    inicio = init_date.strftime("%Y-%m-%dT00:00:00.%fZ").replace(':', '%3A')
    fim = final_date.strftime("%Y-%m-%dT23:59:59.%fZ").replace(':', '%3A')

    oi_url, url_args = mount_url(
        base_url,
        limit=limit,
        offset=offset,
        paymentStatus=payment_status,
        documentType=document_type,
        dueDateStart=inicio,
        dueDateEnd=fim)

    sleep(5)
    webdriver.get(oi_url)

    _validacao_url(webdriver, oi_url, url_args)

    next_page_btn = driver.find_by_element(
        webdriver,
        '//*[@id="application"]/div/div/main/div[2]/div[5]/div/div/div[2]/div/div/div/div[3]/button',
        wait=10)

    while True:
        try:
            driver.click_by_element(webdriver,
                                    '//table/thead/tr/th/input[@type="checkbox"]',
                                    wait=20)

        except Exception:
            sleep(5)
            driver.click_by_element(webdriver,
                                    '//table/thead/tr/th/input[@type="checkbox"]',
                                    wait=20)

        if 'disabled' not in webdriver.execute_script(
                'return arguments[0].getAttributeNames()', next_page_btn):
            next_page_btn.click()
            sleep(5)
        else:
            break

    driver.click_by_element(webdriver,
                            '//button[@data-context="btn_baixar_barra_modal"]',
                            wait=5)

    driver.click_by_element(webdriver,
                            f'//label[contains(text(), "{tipo_arquivo}")]',
                            wait=10)

    driver.click_by_element(
        webdriver,
        '//button[@data-context="btn_baixar"]'
    )

    driver.click_by_element(webdriver,
                            '//button[text() = "Ver downloads"]',
                            wait=10)

    file_down_xpath = ('//tr[1][td/a[@title="Baixar arquivo"]'
                       f' and td[2][contains(text(), "{tipo_arquivo}")]'
                       ' and td[5]/p[text()="Disponível"]]/td/a')

    i = 0
    tries = 15
    print('Esperando o download do arquivo...')
    while True:
        try:
            print(f'{i+1} de {tries}', end='... ')
            driver.click_by_element(webdriver,
                                    file_down_xpath)
            print("Arquivo concluído com sucesso")
            break

        except BaseException:
            if i < tries:
                sleep(5)
                i += 1
            else:
                raise FileNotFoundError('Arquivo não processado corretamente')

    _verify_download(download_folder)

    _extract_files(download_folder, format_exit=tipo_arquivo)

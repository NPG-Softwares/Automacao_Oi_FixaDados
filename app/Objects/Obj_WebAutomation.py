import os
import platform
from time import sleep, time

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        ElementNotSelectableException,
                                        ElementNotVisibleException,
                                        JavascriptException)
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

xpath = By.XPATH
id_selector = By.ID
name_selector = By.NAME
tag_selector = By.TAG_NAME
css_selector = By.CSS_SELECTOR
class_selector = By.CLASS_NAME


class FolderNotExistsError(Exception):
    pass


class Driver:
    """Classe criada para automatizar o download das faturas web"""

    def __init__(self, download_folder: str = None):
        """
        Initializes a new instance of the `Driver` class.

        Args:
            operadora (str, optional): The operator. Defaults to None.
            cliente (str, optional): The client. Defaults to None.
            client_folder (str, optional): The client folder. Defaults to None.
            download_folder (str, optional): The download folder. Defaults to None.

        Raises:
            FolderNotExistsError: If the specified download folder does not exist.

        Notes:
            - If a download folder is specified, it is checked for existence.
            - The download folder path is normalized to ensure compatibility with Selenium.
            - The download folder path is stored as a private attribute `__download_folder__`.
        """

        if download_folder:
            if not os.path.exists(download_folder):
                raise FolderNotExistsError(
                    f"O diretório {download_folder} não existe")

            self.__download_folder__ = download_folder

    def __options__(self, no_window: bool = False,
                    arguments: list = [], safe_sites: list = []):
        """
        Returns a ChromeOptions object with the specified options.

        Args:
            no_window (bool, optional): If True, the webdriver will run in headless mode. Defaults to False.
            arguments (list, optional): A list of additional arguments to be added to the ChromeOptions object. Defaults to an empty list.
            safe_sites (list, optional): A list of safe sites to configure WebDriver security options. Defaults to an empty list.

        Returns:
            ChromeOptions: A ChromeOptions object with the specified options.
        """

        webdriver_options = ChromeOptions()
        webdriver_options.add_argument('--log-level=3')
        webdriver_options.add_argument("--start-maximized")
        webdriver_options.add_argument('--ignore-ssl-errors')
        webdriver_options.add_argument('--ignore-certificate-errors')
        webdriver_options.add_argument('--allow-insecure-localhost')
        webdriver_options.add_argument('--allow-running-insecure-content')

        print('Download folder:', self.__download_folder__)
        prefs_args = {
            "plugins.always_open_pdf_externally": True,  # Garante que o PDF será baixado
            "download.prompt_for_download": "false",
            "download.directory_upgrade": "true",
            "download.default_directory": self.__download_folder__,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1
        }

        webdriver_options.add_experimental_option('prefs', prefs_args)

        if no_window:
            webdriver_options.add_argument('--headless')
            webdriver_options.add_argument('--no-sandbox')
            webdriver_options.add_argument('--disable-gpu')
            webdriver_options.add_argument('--disable-dev-shm-usage')
            webdriver_options.add_argument('--window-size=1420,1080')
            webdriver_options.add_argument("--disable-features=VizDisplayCompositor")

        if arguments != []:
            for arg in arguments:
                webdriver_options.add_argument(arg)

        if safe_sites != []:
            sites = ','.join(safe_sites)
            webdriver_options.add_argument(f'--unsafely-treat-insecure-origin-as-secure={sites}')  # noqa
            webdriver_options.add_argument(f'--unsafely-allow-protected-media-identifier-dor-domain={sites}')  # noqa

        return webdriver_options

    def new_driver(self, no_window: bool = False,
                   safe_sites: list = []) -> WebDriver:
        """
        Creates a new WebDriver instance and returns it.

        Args:
            self: The object instance.
            no_window (bool): Flag to indicate if the WebDriver should run in headless mode. Default is False.
            safe_sites (list): List of safe sites to configure WebDriver security options. Default is an empty list.

        Returns:
            WebDriver: A new WebDriver instance based on the specified options.
        """
        match platform.system():
            case 'Windows':
                service = Service('chromedriver.exe')
            case 'Linux':
                service = Service('/usr/local/bin/chromedriver')
            case _:
                service = Service()

        return Chrome(service=service,
                      options=self.__options__(no_window=no_window, safe_sites=safe_sites))

    def find_by_element(self,
                        driver: WebDriver,
                        element: str,
                        selector: str = xpath,
                        wait: float = None,
                        multiple: bool = False) -> WebElement | list[WebElement]:  # noqa
        """
        Finds an element on a web page using the provided driver, element, selector, wait, and multiple flags.

        Args:
            driver (Chrome): The Selenium Chrome driver used to interact with the web page.
            element (str): The element to find on the web page.
            selector (str, optional): The selector method to use for finding the element. Defaults to xpath.
            wait (float, optional): The amount of time to wait for the element to be present on the web page. Defaults to None.
            multiple (bool, optional): Flag indicating whether to find multiple elements matching the selector. Defaults to False.

        Returns:
            WebElement | list[WebElement]: If multiple is True, returns a list of WebElements matching the selector. Otherwise, returns a single WebElement.

        Raises:
            Exception: If an error occurs while finding the element.
        """

        try:
            if wait:
                wait_func = WebDriverWait(driver,
                                          timeout=wait,
                                          poll_frequency=1,
                                          ignored_exceptions=[
                                              ElementNotVisibleException,
                                              ElementNotSelectableException,
                                              ElementNotInteractableException,
                                              ElementClickInterceptedException,
                                          ])

                return wait_func.until(EC.presence_of_element_located((
                    selector, element)))
            if multiple:
                return driver.find_elements(xpath, element)
            else:
                return driver.find_element(xpath, element)
        except Exception as e:
            raise e

    def click_by_element(self,
                         driver: WebDriver,
                         x_path: str,
                         selector: str = xpath,
                         wait=None,
                         use_js: bool = True) -> WebElement:
        """
        Clicks on an element identified by its XPath using Selenium WebDriver.

        Args:
            driver (WebDriver): The Selenium WebDriver instance.
            x_path (str): The XPath expression to locate the element.
            selector (str, optional): The selector method to use. Defaults to xpath.
            wait (int, optional): The time to wait for the element to be clickable. Defaults to None.
            use_js (bool, optional): Whether to use JavaScript to click the element. Defaults to True.

        Returns:
            WebElement: The clicked element.

        Raises:
            Exception: If an error occurs while clicking the element.
        """

        try:
            if wait:
                elem = WebDriverWait(driver, wait).until(
                    EC.element_to_be_clickable((selector, x_path)))

                if use_js:
                    driver.execute_script("arguments[0].click()", elem)
                else:
                    elem.click()

                return elem
            elem = driver.find_element(selector, x_path)
            elem.click()
            return elem
        except Exception as e:
            raise e

    def getDownLoadedFileName(self, driver: WebDriver, waitTime=500):
        """
        A function to get the name of the downloaded file after a download operation.

        Args:
            driver: The WebDriver object.
            waitTime: Maximum time to wait for the download to complete (default is 500 seconds).

        Returns:
            The name of the downloaded file.

        Raises:
            Exception: If an error occurs during the process of getting the downloaded file name.
        """

        driver.execute_script("window.open()")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get('chrome://downloads')

        endTime = time() + waitTime
        while True:
            sleep(1)
            try:
                try:
                    # get downloaded percentage
                    downloadPercentage = driver.execute_script(
                        "return document.querySelector('downloads-manager')"
                        ".shadowRoot"
                        ".querySelector('#downloadsList downloads-item')"
                        ".shadowRoot"
                        ".querySelector('#progress').value")
                    if downloadPercentage == 100:
                        sleep(3)
                        self.find_by_element(driver, r'//*[@id="tag"]', wait=5)
                        return driver.execute_script(
                            "return document"
                            ".querySelector('downloads-manager')"
                            ".shadowRoot"
                            ".querySelector('#downloadsList downloads-item')"
                            ".shadowRoot"
                            ".querySelector('div#content  #file-link').text")
                except Exception:
                    return driver.execute_script(
                        "return document"
                        ".querySelector('downloads-manager')"
                        ".shadowRoot"
                        ".querySelector('#downloadsList downloads-item')"
                        ".shadowRoot"
                        ".querySelector('div#content  #file-link').text")

                if time() > endTime:
                    print('Tempo esgotado')
                    break

            except JavascriptException:
                raise Exception("Não foi possível fazer o download do arquivo")

    def save_page_as_pdf(self, driver: WebDriver, **kwargs):
        """
        A function to save the current page as a PDF file.

        Args:
            driver: The WebDriver object.
            **kwargs: Additional keyword arguments.

        Formats:
            margin: _MarginOpts
            page: _PageOpts
            background: bool
            orientation: Orientation
            scale: float
            shrinkToFit: bool
            pageRanges: List[str]

        Raises:
            Exception: If an error occurs during the process of saving the page as a PDF file.
        """

        print_opt = PrintOptions()

        for key, value in kwargs.items():
            setattr(print_opt, key, value)

        driver.print_page(print_opt)

import pyautogui

from time import sleep
from colorama import init
from os.path import join, exists


class AutoGui:
    def __init__(self, path: str, local_path: str = None):
        """Cria um objeto para automação utilizando imagens

        Args:
            path (str): Define um path geral para caso não queira criar um path personalizado para cada desktop
            local_path (str, optional): Cria um path específico onde irá buscar as imagens de referência. Defaults to None.
        """
        init()
        if exists(local_path):
            self.path = local_path
        else:
            self.path = path

    def go_to_btn_click(self, image: str, confidence: int = 0.7,
                        grayscale: bool = False, sleep_t: int | float = 0.5, **kwargs):
        """
        The function `go_to_btn_click` locates and clicks on a button on the screen based on an input image.

        :param image: The image parameter is a string that represents the path to the image file or the
        image itself that you want to locate on the screen
        :type image: str
        :param confidence: The confidence parameter is used to specify the minimum confidence level required
        for the image recognition. It is a value between 0 and 1, where 1 represents 100% confidence. The
        default value is 0.7, which means that the image must be recognized with at least 70%
        :type confidence: int
        :param grayscale: The `grayscale` parameter is a boolean value that determines whether the image
        should be searched in grayscale or color. If `grayscale` is set to `True`, the image will be
        converted to grayscale before searching for it on the screen. If `grayscale` is set to `False`,
        defaults to False
        :type grayscale: bool (optional)
        :param sleep_t: The parameter `sleep_t` is the amount of time (in seconds) to sleep after clicking
        the button. It is used to introduce a delay between consecutive actions, defaults to 1
        :type sleep_t: int | float (optional)
        """
        try:
            btn = pyautogui.locateCenterOnScreen(image=join(self.path, image),
                                                 confidence=confidence,
                                                 grayscale=grayscale,
                                                 **kwargs)
        except Exception as e:
            raise Exception(fr"""\033[1;31mErro: {e}
                Erro ao localizar a imagem {image}. \033[0m
                Caso o erro persista, capture novamente a imagem usando a ferramenta de captura e substitua a imagem dentro da pasta \033[4;33m"{self.path}"\033[0m utilizando o mesmo nome do arquivo que será substituido.
                """)

        if btn:
            pyautogui.click(btn.x, btn.y)
            sleep(sleep_t)

    def go_to_btn_dbclick(self, image: str, confidence: int = 0.7,
                          grayscale: bool = False, sleep_t: int | float = 0.5,
                          **kwargs):
        """
        The function `go_to_btn_dbclick` locates a button on the screen using an image, and if found, double
        clicks on it and sleeps for a specified amount of time.

        :param image: The image parameter is a string that represents the path or filename of the image file
        you want to search for on the screen
        :type image: str
        :param confidence: The `confidence` parameter is used to specify the minimum confidence level
        required for the image recognition. It is a value between 0 and 1, where 1 represents 100%
        confidence. The default value is 0.7, meaning that the image must be recognized with at least 70
        :type confidence: int
        :param grayscale: The `grayscale` parameter is a boolean value that determines whether the image
        should be searched in grayscale or color. If `grayscale` is set to `True`, the image will be
        converted to grayscale before searching for it on the screen. If `grayscale` is set to `False`,
        defaults to False
        :type grayscale: bool (optional)
        :param sleep_t: The parameter `sleep_t` is the amount of time to sleep after double-clicking the
        button. It can be specified as an integer or float value, representing the number of seconds to
        sleep, defaults to 1
        :type sleep_t: int | float (optional)
        """
        try:
            btn = pyautogui.locateCenterOnScreen(image=self.path(
                image), confidence=confidence, grayscale=grayscale, **kwargs)
        except Exception as e:
            raise Exception(fr"""\033[1;31mErro: {e}
                Erro ao localizar a imagem {image}. \033[0m
                Caso o erro persista, capture novamente a imagem usando a ferramenta de captura e substitua a imagem dentro da pasta \033[4;33m{self.path}\033[0m utilizando o mesmo nome do arquivo que será substituido.
                """)

        if btn:
            pyautogui.doubleClick(btn.x, btn.y)
            sleep(sleep_t)

    def locate_image(self, image: str, confidence: int = 0.7,
                     grayscale: bool = False, sleep_t: int | float = 0.5,
                     **kwargs):
        """
        The `locate_image` function uses the `pyautogui` library to locate an image on the screen with a
        specified confidence level, grayscale option, and additional keyword arguments, and returns the
        center coordinates of the image if found, or None if not found.

        :param image: The image parameter is a string that represents the path or filename of the image file
        you want to locate on the screen
        :type image: str
        :param confidence: The confidence parameter determines the minimum confidence level required for the
        image to be considered a match. It is a value between 0 and 1, where 1 represents a perfect match
        and 0 represents no match. The default value is 0.7, meaning that the image must be at least
        :type confidence: int
        :param grayscale: The `grayscale` parameter is a boolean value that determines whether the image
        should be searched in grayscale or color. If `grayscale` is set to `True`, the image will be
        searched in grayscale. If `grayscale` is set to `False` (default), the image will be, defaults to
        False
        :type grayscale: bool (optional)
        :param sleep_t: The `sleep_t` parameter is the amount of time (in seconds) that the program will
        pause before attempting to locate the image on the screen. This can be useful if you want to give
        the screen some time to load or if you want to slow down the execution of the program. The default,
        defaults to 1
        :type sleep_t: int | float (optional)
        :return: The function `locate_image` returns the coordinates of the center of the located image if
        it is found on the screen. If the image is not found, it returns `None`.
        """
        try:
            img = pyautogui.locateCenterOnScreen(image=join(self.path, image),
                                                 confidence=confidence,
                                                 grayscale=grayscale,
                                                 **kwargs)

            if img:
                sleep(sleep_t)
                return img
            else:
                return None
        except Exception as e:
            raise Exception(fr"""\033[1;31mErro: {e}
                Erro ao localizar a imagem {image}. \033[0m
                Caso o erro persista, capture novamente a imagem usando a ferramenta de captura e substitua a imagem dentro da pasta \033[4;33m"{self.path}"\033[0m utilizando o mesmo nome do arquivo que será substituido.
                """)

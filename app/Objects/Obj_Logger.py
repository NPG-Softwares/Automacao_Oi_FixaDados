import os
import gzip


class Logger:
    def __init__(self, file_name: str, path: str):
        self.file_name = file_name
        self.path = os.path.abspath(path)
        self.full_path = os.path.join(self.path, self.file_name)
        self._create_if_not_exists()

    def write(self, content: str):
        with gzip.open(self.full_path, 'wt') as file:
            file.write(content)

    def append(self, content: str):
        content = content.strip()

        if not content.startswith('\n') and len(self.read()) > 0:
            content = '\n' + content

        print(content)
        with gzip.open(self.full_path, 'at') as file:
            file.write(content)

    def read(self):
        """
        Lê o conteúdo do arquivo comprimido Gzip.

        :return: O conteúdo do arquivo como uma string.
        """
        with gzip.open(self.full_path, 'rt') as file:
            return file.read()

    def clear(self):
        """
        Limpa o conteúdo do arquivo.
        """
        with gzip.open(self.full_path, 'wt') as file:
            file.write('')

    def to_list(self) -> list:
        return self.read().split('\n')

    def _create_if_not_exists(self):
        os.makedirs(os.path.dirname(self.full_path), exist_ok=True)

        if not self._file_exists():
            self.write('')

    def _file_exists(self):
        """
        Verifica se o arquivo comprimido Gzip existe.

        :return: True se o arquivo existir, False caso contrário.
        """
        return os.path.exists(self.full_path)

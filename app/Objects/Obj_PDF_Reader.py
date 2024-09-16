import os
import re

import fitz
from PyPDF2 import PdfReader


class PDFReader:
    def __init__(self, file, path) -> None:
        self.file = file
        self.path = path

    def read_pdf(self, engine="fitz"):
        self.engine = engine
        if engine not in ["PyPDF2", "fitz", "PyMuPDF"]:
            raise EnvironmentError(
                "Engine não reconhecida. Engines disponiveis: PyPDF2, fitz, PyMuPDF")

        if engine == "PyPDF2":
            self._pdf_obj = open(os.path.join(self.path, self.file), 'rb')
            self._pdf_readed = PdfReader(self._pdf_obj)
            return self._pdf_readed

        elif engine == "fitz" or engine == "PyMuPDF":
            self._pdf_obj = fitz.open(os.path.join(self.path, self.file))
            return self._pdf_obj

    def get_text(self, pdf, page) -> str:
        if self.engine == "PyPDF2":
            return pdf.pages[page].extract_text().encode().decode()

        elif self.engine == "fitz" or self.engine == "PyMuPDF":
            return pdf.load_page(page).get_text().encode().decode()

    def find_element(self, line: str, element: str, index: int = -1,
                     sep: str = None, debug_line: bool = False,
                     regex: bool = None) -> str:
        if regex:
            result = re.findall(element, line)
            if len(result) > 0:
                return result

        if element in line:
            if debug_line:
                print(line)
                print(line.split(sep))

            found_element = line.split(sep)[index].strip()
            return found_element

    def get_pages(self) -> int:
        return range(len(self._pdf_readed.pages) if self.engine == "PyPDF2"
                     else self._pdf_obj.page_count)

    def close_pdf(self):
        self._pdf_obj.close()

    def extract_specific_pages(self, output_file, pages_to_extract):
        with fitz.open() as new_pdf:
            for page_number in pages_to_extract:
                self._pdf_obj.load_page(page_number)
                new_pdf.insert_pdf(self._pdf_obj,
                                   from_page=page_number,
                                   to_page=page_number)
            new_pdf.save(output_file)

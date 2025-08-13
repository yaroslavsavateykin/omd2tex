import re

from .paragraph import Paragraph
from default.globals import GLOBAL_MIN_HEADLINE_LEVEL, GLOBAL_REFERENCE_DICT


class Headline:
    def __init__(self, level: int, text: str, settings={}) -> None:
        self.level = level
        self.__identify_level()
        self.settings = settings
        self.text = text

        self._is_initialized = False
        self.reference = None

    @staticmethod
    def identify_headline_reference(elements: list) -> list:
        new_list = []

        for el in elements:
            if isinstance(el, Headline):
                el._is_initialized = True
                el._identify_reference()
                new_list.append(el)
            else:
                new_list.append(el)
        return new_list

    def _identify_reference(self) -> None:
        if self.reference:
            settings = self.settings["headline"]
            global GLOBAL_REFERENCE_DICT
            global GLOBAL_MIN_HEADLINE_LEVEL

            if GLOBAL_MIN_HEADLINE_LEVEL < self.level:
                self.__global_level_align()

            if settings["numeration"]:
                ref_type = [
                    "sec",
                    "subsec",
                    "subsubsec",
                    "par",
                    "txt",
                    "txt",
                    "txt",
                    "txt",
                ]
                GLOBAL_REFERENCE_DICT[self.reference] = ref_type[self.level]
            else:
                GLOBAL_REFERENCE_DICT[self.reference] = "not_found_headline"

    def __identify_level(self) -> None:
        global GLOBAL_MIN_HEADLINE_LEVEL

        if self.level < GLOBAL_MIN_HEADLINE_LEVEL:
            GLOBAL_MIN_HEADLINE_LEVEL = self.level

    def __global_level_align(self) -> None:
        global GLOBAL_MIN_HEADLINE_LEVEL

        settings = self.settings["headline"]
        if settings["global_level_align"]:
            self.level -= GLOBAL_MIN_HEADLINE_LEVEL + 1

    def _pick_surround(self):
        global GLOBAL_MIN_HEADLINE_LEVEL
        global GLOBAL_REFERENCE_DICT

        settings = self.settings["headline"]

        if settings["numeration"]:
            latex_command = [
                "section",
                "subsection",
                "subsubsection",
                "paragraph",
                "textbf",
                "textbf",
                "textbf",
                "textbf",
            ]
            if self.reference:
                ref_type = [
                    "sec",
                    "subsec",
                    "subsubsec",
                    "par",
                    "txt",
                    "txt",
                    "txt",
                    "txt",
                ]
                latex_function = (
                    lambda x: f"\\{latex_command[self.level]}{{{x}}}\\label{{{ref_type[self.level]}:{self.reference}}}"
                )
            else:
                latex_function = lambda x: f"\\{latex_command[self.level]}{{{x}}}"

        else:
            latex_command = [
                "\\Large",
                "\\large",
                "\\normalsize",
                "\\normalsize",
                "\\normalsize",
                "\\normalsize",
                "\\normalsize",
                "\\normalsize",
            ]

            latex_function = (
                lambda x: f"\n\\noindent\\textbf{{{latex_command[self.level]} {x}}}\\newline"
            )

        return latex_function

    @staticmethod
    def _clean_markdown_numeration(heading: str) -> str:
        """
        Дипсикнуто)
        Удаляет все форматы нумерации из начала строки заголовка Markdown.
        Поддерживает:
        - Арабские цифры (1, 1.1, 1.1.1)
        - Римские цифры (IV, vii, ХХ)
        - Буквенные обозначения (a, A, б, Б)
        - Разделители (., ), ], •, ◦, ›)
        - Скобки (круглые, квадратные)
        - Многоуровневые комбинации (1.A.iii, [IV.б])

        Параметры:
            heading (str): Строка заголовка Markdown

        Возвращает:
            str: Очищенная строка без нумерации
        """
        # Компилируем комплексное регулярное выражение
        print(heading)
        pattern = re.compile(
            r"^\s*"  # Начальные пробелы
            r"[\[({]?"  # Необязательная открывающая скобка
            r"(?:"  # Группа элементов:
            r"(?:\d+|"  # Арабские цифры
            r"[a-zа-я]|"  # Одиночные буквы (латиница/кириллица)
            r"[ivxlcdm]+|"  # Римские цифры (строчные)
            r"[IVXLCDM]+|"  # Римские цифры (заглавные)
            r"[IVXLCDMivxlcdmа-яА-Я]+"  # Комбинированные наборы
            r")"
            r"(?:"  # Группа разделителей:
            r"[\.\s)\]}•◦›]|"  # Стандартные разделители
            r"\)\s*|"  # Закрывающая скобка с пробелом
            r"\]\s*|"  # Закрывающая квадратная скобка
            r"\}\s*"  # Закрывающая фигурная скобка
            r")?"  # Разделитель не обязателен
            r")+"  # Один или более элементов
            r"[\]})]?"  # Необязательная закрывающая скобка
            r"\s*"  # Конечные пробелы
            r"(?=[^\w\s]|$)",  # Lookahead для границы
            re.IGNORECASE | re.UNICODE,
        )
        heading = pattern.sub("", heading, count=1).strip()
        print(heading)
        # Удаляем нумерацию и возвращаем результат
        return heading

    def _parse_text(self, text):
        text = self._clean_markdown_numeration(text)
        par = Paragraph(text=text, settings=self.settings)
        text = par._parse_text()

        return text

    def to_latex(self):
        if not self._is_initialized:
            raise RuntimeError("Headline is not initialized! Firstly call initialize()")

        return self._pick_surround()(self.text)

    def to_latex_project(self, settings={}):
        return self.to_latex()

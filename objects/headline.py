import re

from objects.equation import Equation
from tools.settings import Settings

from .paragraph import Paragraph
from tools.globals import Global


class Headline:
    def __init__(self, level: int, text: str) -> None:
        self.level = level
        self.__identify_level()
        self.text = text

        self._is_initialized = False
        self.reference = None

    def _identify_reference(self) -> None:
        self._is_initialized = True
        self.__global_level_align()

        if self.reference:
            if Settings.Headline.numeration:
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
                Global.REFERENCE_DICT[self.reference] = ref_type[self.level]

    def __identify_level(self) -> None:
        if self.level < Global.MIN_HEADLINE_LEVEL:
            Global.MIN_HEADLINE_LEVEL = self.level

    def __global_level_align(self) -> None:
        if Settings.Headline.global_level_align:
            self.level -= Global.MIN_HEADLINE_LEVEL

    def _pick_surround(self):
        if Settings.Headline.numeration:
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
        # Удаляем нумерацию и возвращаем результат
        return heading

    @staticmethod
    def _parse_text(text):
        if Settings.Headline.clean_all_highlight:
            text = Paragraph._remove_all_highlight(text)
        if Settings.Headline.clean_markdown_numeration:
            text = Headline._clean_markdown_numeration(text)
        text = Paragraph(text).to_latex()

        return text

    def to_latex(self):
        if not self._is_initialized:
            raise RuntimeError(
                "Headline is not initialized! Firstly call _identify_reference()"
            )

        return self._pick_surround()(self._parse_text(self.text))

    def _to_latex_project(self):
        return self.to_latex()

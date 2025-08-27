import re

from .equation import Equation
from .paragraph import Paragraph

from ..tools import Settings
from ..tools import Global


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
        if not heading:
            return heading

        # Более консервативное регулярное выражение - удаляет только явную нумерацию
        patterns = [
            # Арабские цифры с точкой и пробелом: "1. ", "1.1. ", "1.1.1. "
            r"^\s*\d+(?:\.\d+)*\.\s+",
            # Арабские цифры со скобкой: "1) ", "1.1) "
            r"^\s*\d+(?:\.\d+)*\)\s+",
            # Римские цифры с точкой: "IV. ", "vii. "
            r"^\s*[ivxlcdmIVXLCDM]+\.\s+",
            # Римские цифры со скобкой: "IV) ", "vii) "
            r"^\s*[ivxlcdmIVXLCDM]+\)\s+",
            # Буквы с точкой: "a. ", "A. ", "б. ", "Б. "
            r"^\s*[a-zA-Zа-яА-ЯёЁ]\.\s+",
            # Буквы со скобкой: "a) ", "A) ", "б) ", "Б) "
            r"^\s*[a-zA-Zа-яА-ЯёЁ]\)\s+",
            # В скобках: "[1] ", "(1) ", "[a] ", "(a) "
            r"^\s*[\[({][a-zA-Zа-яА-ЯёЁ0-9ivxlcdmIVXLCDM]+[\])}]\s+",
            # Маркеры списков: "• ", "◦ ", "› "
            r"^\s*[•◦›]\s+",
            # Сложные комбинации в скобках: "[1.A.iii] ", "(2.б) "
            r"^\s*[\[({]\w+(?:[\.\-]\w+)*[\])}]\s+",
        ]

        result = heading

        # Применяем паттерны по очереди, останавливаемся на первом совпадении
        for pattern_str in patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE | re.UNICODE)
            new_result = pattern.sub("", result, count=1)
            if new_result != result:
                result = new_result
                break

        return result.strip()

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

import re
import json
import random

from objects.citation import Citation
from objects.footnote import Footnote
from tools.globals import Global
from tools.settings import Settings


class Paragraph:
    def __init__(self, text: str, parse=True) -> None:
        self.text = text
        self.parse = parse

        self.reference = None

        self.footnote = Footnote().collection

    def to_latex(self):
        return self._parse_text()

    def to_latex_project(self):
        return self.to_latex()

    @staticmethod
    def _change_letters_for_equations(
        text, dict_file="default/formulas.json", surround_func=lambda x: x
    ):
        with open(dict_file, "r") as f:
            change_dict = json.load(f)
        for key in change_dict:
            text = text.replace(key, surround_func(change_dict[key]))

        return text

    @staticmethod
    def _highlight_text(text: str) -> str:
        # regular expressions: function
        change_dict = {
            r"\*\*(.*?)\*\*": lambda x: f"\\textbf{{{x.group(1)}}}",
            r"\_\_(.*?)\_\_": lambda x: f"\\textbf{{{x.group(1)}}}",
            r"\*(.*?)\*": lambda x: f"\\textit{{{x.group(1)}}}",
            r"\_(.*?)\_": lambda x: f"\\textit{{{x.group(1)}}}",
            r"\=\=(.*?)\=\=": lambda x: f"\\sethlcolor{{mintgreen}}\\hl{{{x.group(1)}}}",
            r"\~\~(.*?)\~\~": lambda x: f"\\sout{{{x.group(1)}}}",
            r"\#(.*?)": lambda x: f"{x.group(1)}",
            r"\<u>(.*?)<\/u>": lambda x: f"\\ul{{{x.group(1)}}}",
            r"\<sup>(.*?)<\/sup>": lambda x: f"$_\\text{{{x.group(1)}}}$",
            r"\<sub>(.*?)<\/sub>": lambda x: f"$^\\text{{{x.group(1)}}}$",
        }

        for regular in change_dict:
            text = re.sub(
                regular,
                change_dict[regular],
                text,
            )
        return text

    @staticmethod
    def _replace_inline_code(text: str) -> tuple[str, list]:
        inline_codes = []

        def replace_inline(match):
            inline_codes.append(match.group(1))
            return f"@@INLINE-CODE-{len(inline_codes)}@@"

        text = re.sub(r"`(.*?)`", replace_inline, text)

        return text, inline_codes

    @staticmethod
    def _replace_inline_equation(text: str) -> tuple[str, list]:
        inline_equations = []

        def replace_inline(match):
            inline_equations.append(match.group(1))
            return f"@@INLINE-EQUATION-{len(inline_equations)}@@"

        text = re.sub(r"\$(.*?)\$", replace_inline, text)
        return text, inline_equations

    @staticmethod
    def _replace_outline_equation(text: str) -> tuple[str, list]:
        outline_equations = []

        def replace_inline(match):
            outline_equations.append(match.group(1))
            return f"@@OUTLINE-EQUATION-{len(outline_equations)}@@"

        text = re.sub(r"\$\$([\\s\\S]*?)\$\$", replace_inline, text)
        return text, outline_equations

    @staticmethod
    def _restore_placeholders(
        text: str, inline_equations=[], inline_codes=[], outline_equations=[]
    ) -> str:
        if inline_codes:
            for i, inline_code in enumerate(inline_codes):
                inline_code = (
                    inline_code.replace("\\", "\\\\")
                    .replace("#", "\\#")
                    .replace("$", "\\$")
                    .replace("%", "\\%")
                )
                text = text.replace(
                    f"@@INLINE-CODE-{i + 1}@@", f"\\texttt{{{inline_code}}}"
                )

        if inline_equations:
            for i, inline_equation in enumerate(inline_equations):
                text = text.replace(
                    f"@@INLINE-EQUATION-{i + 1}@@",
                    f"${inline_equation}$",
                )

        if outline_equations:
            for i, outline_equation in enumerate(outline_equations):
                text = text.replace(
                    f"@@OUTLINE-EQUATION-{i + 1}@@",
                    f"${outline_equation}$",
                )

        return text

    @staticmethod
    def _latinify_lines(
        lines: str,
        probability=0.05,
        seed=None,
        change_dict="default/latinify_line.json",
    ) -> str:
        if seed is not None:
            random.seed(seed)

        with open(change_dict, "r") as f:
            repl_map = json.load(f)

        def replace_in_string(s: str) -> str:
            result_chars = []
            for ch in s:
                if ch in repl_map and random.random() < probability:
                    result_chars.append(random.choice(repl_map[ch]))
                else:
                    result_chars.append(ch)
            return "".join(result_chars)

        return "".join([replace_in_string(line) for line in lines])

    @staticmethod
    def _eq_ru_letter_workaround(text: str) -> str:
        change_list = [
            "й",
            "ц",
            "у",
            "к",
            "е",
            "н",
            "г",
            "ш",
            "щ",
            "з",
            "ф",
            "ы",
            "в",
            "а",
            "п",
            "р",
            "о",
            "л",
            "д",
            "ж",
            "э",
            "я",
            "ч",
            "с",
            "м",
            "и",
            "т",
            "ь",
            "б",
            "ю",
            "ё",
        ]
        new_text = []

        for letter in text:
            if letter.lower() in change_list:  # Проверяем в нижнем регистре
                new_text.append(f"\\text{{{letter}}}")
            else:
                new_text.append(letter)

        return "".join(new_text)

    @staticmethod
    def _text_errors_workaround(text: str) -> str:
        change_dict = {"й": "й"}
        for key in change_dict:
            text = text.replace(key, change_dict[key])

        return text

    @staticmethod
    def _process_references(text: str) -> str:
        ref_pattern = re.compile(
            r"\[\[(?:([^\|\]#]+)?#)?\^([^\|\]]+)(?:\|([^\]]+))?\]\]"
        )

        def process_ref_match(match):
            file_reference = match.group(1) or ""
            ref_id = match.group(2)
            text = match.group(3)

            if ref_id in Global.REFERENCE_DICT:
                latex_ref = f"\\cref{{{Global.REFERENCE_DICT[ref_id]}:{ref_id}}}"
            else:
                latex_ref = ""
                print(f"Reference {ref_id} not found in Global.REFERENCE_DICT")

            if text:
                return text + " " + latex_ref
            return latex_ref

        text = ref_pattern.sub(process_ref_match, text)

        return text

    def _process_footnotes(self, text: str) -> str:
        def process(match):
            key = match.group(1)
            if self.footnote[key]:
                return f" \\footnote{{{self.footnote[key]}}} "
            else:
                print(f"Footnote {key}")
                return " "

        text = re.sub(r"\[\^([^\]]+)\]", process, text)

        return text

    @staticmethod
    def _process_citations(text):
        """
        Обрабатывает различные форматы цитирований и приводит их к формату: text \cite{cite}

        Поддерживаемые форматы:
        ![[@cite|text]] -> text \cite{cite}
        ![[@cite]] -> \cite{cite}
        [[@cite|text]] -> text \cite{cite}
        [[@cite]] -> \cite{cite}
        \cite{@cite} -> \cite{cite}
        \cite{cite} -> \cite{cite}
        """
        result = text

        pattern1 = r"(!?)\[\[@([^|\]]+)(?:\|([^\]]+))?\]\]"

        def replace_pattern1(match):
            has_exclamation = match.group(1) == "!"
            cite = match.group(2).strip()
            text_part = match.group(3)

            if text_part:
                cit = Citation(key=f"@{cite}")
                if cit.text:
                    return f"{text_part.strip()} \\cite{{{cite}}}"
                else:
                    return ""
            else:
                cit = Citation(key=f"@{cite}")
                if cit.text:
                    return f"\\cite{{{cite}}}"
                else:
                    return ""

        result = re.sub(pattern1, replace_pattern1, result)

        pattern2 = r"\\cite\{@([^}]+)\}"

        def replace_pattern2(match):
            cite = match.group(1).strip()
            cit = Citation(key=f"@{cite}")
            if cit.text:
                return f"\\cite{{{cite}}}"
            else:
                return ""

        result = re.sub(pattern2, replace_pattern2, result)

        return result

    def _parse_text(self) -> str:
        if self.parse:
            text = self.text

            text, outline_equations = self._replace_outline_equation(text)

            text = re.sub(
                r"\$(?:[^$\\]|\\\$|\\[^$])*?\$",
                lambda x: f"${self._change_letters_for_equations(x.group(0).strip('$'), dict_file=Settings.Paragraph.formulas_json)}$",
                text,
            )
            text = self._change_letters_for_equations(
                text, surround_func=lambda x: f"${x}$"
            )

            text, inline_codes = self._replace_inline_code(text)

            text, inline_equations = self._replace_inline_equation(text)

            outline_equations = [
                self._eq_ru_letter_workaround(x) for x in outline_equations
            ]

            inline_equations = [
                self._eq_ru_letter_workaround(x) for x in inline_equations
            ]

            text = self._highlight_text(text)

            text = self._restore_placeholders(
                text,
                inline_codes=inline_codes,
                inline_equations=inline_equations,
                outline_equations=outline_equations,
            )

            text = self._process_references(text)

            text = self._process_footnotes(text)

            text = self._process_citations(text)

            text = self._text_errors_workaround(text)

            if Settings.Paragraph.latinify:
                text = self._latinify_lines(
                    text,
                    probability=Settings.Paragraph.latinify_probability,
                    change_dict=Settings.Paragraph.latinify_json,
                )
        else:
            text = self.text

        return text

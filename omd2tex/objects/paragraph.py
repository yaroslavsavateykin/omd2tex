import os
import re
import json
import random

from .base import BaseClass

from .citation import Citation
from .footnote import Footnote


class Paragraph(BaseClass):
    def __init__(self, text: str, parse: bool = True) -> None:
        """Initialize a paragraph wrapper with optional parsing.

        Args:
            text: Raw paragraph content.
            parse: Whether to apply markdown and reference transformations.

        Returns:
            None
        """
        super().__init__()
        self.text = text
        self.parse = parse

        self.reference = None

        self.footnote = Footnote().collection

    def to_latex(self) -> str:
        """Render the paragraph to LaTeX, optionally parsing markdown constructs."""
        return self._parse_text()

    def _to_latex_project(self) -> str:
        return self.to_latex()

    @staticmethod
    def change_letters_for_equations(
        text: str, dict_file: str = "", surround_func=lambda x: x
    ) -> str:
        """Replace symbols in equations using a mapping file and wrapper.

        Args:
            text: Input equation text.
            dict_file: Optional path to a JSON mapping file; defaults to bundled formulas.
            surround_func: Callable applied to mapped values.

        Returns:
            Transformed text with mapped symbols.
        """
        from ..tools import Global, Settings

        if dict_file:
            dict_file = Settings.Paragraph.formulas_json
        else:
            dict_file = os.path.join(
                os.path.dirname((__file__)), "..", "default/formulas.json"
            )

        with open(os.path.expanduser(dict_file), "r") as f:
            change_dict = json.load(f)
        for key in change_dict:
            text = text.replace(key, surround_func(change_dict[key]))

        return text

    _change_letters_for_equations = change_letters_for_equations

    @staticmethod
    def highlight_text1(text: str) -> str:
        """Convert HTML superscript/subscript markers to LaTeX equivalents."""
        change_dict = {
            r"<sup>(.*?)</sup>": lambda x: f"$^{{{x.group(1)}}}$",
            r"<sub>(.*?)</sub>": lambda x: f"$_{{{x.group(1)}}}$",
            r"<u>(.*?)</u>": lambda x: f"\\ul{{{x.group(1)}}}",
        }

        for regular in change_dict:
            text = re.sub(
                regular,
                change_dict[regular],
                text,
            )
        return text

    _highlight_text1 = highlight_text1

    @staticmethod
    def highlight_text2(text: str) -> str:
        """Convert markdown emphasis markers to LaTeX formatting."""
        change_dict = {
            r"\*\*(.*?)\*\*": lambda x: f"\\textbf{{{x.group(1)}}}",
            r"__(.*?)__": lambda x: f"\\textbf{{{x.group(1)}}}",
            r"\*(.*?)\*": lambda x: f"\\textit{{{x.group(1)}}}",
            r"_(.*?)_": lambda x: f"\\textit{{{x.group(1)}}}",
            r"==(.*?)==": lambda x: f"\\sethlcolor{{mintgreen}}\\hl{{{x.group(1)}}}",
            r"~~(.*?)~~": lambda x: f"\\sout{{{x.group(1)}}}",
            r"#(.*?)(?=\s|$)": lambda x: f"\\#{x.group(1)}",
        }

        for regular in change_dict:
            text = re.sub(
                regular,
                change_dict[regular],
                text,
            )
        return text

    _highlight_text2 = highlight_text2

    @staticmethod
    def replace_inline_code(text: str) -> tuple[str, list]:
        """Replace inline code segments with placeholders preserving content."""
        inline_codes = []

        def replace_inline(match):
            inline_codes.append(match.group(1))
            return f"@@INLINE-CODE-{len(inline_codes)}@@"

        text = re.sub(r"`(.*?)`", replace_inline, text)

        return text, inline_codes

    _replace_inline_code = replace_inline_code

    @staticmethod
    def replace_inline_equation(text: str) -> tuple[str, list]:
        """Replace inline equations with placeholders preserving content."""
        inline_equations = []

        def replace_inline(match):
            inline_equations.append(match.group(1))
            return f"@@INLINE-EQUATION-{len(inline_equations)}@@"

        text = re.sub(r"\$(.*?)\$", replace_inline, text)
        return text, inline_equations

    _replace_inline_equation = replace_inline_equation

    @staticmethod
    def replace_outline_equation(text: str) -> tuple[str, list]:
        """Replace outline equations with placeholders preserving content."""
        outline_equations = []

        def replace_inline(match):
            outline_equations.append(match.group(1))
            return f"@@OUTLINE-EQUATION-{len(outline_equations)}@@"

        text = re.sub(r"\$\$(.*?)\$\$", replace_inline, text)
        return text, outline_equations

    _replace_outline_equation = replace_outline_equation

    @staticmethod
    def restore_placeholders(
        text: str, inline_equations=[], inline_codes=[], outline_equations=[]
    ) -> str:
        """Restore code and equation placeholders into the provided text."""
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

    _restore_placeholders = restore_placeholders

    @staticmethod
    def latinify_lines(
        lines: str,
        probability=0.05,
        seed=None,
        change_dict="",
    ) -> str:
        """Randomly replace characters based on latinify mapping and probability."""
        if seed is not None:
            random.seed(seed)

        if change_dict:
            change_dict = Settings.Paragraph.latinify_json
        else:
            change_dict = os.path.join(
                os.path.dirname((__file__)), "..", "default/latinify.json"
            )

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

    _latinify_lines = latinify_lines

    @staticmethod
    def eq_ru_letter_workaround(text: str) -> str:
        """Wrap Cyrillic characters in equations with text mode to avoid errors."""
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

    _eq_ru_letter_workaround = eq_ru_letter_workaround

    @staticmethod
    def text_errors_workaround(text: str) -> str:
        """Normalize known problematic characters and dashes."""
        change_dict = {"й": "й", "–": "-", "ο": "o", "ё": "ё", "−": "-"}
        for key in change_dict:
            text = text.replace(key, change_dict[key])

        return text

    _text_errors_workaround = text_errors_workaround

    @staticmethod
    def process_references(text: str) -> str:
        """Convert wiki-style references to LaTeX cref calls using global mapping."""
        from ..tools import Global, Settings

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
                # print(f"Reference {ref_id} not found in Global.REFERENCE_DICT")

            if text:
                return text + " " + latex_ref
            return latex_ref

        text = ref_pattern.sub(process_ref_match, text)

        return text

    _process_references = process_references

    def _process_footnotes(self, text: str) -> str:
        """Replace footnote markers with LaTeX footnote commands using collection."""

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
    def process_citations(text: str) -> str:
        """Normalize citation markers to LaTeX ``\\cite{}`` commands.

        Supports patterns like ``![[ @cite|text ]]``, ``[[ @cite ]]``, and ``\\cite{@cite}``, returning formatted citations or empty strings when source entries are missing.

        Args:
            text: Input string possibly containing various citation syntaxes.

        Returns:
            Text with citation patterns replaced by LaTeX citations; returns empty strings when citations are missing.
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

    _process_citations = process_citations

    def _parse_text(self) -> str:
        """Parse and transform paragraph text according to settings."""
        from ..tools import Global, Settings

        if self.parse:
            text = self.text

            # text = self.escape_latex_special_chars(text)
            text, outline_equations = self.replace_outline_equation(text)

            text = self.highlight_text1(text)

            for i in range(len(outline_equations)):
                outline_equations[i] = self.change_letters_for_equations(
                    outline_equations[i]
                )

            text = re.sub(
                r"\$\$(.*?)\$\$",
                lambda x: f"$${self.change_letters_for_equations(x.group(0).strip('$'), dict_file=Settings.Paragraph.formulas_json)}$$",
                text,
            )

            text = re.sub(
                r"\$(?:[^$\\]|\\\$|\\[^$])*?\$",
                lambda x: f"${self.change_letters_for_equations(x.group(0).strip('$'), dict_file=Settings.Paragraph.formulas_json)}$",
                text,
            )

            text = self.change_letters_for_equations(
                text, surround_func=lambda x: f"${x}$"
            )

            text, inline_codes = self.replace_inline_code(text)

            text, inline_equations = self.replace_inline_equation(text)

            outline_equations = [
                self.eq_ru_letter_workaround(x) for x in outline_equations
            ]

            inline_equations = [
                self.eq_ru_letter_workaround(x) for x in inline_equations
            ]

            text = self.highlight_text2(text)

            text = self.restore_placeholders(
                text,
                inline_codes=inline_codes,
                inline_equations=inline_equations,
                outline_equations=outline_equations,
            )

            text = self.process_references(text)

            text = self._process_footnotes(text)

            text = self.process_citations(text)

            text = self.text_errors_workaround(text)

            if Settings.Paragraph.latinify:
                text = self.latinify_lines(
                    text,
                    probability=Settings.Paragraph.latinify_probability,
                    change_dict=Settings.Paragraph.latinify_json,
                )

            text = text.replace(r"\%", "%").replace("%", r"\%")

        else:
            text = self.text

        return text

    @staticmethod
    def escape_latex_special_chars(text: str) -> str:
        """Escape unescaped LaTeX special characters in the provided text.

        Args:
            text (str): Входная строка с LaTeX-выражениями

        Returns:
            str: Строка с экранированными специальными символами LaTeX
        """
        # Список специальных символов LaTeX, которые нужно экранировать
        special_chars = ["#", "$", "\%", "&", "_", "{", "}", "~", "^", "\\"]
        special_chars = ["\%", "&"]

        # Регулярное выражение для поиска неэкранированных специальных символов
        pattern = r"(?<!\\)([" + re.escape("".join(special_chars)) + r"])"

        # Экранируем найденные символы
        escaped_text = re.sub(pattern, r"\\\1", text)

        return escaped_text

    @staticmethod
    def remove_all_highlight(text: str) -> str:
        """Strip all markdown-style highlighting and emphasis markers."""
        change_dict = {
            r"\*\*(.*?)\*\*": lambda x: x.group(1),
            r"__(.*?)__": lambda x: x.group(1),
            r"\*(.*?)\*": lambda x: x.group(1),
            r"_(.*?)_": lambda x: x.group(1),
            r"==(.*?)==": lambda x: x.group(1),
            r"~~(.*?)~~": lambda x: x.group(1),
            r"#(.*?)(?=\s|$)": lambda x: x.group(
                1
            ),  # Только до пробела или конца строки
            r"<u>(.*?)</u>": lambda x: x.group(1),
            r"<sup>(.*?)</sup>": lambda x: x.group(1),  # Исправлено
            r"<sub>(.*?)</sub>": lambda x: x.group(1),  # Исправлено
        }

        for regular in change_dict:
            text = re.sub(
                regular,
                change_dict[regular],
                text,
            )
        return text

    _remove_all_highlight = remove_all_highlight

    @staticmethod
    def merge_items(items: list) -> list:
        """Merge adjacent Paragraph instances when parsing flags match."""
        if not items:
            return []

        result = []
        i = 0

        while i < len(items):
            current_item = items[i]

            if not isinstance(current_item, Paragraph):
                result.append(current_item)
                i += 1
                continue

            j = i + 1
            while j < len(items):
                next_item = items[j]

                if not isinstance(next_item, Paragraph):
                    break

                if (
                    next_item.parse == current_item.parse
                    and next_item.reference == current_item.reference
                ):
                    current_item.text += " " + current_item.text
                    j += 1
                else:
                    break

            result.append(current_item)
            i = j if j > i + 1 else i + 1

        return result

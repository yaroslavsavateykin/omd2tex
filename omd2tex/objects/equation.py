from .paragraph import Paragraph
from ..tools import Global
from ..tools import Settings


class Equation:
    def __init__(self, equation: str) -> None:
        self.equation = equation.strip("\n")

        self.reference = None

        self._is_initialized = True

    def _identify_reference(self):
        self._is_initialized = True
        Global.REFERENCE_DICT[self.reference] = "eq"

    def to_latex(self):
        if not self._is_initialized:
            raise RuntimeError(
                "Equation is not initialized! Firstly call _identify_reference()"
            )

        equation = Paragraph._change_letters_for_equations(
            self.equation.strip("\n"),
            dict_file=Settings.Paragraph.formulas_json,
        )
        equation = Paragraph._eq_ru_letter_workaround(equation)
        if self.reference:
            equation = rf"""
\begin{{equation}}
{equation}
\label{{eq:{self.reference}}}
\end{{equation}}"""
        else:
            equation = rf"""
\begin{{equation*}}
{equation}
\end{{equation*}}"""
        return equation

    def _to_latex_project(self):
        return self.to_latex()

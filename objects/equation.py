from default.globals import GLOBAL_REFERENCE_DICT


class Equation:
    def __init__(self, equation: str) -> None:
        self.equation = equation

        self.reference = None

    def to_latex(self, settings={}):
        global GLOBAL_REFERENCE_DICT

        if self.reference:
            GLOBAL_REFERENCE_DICT[self.reference] = "eq"

            equation = rf"""
\begin{{equation}}
{self.equation.strip("\n")}
\label{{eq:{self.reference}}}
\end{{equation}}
"""
        else:
            equation = rf"""
\begin{{equation*}}
{self.equation.strip("\n")}
\end{{equation*}}
"""
        return equation

    def to_latex_project(self, settings={}):
        return self.to_latex(settings)

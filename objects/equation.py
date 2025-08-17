from tools.globals import Global


class Equation:
    def __init__(self, equation: str) -> None:
        self.equation = equation

        self.reference = None

        self._is_initialized = False

    def _identify_reference(self):
        self._is_initialized = True
        Global.REFERENCE_DICT[self.reference] = "eq"

    def to_latex(self):
        if not self._is_initialized:
            raise RuntimeError(
                "Equation is not initialized! Firstly call _identify_reference()"
            )

        if self.reference:
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

    def to_latex_project(self):
        return self.to_latex()

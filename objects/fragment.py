from tools.settings import Settings


class SplitLine:
    def __init__(self, text: str = ""):
        self.text = text

    def to_latex(self):
        return f"\\noindent\\rule{{\\textwidth}}{{{Settings.Fragment.Splitline.width}}} %{self.text}"

    def to_latex_project(self):
        return self.to_latex()

from .base import BaseClass
from .headline import Headline

from typing import Union, List


class SplitLine(BaseClass):
    def __init__(self, text: str = "") -> None:
        """Initialize a split line marker optionally carrying text."""
        # Counter.Splitline += 1
        self.text = text

    def to_latex(self) -> str:
        """Render a horizontal rule using configured width."""
        from ..tools import Global, Settings
        return f"\\noindent\\rule{{\\textwidth}}{{{Settings.Fragment.Splitline.width}}} %{self.text}"

    def _to_latex_project(self) -> str:
        return self.to_latex()

    @classmethod
    def make_beamer(cls, elements_list: List) -> List:
        """Split elements into beamer frames based on divider elements."""
        from ..tools import Global, Settings
        frames = []
        current_frame_elements = []
        frame_title = ""

        divide_dict = {"splitline": SplitLine, "headline": Headline}

        divide_list = Settings.Beamer.divide_element

        if isinstance(divide_list, List):
            divide_els = []
            if "splitline" in divide_list:
                divide_els.append("splitline")
            if "headline" in divide_list:
                divide_els.append("headline")
        elif any(x == divide_list for x in divide_dict):
            divide_els = [divide_list]
        else:
            print(f"No such divider as {divide_list}. Using Splitline.")
            divide_els = ["splitline"]

        for el in elements_list:
            is_divider = False
            for divide_el in divide_els:
                if isinstance(el, divide_dict[divide_el]):
                    is_divider = True
                    if current_frame_elements:
                        frames.append(
                            Frame(
                                elements=current_frame_elements.copy(),
                                title=frame_title,
                            )
                        )
                        current_frame_elements.clear()
                    frame_title = el.text.strip() if el.text else ""
                    break  # важный момент — прекращаем проверку после нахождения разделителя
            if not is_divider:
                current_frame_elements.append(el)

        return frames


class Frame(BaseClass):
    def __init__(self, elements: List, title="") -> None:
        """Initialize a beamer frame with elements and optional title."""
        super().__init__()
        self.elements = elements
        self.title = title

    def to_latex(self) -> str:
        """Render the frame with contained elements to LaTeX."""
        elements = "\n".join([x.to_latex() for x in self.elements])

        latex = f"""\\begin{{frame}}{{{self.title}}}

{elements}

\\end{{frame}}"""

        return latex

    def _to_latex_project(self) -> str:
        """Render the frame for project export, keeping comments for structure."""
        elements = "\n\n".join([x._to_latex_project() for x in self.elements])

        latex = f"""\\begin{{frame}}{{{self.title}}}{"%" * 30}

{elements}

\\end{{frame}}{"%" * 30}
"""

        return latex


class Caption(BaseClass):
    def __init__(self, text: Union[list, str]) -> None:
        """Initialize a caption wrapper from list or string content."""
        if isinstance(text, list):
            self.cap_text = " ".join(text)
        elif isinstance(text, str):
            self.cap_text = text.replace("\n", " ")

    @staticmethod
    def attach_caption(elements) -> List:
        """Attach caption objects to the preceding element as metadata."""
        result = []
        last_reference = None

        for el in elements:
            if isinstance(el, Caption):
                last_reference = el
                if result:
                    result[-1].caption = last_reference.cap_text
            else:
                last_reference = None
                result.append(el)

        return result

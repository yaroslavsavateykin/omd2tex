from omd2tex.objects.headline import Headline
from ..tools import Settings
from ..tools import Counter

from typing import Union, List


class SplitLine:
    def __init__(self, text: str = ""):
        Counter.Splitline += 1
        self.text = text

    def to_latex(self):
        return f"\\noindent\\rule{{\\textwidth}}{{{Settings.Fragment.Splitline.width}}} %{self.text}"

    def _to_latex_project(self):
        return self.to_latex()

    @classmethod
    def make_beamer(cls, elements_list: List) -> List:
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


class Frame:
    def __init__(self, elements: List, title=""):
        self.elements = elements
        self.title = title

    def to_latex(self):
        elements = "\n".join([x.to_latex() for x in self.elements])

        latex = f"""\\begin{{frame}}{{{self.title}}}

{elements}

\\end{{frame}}"""

        return latex

    def _to_latex_project(self):
        elements = "\n\n".join([x._to_latex_project() for x in self.elements])

        latex = f"""\\begin{{frame}}{{{self.title}}}{"%" * 30}

{elements}

\\end{{frame}}{"%" * 30}
"""

        return latex


class Caption:
    def __init__(self, text: Union[list, str]):
        if isinstance(text, list):
            self.cap_text = " ".join(text)
        elif isinstance(text, str):
            self.cap_text = text.replace("\n", " ")

    @staticmethod
    def attach_caption(elements):
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

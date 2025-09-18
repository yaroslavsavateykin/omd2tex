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

        for el in elements_list:
            if isinstance(el, SplitLine):
                if current_frame_elements:
                    frames.append(
                        Frame(elements=current_frame_elements.copy(), title=frame_title)
                    )
                    current_frame_elements.clear()

                frame_title = el.text.strip() if el.text else ""

            else:
                current_frame_elements.append(el)

        if current_frame_elements:
            frames.append(
                Frame(elements=current_frame_elements.copy(), title=frame_title)
            )

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
        elements = "\n".join([x._to_latex_project() for x in self.elements])

        latex = f"""\\begin{{frame}}{{{self.title}}}
        {elements}
        \\end{{frame}}"""

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
                # Обновляем последний референс (перезаписываем если были подряд)
                last_reference = el
                # Прикрепляем к последнему элементу в результате (если есть)
                if result:
                    result[-1].caption = last_reference.cap_text
            else:
                # Сбрасываем референс для нового элемента
                last_reference = None
                result.append(el)

        return result

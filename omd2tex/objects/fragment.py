from ..tools import Settings


from typing import Union


class SplitLine:
    def __init__(self, text: str = ""):
        self.text = text

    def to_latex(self):
        return f"\\noindent\\rule{{\\textwidth}}{{{Settings.Fragment.Splitline.width}}} %{self.text}"

    def _to_latex_project(self):
        return self.to_latex()


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

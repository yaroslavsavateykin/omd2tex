from .base import BaseClass
from .equation import Equation
from .headline import Headline
from .image import Image
from .table import Table


class Reference(BaseClass):
    def __init__(self, ref_text: str) -> None:
        super().__init__()
        self.ref_text = ref_text

    def to_latex(self):
        return ""

    def _to_latex_project(self):
        return self.to_latex()

    @staticmethod
    def identify_elements_reference(elements: list) -> list:
        new_list = []
        types = [Headline, Equation, Image, Table]

        for el in elements:
            if type(el) in types:
                el._identify_reference()
                new_list.append(el)
            else:
                new_list.append(el)
        return new_list

    @staticmethod
    def attach_reference(elements):
        result = []
        last_reference = None

        for el in elements:
            if isinstance(el, Reference):
                last_reference = el
                if result:
                    result[-1].reference = last_reference.ref_text
            else:
                last_reference = None
                result.append(el)

        return result

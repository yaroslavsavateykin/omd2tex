from .base import BaseClass
from .equation import Equation
from .headline import Headline
from .image import Image
from .table import Table
from .quote import Quote


class Reference(BaseClass):
    @staticmethod
    def _filename_variants(filename: str) -> list:
        if not filename:
            return []

        normalized = str(filename).strip().replace("\\", "/")
        if not normalized:
            return []

        variants = [normalized]
        if normalized.startswith("./"):
            variants.append(normalized[2:])
        if normalized.endswith(".md"):
            variants.append(normalized[:-3])

        base = normalized.rsplit("/", 1)[-1]
        variants.append(base)
        if base.endswith(".md"):
            variants.append(base[:-3])

        uniq = []
        seen = set()
        for item in variants:
            if item and item not in seen:
                uniq.append(item)
                seen.add(item)
        return uniq

    def __init__(self, ref_text: str) -> None:
        """Initialize a reference marker.

        Args:
            ref_text: Reference identifier without prefix.

        Returns:
            None
        """
        super().__init__()
        self.ref_text = ref_text

    def to_latex(self) -> str:
        """Render reference placeholder; no direct LaTeX output."""
        return ""

    def _to_latex_project(self) -> str:
        return self.to_latex()

    @staticmethod
    def identify_elements_reference(elements: list) -> list:
        """Update reference mappings for supported element types.

        Args:
            elements: List of parsed elements to inspect.

        Returns:
            New list with reference metadata registered.
        """
        from ..tools import Global

        new_list = []
        types = [Headline, Equation, Image, Table, Quote]

        for el in elements:
            if type(el) in types:
                el._identify_reference()
                ref_id = getattr(el, "reference", None)
                if ref_id:
                    ref_type = Global.REFERENCE_DICT.get(ref_id)
                    if ref_type:
                        source_filename = getattr(el, "_source_filename", "")
                        for variant in Reference._filename_variants(source_filename):
                            Global.REFERENCE_DICT[f"{variant}#^{ref_id}"] = ref_type
                new_list.append(el)
            else:
                new_list.append(el)
        return new_list

    @staticmethod
    def attach_reference(elements):
        """Attach the last seen reference object to the preceding element.

        Args:
            elements: Sequence of elements that may include Reference instances.

        Returns:
            List where references are assigned to prior elements when present.
        """
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

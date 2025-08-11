class Reference:
    def __init__(self, ref_text: str) -> None:
        self.ref_text = ref_text

    def to_latex(self):
        return ""

    def to_latex_project(self):
        return self.to_latex()

    @staticmethod
    def attach_reference(elements):
        result = []
        pending_reference = None

        for el in elements:
            if isinstance(el, Reference):
                pending_reference = el
            else:
                if pending_reference:
                    setattr(el, "reference", pending_reference)
                    pending_reference = None
                result.append(el)

        return result

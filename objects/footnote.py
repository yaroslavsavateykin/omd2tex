class Footnote:
    collection = {}

    @classmethod
    def append(cls, key: str, text: str):
        from objects.paragraph import Paragraph

        cls.collection[key] = Paragraph(text).to_latex()

    @classmethod
    def to_default(cls):
        cls.collection = {}

    def __init__(self):
        self.collection = self.__class__.collection

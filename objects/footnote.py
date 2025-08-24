import uuid
import re


class Footnote:
    collection = {}

    @classmethod
    def append(cls, key: str, text: str):
        from .paragraph import Paragraph

        cls.collection[key] = Paragraph(text).to_latex()

    def to_default(cls):
        cls.collection = {}

    def __init__(self):
        self.exchange_dict = {}

    def change_footnote_keys(self, text: str) -> str:
        def process(match):
            key = match.group(1)
            if key in self.exchange_dict:
                return f"[^{self.exchange_dict[key]}]"
            else:
                new_key = str(uuid.uuid4())[:7]
                self.exchange_dict[key] = new_key
                return f"[^{self.exchange_dict[key]}]"

        text = re.sub(r"\[\^([^\]]+)\]", process, text)

        return text

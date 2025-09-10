import uuid
import re
from typing import Union, List


class Footnote:
    collection = {}

    @classmethod
    def append(cls, key: str, text: Union[str, List[str]]):
        from .paragraph import Paragraph

        if isinstance(text, list):
            text = "\n".join(text)

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

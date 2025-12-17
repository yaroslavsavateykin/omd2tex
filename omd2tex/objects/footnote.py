import uuid
import re
from typing import Union, List

from .base import BaseClass


class Footnote(BaseClass):
    collection = {}

    @classmethod
    def append(cls, key: str, text: Union[str, List[str]]) -> None:
        """Add a footnote to the shared collection converting markdown to LaTeX.

        Args:
            key: Footnote identifier.
            text: Footnote text as string or list of lines.

        Returns:
            None

        Side Effects:
            Mutates the class-level ``collection`` mapping.
        """
        from .paragraph import Paragraph

        if isinstance(text, list):
            text = "\n".join(text)

        cls.collection[key] = Paragraph(text).to_latex()

    def to_default(cls) -> None:
        """Reset the shared footnote collection to defaults."""
        cls.collection = {}

    def __init__(self) -> None:
        """Initialize a footnote helper with an exchange dictionary."""
        super().__init__()
        self.exchange_dict = {}

    def change_footnote_keys(self, text: str) -> str:
        """Replace footnote keys in text with unique generated identifiers.

        Args:
            text: Input text containing footnote markers.

        Returns:
            Text with footnote keys rewritten to unique values.
        """
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

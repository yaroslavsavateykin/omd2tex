from functools import wraps
import re
from typing import Union
from objects.paragraph import Paragraph


class List:
    def __init__(self, text: str, depth: int, number=0, complete=False, reference=None):
        self.text = text
        self.depth = depth
        self.complete = complete
        self.number = number

        self.reference = reference

        self.items = [self]
        self.merged = []

    def to_latex_item(self):
        text = Paragraph(self.text).to_latex()

        return text

    def to_latex(self):
        if not self.merged:
            return "\n\n".join([x.to_latex_item() for x in self.items])
        else:
            return "\n\n".join([x.to_latex() for x in self.merged])

    def to_latex_project(self):
        return self.to_latex()

    def append(self, item):
        if isinstance(item, self.__class__) and item.depth == self.depth:
            self.items.append(item)
        elif isinstance(item, self.__class__):
            raise TypeError(
                f"Item's depth ({item.depth}) must be the same as ({self.depth})"
            )
        else:
            raise TypeError(f"Item must be instance of {self.__class__.__name__}")

    @staticmethod
    def append_items(items: list):
        if not items:
            return []

        allowed_classes = [Enumerate, Bullet, Check]

        grouped = []
        i = 0

        while i < len(items):
            current_item = items[i]
            current_type = type(current_item)

            if current_type not in allowed_classes:
                grouped.append(current_item)
                i += 1
                continue

            if not hasattr(current_item, "depth"):
                grouped.append(current_item)
                i += 1
                continue

            current_depth = current_item.depth

            j = i + 1
            while j < len(items):
                next_item = items[j]
                next_type = type(next_item)

                if (
                    next_type == current_type
                    and hasattr(next_item, "depth")
                    and next_item.depth == current_depth
                ):
                    current_item.append(next_item)
                    j += 1
                else:
                    break

            grouped.append(current_item)
            i = j

        return grouped

    def merge(self, item):
        if item.depth > self.depth:
            self.merged.append(item)
        else:
            raise TypeError(
                f"Item's depth ({item.depth}) must be lower then ({self.depth})"
            )

    @staticmethod
    def merge_items(items: list):
        if not items:
            return []

        allowed_classes = [Enumerate, Bullet, Check]

        grouped = []
        i = 0

        while i < len(items):
            current_item = items[i]
            current_type = type(current_item)

            if current_type not in allowed_classes:
                grouped.append(current_item)
                i += 1
                continue

            if not hasattr(current_item, "depth"):
                grouped.append(current_item)
                i += 1
                continue

            current_depth = current_item.depth

            j = i + 1
            while j < len(items):
                next_item = items[j]
                next_type = type(next_item)

                if hasattr(next_item, "depth") and next_item.depth > current_depth:
                    current_item.merge(next_item)
                    j += 1
                else:
                    break

            grouped.append(current_item)
            i = j

        return grouped

    @staticmethod
    def indent(text, depth):
        text = text.splitlines()
        new_text = []

        for line in text:
            new_text.append(depth * "    " + line)

        return "\n".join(new_text)


class Enumerate(List):
    def to_latex_item(self):
        return List.indent(
            f"\\setcounter{{enumi}}{{{self.number}}}\n\\item {super().to_latex_item()}",
            self.depth + 1,
        )

    def to_latex(self):
        return List.indent(
            f"\\begin{{enumerate}}\\keepwithnext\n{super().to_latex()}\n\\end{{enumerate}}",
            self.depth,
        )


class Check(List):
    def to_latex_item(self):
        if self.complete:
            return List.indent(
                f"\\item[$\\square$] {super().to_latex_item()}", self.depth + 1
            )
        else:
            return List.indent(
                f"\\item[$\\boxtimes$] \\sout{{{super().to_latex_item()}}}",
                self.depth + 1,
            )

    def to_latex(self):
        return List.indent(
            f"\\begin{{itemize}}\\keepwithnext\n{super().to_latex()}\n\\end{{itemize}}",
            self.depth,
        )


class Bullet(List):
    def to_latex_item(self):
        return List.indent(f"\\item {super().to_latex_item()}", self.depth + 1)

    def to_latex(self):
        return List.indent(
            f"\\begin{{itemize}}\\keepwithnext\n{super().to_latex()}\n\\end{{itemize}}",
            self.depth,
        )

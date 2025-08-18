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
        if self.merged:
            # Если есть вложенные элементы
            main_content = "\n".join([x.to_latex_item() for x in self.items])
            merged_content = "\n".join([x.to_latex() for x in self.merged])
            return (
                main_content + "\n" + merged_content if merged_content else main_content
            )
        else:
            # Только основные элементы
            return "\n".join([x.to_latex_item() for x in self.items])

    def to_latex_project(self):
        return self.to_latex()

    def append(self, item):
        """Добавляет элемент того же типа и глубины в список items"""
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
        """Группирует подряд идущие элементы одного типа и глубины"""
        if not items:
            return []

        grouped = []
        i = 0

        while i < len(items):
            current_item = items[i]
            current_type = type(current_item)

            # Проверяем, является ли элемент наследником List
            if not isinstance(current_item, List):
                grouped.append(current_item)
                i += 1
                continue

            current_depth = current_item.depth

            # Ищем подряд идущие элементы того же типа и глубины
            j = i + 1
            while j < len(items):
                next_item = items[j]
                next_type = type(next_item)

                if next_type == current_type and next_item.depth == current_depth:
                    current_item.append(next_item)
                    j += 1
                else:
                    break

            grouped.append(current_item)
            i = j

        return grouped

    def merge(self, item):
        """Добавляет элемент с большей глубиной в список merged"""
        if item.depth > self.depth:
            self.merged.append(item)
        else:
            raise TypeError(
                f"Item's depth ({item.depth}) must be greater than ({self.depth})"
            )

    @staticmethod
    def merge_items(items: list):
        """Объединяет элементы по принципу вложенности (depth)"""
        if not items:
            return []

        result = []
        i = 0

        while i < len(items):
            current_item = items[i]

            # Проверяем, является ли элемент наследником List
            if not isinstance(current_item, List):
                result.append(current_item)
                i += 1
                continue

            # Ищем вложенные элементы
            j = i + 1
            while j < len(items):
                next_item = items[j]

                if not isinstance(next_item, List):
                    break

                if next_item.depth > current_item.depth:
                    current_item.merge(next_item)
                    j += 1
                else:
                    break

            result.append(current_item)
            i = j if j > i + 1 else i + 1

        return result

    @staticmethod
    def indent(text, depth):
        if depth <= 0:
            return text
        text_lines = text.splitlines()
        indented_lines = [depth * "    " + line for line in text_lines]
        return "\n".join(indented_lines)


class Enumerate(List):
    def to_latex_item(self):
        return List.indent(
            f"\\setcounter{{enumi}}{{{self.number}}}\n\\item {super().to_latex_item()}",
            self.depth,
        )

    def to_latex(self):
        content = super().to_latex()
        return List.indent(
            f"\\begin{{enumerate}}\\keepwithnext\n{content}\n\\end{{enumerate}}",
            self.depth,
        )


class Check(List):
    def to_latex_item(self):
        if self.complete:
            return List.indent(
                f"\\item[$\\boxtimes$] \\sout{{{super().to_latex_item()}}}",
                self.depth,
            )
        else:
            return List.indent(
                f"\\item[$\\square$] {super().to_latex_item()}",
                self.depth,
            )

    def to_latex(self):
        content = super().to_latex()
        return List.indent(
            f"\\begin{{itemize}}\\keepwithnext\n{content}\n\\end{{itemize}}",
            self.depth,
        )


class Bullet(List):
    def to_latex_item(self):
        return List.indent(f"\\item {super().to_latex_item()}", self.depth)

    def to_latex(self):
        content = super().to_latex()
        return List.indent(
            f"\\begin{{itemize}}\\keepwithnext\n{content}\n\\end{{itemize}}",
            self.depth,
        )

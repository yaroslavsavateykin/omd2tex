from .base import BaseClass
from .paragraph import Paragraph
from ..tools import Settings
from ..tools.settings_preamble import SettingsPreamble


class List(BaseClass):
    def __init__(self, text: str, depth: int, number: int = 0, complete: bool = False, reference=None) -> None:
        """Initialize a list item with metadata for nesting and rendering."""
        super().__init__()
        self.text = text
        self.depth = depth
        self.complete = complete
        self.number = number

        self.reference = reference

        self.items = [self]
        self.merged = []

    def to_latex_item(self) -> str:
        """Render a single list item to LaTeX.

        Returns:
            LaTeX string representing the list item content.
        """
        text = Paragraph(self.text).to_latex()
        return text

    def to_latex(self) -> str:
        """Render the list and merged nested items to LaTeX.

        Returns:
            LaTeX string for the list content, including merged sublists when present.
        """
        if self.merged:
            main_content = "\n".join([x.to_latex_item() for x in self.items])
            merged_content = "\n".join([x.to_latex() for x in self.merged])
            return (
                main_content + "\n" + merged_content if merged_content else main_content
            )
        else:
            return "\n".join([x.to_latex_item() for x in self.items])

    def _to_latex_project(self) -> str:
        return self.to_latex()

    def append(self, item: "List") -> None:
        """Append another list item at the same depth.

        Args:
            item: List item to append; must match depth.

        Returns:
            None

        Raises:
            TypeError: If item type or depth is incompatible.
        """
        if isinstance(item, self.__class__) and item.depth == self.depth:
            self.items.append(item)
        elif isinstance(item, self.__class__):
            raise TypeError(
                f"Item's depth ({item.depth}) must be the same as ({self.depth})"
            )
        else:
            raise TypeError(f"Item must be instance of {self.__class__.__name__}")

    @staticmethod
    def append_items(items: list) -> list:
        """Group consecutive list items of equal depth.

        Args:
            items: Sequence of parsed elements possibly containing List instances.

        Returns:
            List with grouped List items aggregated by depth.
        """
        if not items:
            return []

        grouped = []
        i = 0

        
        while i < len(items):
            
            current_line = items[i]._start_line
            current_item = items[i]
            current_type = type(current_item)
            current_item._start_line = current_line

            if not isinstance(current_item, List):
                grouped.append(current_item)
                i += 1
                continue

            current_depth = current_item.depth

            j = i + 1
            while j < len(items):

                current_line = items[i]._start_line
                next_item = items[j]
                next_type = type(next_item)

                if next_type == current_type and next_item.depth == current_depth:
                    next_item._start_line = current_line
                    current_item.append(next_item)
                    j += 1
                else:
                    break

            grouped.append(current_item)
            i = j

        return grouped

    def merge(self, item: "List") -> None:
        """Merge a deeper nested item under the current list element.

        Args:
            item: Nested List item.

        Returns:
            None

        Raises:
            TypeError: If provided item is not deeper than the current one.
        """
        if item.depth > self.depth:
            self.merged.append(item)
        else:
            raise TypeError(
                f"Item's depth ({item.depth}) must be greater than ({self.depth})"
            )

    @staticmethod
    def merge_items(items: list) -> list:
        """Merge subsequent deeper list items into preceding parents.

        Args:
            items: Sequence of elements containing List instances.

        Returns:
            List where nested items are attached to their appropriate parents.
        """
        if not items:
            return []

        result = []
        i = 0
        

        while i < len(items):
            current_item = items[i]

            if not isinstance(current_item, List):
                result.append(current_item)
                i += 1
                continue

            j = i + 1
            while j < len(items):
                current_line = items[i]._start_line
                
                next_item = items[j]
                next_item._start_line = current_line

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
    def indent(text: str, depth: int) -> str:
        """Indent text by a multiple of four spaces based on depth.

        Args:
            text: String to indent.
            depth: Nesting level to determine indentation.

        Returns:
            Indented text string.
        """
        if depth <= 0:
            return text
        text_lines = text.splitlines()
        indented_lines = [depth * "    " + line for line in text_lines]
        return "\n".join(indented_lines)


class Enumerate(List):
    def to_latex_item(self) -> str:
        """Render an enumerated item with adjusted counter."""
        return List.indent(
            f"\\setcounter{{enumi}}{{{self.number - 1}}}\n\\item {super().to_latex_item()}",
            1,
        )

    def to_latex(self) -> str:
        """Render an enumerate environment with optional keep-with-next fix."""
        content = super().to_latex()
        if SettingsPreamble.documentclass == "article":
            fix = "\\keepwithnext"
        else:
            fix = ""

        return List.indent(
            f"\\begin{{enumerate}}{fix}\\itemsep{Settings.List.itemsep}\n{content}\n\\end{{enumerate}}",
            # f"\\begin{{enumerate}}\\keepwithnext\\itemsep{Settings.List.itemsep}\n{content}\n\\end{{enumerate}}",
            0,
        )


class Check(List):
    def to_latex_item(self) -> str:
        """Render a checklist item using box symbols."""
        if self.complete:
            return List.indent(
                f"\\item[$\\boxtimes$] \\sout{{{super().to_latex_item()}}}",
                1,
            )
        else:
            return List.indent(
                f"\\item[$\\square$] {super().to_latex_item()}",
                1,
            )

    def to_latex(self) -> str:
        """Render a checklist as an itemize environment."""
        if SettingsPreamble.documentclass == "article":
            fix = "\\keepwithnext"
        else:
            fix = ""
        content = super().to_latex()
        return List.indent(
            f"\\begin{{itemize}}{fix}\\itemsep{Settings.List.itemsep}\n{content}\n\\end{{itemize}}",
            # f"\\begin{{itemize}}\\keepwithnext\\itemsep{Settings.List.itemsep}\n{content}\n\\end{{itemize}}",
            self.depth,
        )


class Bullet(List):
    def to_latex_item(self) -> str:
        """Render a bullet list item."""
        return List.indent(f"\\item {super().to_latex_item()}", 1)

    def to_latex(self) -> str:
        """Render a bullet list environment."""
        content = super().to_latex()
        if SettingsPreamble.documentclass == "article":
            fix = "\\keepwithnext"
        else:
            fix = ""
        return List.indent(
            f"\\begin{{itemize}}{fix}\\itemsep{Settings.List.itemsep}\n{content}\n\\end{{itemize}}",
            # f"\\begin{{itemize}}\\keepwithnext\\itemsep{Settings.List.itemsep}\n{content}\n\\end{{itemize}}",
            self.depth,
        )

class BaseClass:
        
    def __init__(self) -> None:
        """Initialize shared metadata for document elements."""

        self._start_line = 0
        # self._end_line = 0

    def to_latex(self) -> str:
        """Render the object to LaTeX markup.

        Returns:
            LaTeX string representation.
        """
        pass

    def _to_latex_project(self) -> str:
        """Render the object to LaTeX for project export context.

        Returns:
            LaTeX string representation suitable for file-based export.
        """
        pass 

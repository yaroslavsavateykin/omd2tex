class Header:
    def __init__(self, level: int, text: str, settings={}) -> None:
        self.text = self._parse_text(text, settings)
        self.level = level
        self.settings = settings

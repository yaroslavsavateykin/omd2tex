from .config_base import ConfigBase


class Global(ConfigBase):
    REFERENCE_DICT = {}
    HEADING_REFERENCE_DICT = {}
    MIN_HEADLINE_LEVEL = 100
    CITATION_INITIALIZED = False
    CREATE_PROJECT = False

    YAML_DICT = {}

    DOCUMENT_CLASS = "article"  # article, beamer

    DOCUMENT_NAME = ""

    ERROR_CATCHER = True

    NEW_COMMANDS_PREAMBLE = []

    @classmethod
    def to_default(cls) -> None:
        super().to_default()

        from ..objects.citation import Citation
        from ..objects.footnote import Footnote

        Citation.citation_list = []
        Footnote.collection = {}

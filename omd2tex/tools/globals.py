from .config_base import ConfigBase


class Global(ConfigBase):
    REFERENCE_DICT = {}
    MIN_HEADLINE_LEVEL = 100
    CITATION_INITIALIZED = False
    CREATE_PROJECT = False

    YAML_DICT = {}

    DOCUMENT_CLASS = "article"  # article, beamer

    DOCUMENT_NAME = ""

    ERROR_CATCHER = True

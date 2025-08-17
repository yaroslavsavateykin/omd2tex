from tools.config_base import ConfigBase


class ParagraphConfig(ConfigBase):
    latinify = True
    latinify_probability = 0.05
    latinify_json = "default/latinify.json"
    formulas_json = "default/formulas.json"

    def __init__(self):
        self.latinify = self.__class__.latinify
        self.latinify_probability = self.__class__.latinify_probability
        self.latinify_json = self.__class__.latinify_json
        self.formulas_json = self.__class__.formulas_json
        super().__init__()


class HeadlineConfig(ConfigBase):
    global_level_align = True
    numeration = True
    clean_markdown_numeration = True

    def __init__(self):
        self.global_level_align = self.__class__.global_level_align
        self.numeration = self.__class__.numeration
        self.clean_markdown_numeration = self.__class__.clean_markdown_numeration
        super().__init__()


class ImageConfig(ConfigBase):
    wh_aspect_borders = [0.6, 1.8]
    default_width = "8cm"
    default_height = "8cm"

    def __init__(self):
        self.wh_aspect_borders = self.__class__.wh_aspect_borders
        self.default_width = self.__class__.default_width
        self.default_height = self.__class__.default_height
        super().__init__()


class QuoteConfig(ConfigBase):
    max_quote_recursion = 5

    def __init__(self):
        self.max_quote_recursion = self.__class__.max_quote_recursion
        super().__init__()


class Settings(ConfigBase):
    max_file_recursion = 5
    dir = "~/Vzlet/"
    preamble = True
    makefile = True
    output_dir = "~/omd2tex/test/"
    branching_project = False

    def __init__(self):
        self.max_file_recursion = self.__class__.max_file_recursion
        self.dir = self.__class__.dir
        self.preamble = self.__class__.preamble
        self.makefile = self.__class__.makefile
        self.output_dir = self.__class__.output_dir
        self.branching_project = self.__class__.branching_project
        self.paragraph = ParagraphConfig()
        self.headline = HeadlineConfig()
        self.image = ImageConfig()
        self.quote = QuoteConfig()
        super().__init__()

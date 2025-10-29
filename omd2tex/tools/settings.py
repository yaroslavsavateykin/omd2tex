from .config_base import ConfigBase


class Settings(ConfigBase):
    class Export(ConfigBase):
        search_dir = "~/Obsidian/"
        search_ignore_dirs = [
            ".trash",
            ".obsidian",
            ".plugins",
            ".smart-env",
            ".reference-map",
            "LaTeX",
        ]
        makefile = True
        export_dir = "./test/"
        branching_project = False

        def __init__(self):
            self.search_dir = self.__class__.search_dir
            self.search_ignore_dirs = self.__class__.search_ignore_dirs
            self.makefile = self.__class__.makefile
            self.export_dir = self.__class__.export_dir
            self.branching_project = self.__class__.branching_project
            super().__init__()

    class Frontmatter(ConfigBase):
        parse = False

        def __init__(self):
            self.parse = self.__class__.parse
            super().__init__()

    class Beamer(ConfigBase):
        divide_element = "splitline"

        def __init__(self):
            self.divide_element = self.__class__.divide_element
            super().__init__()

    class Paragraph(ConfigBase):
        latinify = True
        latinify_probability = 0.05
        latinify_json = ""
        formulas_json = ""

        def __init__(self):
            self.latinify = self.__class__.latinify
            self.latinify_probability = self.__class__.latinify_probability
            self.latinify_json = self.__class__.latinify_json
            self.formulas_json = self.__class__.formulas_json
            super().__init__()

    class Preamble(ConfigBase):
        create_preamble = True
        settings_json = ""

        def __init__(self):
            self.create_preamble = self.__class__.create_preamble
            self.settings_json = self.__class__.settings_json
            super().__init__()

    class File(ConfigBase):
        parse = True
        max_file_recursion = 5
        pass_if_not_found = True

        def __init__(self):
            self.parse = self.__class__.parse
            self.max_file_recursion = self.__class__.max_file_recursion
            self.pass_if_not_found = self.__class__.pass_if_not_found
            super().__init__()

    class Headline(ConfigBase):
        parse = True
        global_level_align = True
        numeration = True
        clean_markdown_numeration = False
        clean_all_highlight = True

        def __init__(self):
            self.parse = self.__class__.parse
            self.global_level_align = self.__class__.global_level_align
            self.numeration = self.__class__.numeration
            self.clean_markdown_numeration = self.__class__.clean_markdown_numeration
            self.clean_all_highlight = self.__class__.clean_all_highlight
            super().__init__()

    class Image(ConfigBase):
        parse = True
        wh_aspect_borders = [0.6, 1.8]
        default_width = "8cm"
        default_height = "8cm"

        def __init__(self):
            self.parse = self.__class__.parse
            self.wh_aspect_borders = self.__class__.wh_aspect_borders
            self.default_width = self.__class__.default_width
            self.default_height = self.__class__.default_height
            super().__init__()

    class Quote(ConfigBase):
        parse = True
        max_quote_recursion = 5

        def __init__(self):
            self.parse = self.__class__.parse
            self.max_quote_recursion = self.__class__.max_quote_recursion
            super().__init__()

    class List(ConfigBase):
        itemsep = "0pt"

        def __init__(self):
            self.itemsep = self.__class__.itemsep
            super().__init__()

    class Fragment(ConfigBase):
        class Splitline(ConfigBase):
            parse = True
            width = "0.5pt"

            def __init__(self):
                self.parse = self.__class__.parse
                self.width = self.__class__.width
                super().__init__()

        class Caption(ConfigBase):
            parse = True

            def __init__(self):
                self.parse = self.__class__.parse
                super().__init__()

        def __init__(self):
            self.splitline = self.__class__.Splitline()
            self.caption = self.__class__.Caption()
            super().__init__()

    def __init__(self):
        self.export = self.__class__.Export()
        self.frontmatter = self.__class__.Frontmatter()
        self.beamer = self.__class__.Beamer()
        self.paragraph = self.__class__.Paragraph()
        self.preamble = self.__class__.Preamble()
        self.file = self.__class__.File()
        self.headline = self.__class__.Headline()
        self.image = self.__class__.Image()
        self.quote = self.__class__.Quote()
        self.list = self.__class__.List()
        self.fragment = self.__class__.Fragment()
        super().__init__()

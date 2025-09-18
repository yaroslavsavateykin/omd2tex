from .config_base import ConfigBase

class SettingsPreamble(ConfigBase):
    class Article(ConfigBase):
        fontsize = '12pt'
        linespread = 1.5
        left = '2cm'
        right = '2cm'
        top = '2cm'
        bottom = '2cm'

        def __init__(self):
            self.fontsize = self.__class__.fontsize
            self.linespread = self.__class__.linespread
            self.left = self.__class__.left
            self.right = self.__class__.right
            self.top = self.__class__.top
            self.bottom = self.__class__.bottom
            super().__init__()


    class Beamer(ConfigBase):
        fontsize = '12pt'
        linespread = 1.5
        left = '0.5cm'
        right = '0.5cm'
        top = '0.5cm'
        bottom = '0.5cm'
        theme = 'blei'
        colortheme = 'default'
        fonttheme = 'professionalfonts'
        title = 'My presentaion'
        author = 'Yaroslav'
        institute = 'MSU'
        date = '\today'

        def __init__(self):
            self.fontsize = self.__class__.fontsize
            self.linespread = self.__class__.linespread
            self.left = self.__class__.left
            self.right = self.__class__.right
            self.top = self.__class__.top
            self.bottom = self.__class__.bottom
            self.theme = self.__class__.theme
            self.colortheme = self.__class__.colortheme
            self.fonttheme = self.__class__.fonttheme
            self.title = self.__class__.title
            self.author = self.__class__.author
            self.institute = self.__class__.institute
            self.date = self.__class__.date
            super().__init__()


    documentclass = 'article'

    def __init__(self):
        self.documentclass = self.__class__.documentclass
        self.article = self.__class__.Article()
        self.beamer = self.__class__.Beamer()
        super().__init__()


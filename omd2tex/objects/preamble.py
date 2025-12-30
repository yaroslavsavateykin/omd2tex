import json
import os
from typing import Dict, Any

from omd2tex.tools.globals import Global

from .base import BaseClass


class NewComands(BaseClass):
    @staticmethod
    def fill():
        """Return custom LaTeX command definitions for the preamble."""
        string = r"""

\newcommand{\dashboxed}[1]{%
    \tikz[baseline=(X.base)]\node[draw,dashed,inner sep=5pt] (X) {$#1$};%
}

\newcommand{\dotboxed}[1]{%
    \tikz[baseline=(X.base)]\node[draw,dotted,inner sep=5pt] (X) {$#1$};%
}

\newcommand{\ph}{\text{pH}}
\newcommand{\poh}{\text{pOH}}
\newcommand{\p}[1]{\text{p}\mathrm{#1}}
\newcommand{\chemb}[1]{\left[\ce{#1}\right]}
%\renewcommand{\ce}[1]{{\ce{#1}}}

\tcbuselibrary{breakable}

\newtcolorbox{breakableframe}{
    sharp corners,
    boxrule=0.5pt,
    colback=white,
    colframe=black,
    width=\linewidth,
    breakable=true,
    before upper={\parindent15pt}
}
"""
        string += "\n\n".join(Global.NEW_COMMANDS_PREAMBLE)

        return string


class Preamble(BaseClass):
    def __init__(self) -> None:
        """Initialize preamble builder with defaults."""
        super().__init__()
        # self.config = self._load_config()
        self.beamer_titlepage = False
        # SettingsPreamble.update(self.config)

    def _load_config(self) -> Dict[str, Any]:
        """Load preamble configuration from JSON file."""
        from ..tools import Settings
        from ..tools import SettingsPreamble

        if Settings.Preamble.settings_json:
            config_path = os.path.expanduser(Settings.Preamble.settings_json)
        else:
            config_path = (
                os.path.abspath(os.path.dirname(__file__)) + "/../default/preamble.json"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Некорректный JSON файл: {config_path}")

    def to_latex(self) -> str:
        """Generate LaTeX preamble string based on document class."""
        from ..tools import Settings
        from ..tools import SettingsPreamble

        documentclass = SettingsPreamble.documentclass

        if documentclass == "beamer":
            return self._generate_beamer_preamble()
        else:
            return self._generate_article_preamble()

    def _generate_article_preamble(self) -> str:
        """Compose LaTeX preamble for article documents."""
        from ..tools import Settings
        from ..tools import SettingsPreamble

        string = rf"""
\documentclass[{SettingsPreamble.Article.fontsize}]{{{SettingsPreamble.documentclass}}}
\linespread{{{SettingsPreamble.Article.linespread}}}
\usepackage{{mathtext}}

% Шрифты и кодировка
\usepackage[T2A]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{cmap}}
\usepackage{{textcomp}}
\usepackage[russian]{{babel}}
\usepackage{{extsizes}}

%------------------------------Packages---------------------------------

\usepackage{{geometry}}    % Настройка отступов
\usepackage[version = 4]{{mhchem}}      % Химические формулы через \ce{{}}   
\usepackage{{chemgreek}}

\usepackage{{xcolor}}      % Выделение цветом
\usepackage{{tcolorbox}}
\usepackage{{soul}}        % Выделение цветов
\usepackage{{pdflscape}}   % Для горизонтальной ориентации
\usepackage{{cancel}}      % Зачеркивание
\usepackage{{amsmath}}
\usepackage{{ulem}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{gensymb}}
\usepackage{{graphicx}}    % Вставка картинок 
\usepackage{{subcaption}}    % Подписи к картинкам 
\counterwithin{{subfigure}}{{figure}}
\usepackage{{caption}}
\captionsetup[figure]{{skip=1pt}}
\captionsetup[subfigure]{{skip=1pt}}
\captionsetup[table]{{skip=1pt}}
\captionsetup[longtblr]{{skip=1pt}}
\renewcommand{{\thesubfigure}}{{Рис \thefigure.\arabic{{figure}}.}} 
\usepackage{{floatrow}}
\usepackage{{underscore}}  % Чтобы подчеркивания нормально вставлялись
\usepackage{{svg}}
\usepackage{{collectbox}}

\usepackage[backend=biber, style=ieee]{{biblatex}}
\usepackage[hidelinks]{{hyperref}}
\usepackage[capitalize]{{cleveref}}
\crefname{{figure}}{{рис.}}{{рис.}}
\Crefname{{figure}}{{Рис.}}{{Рис.}}
\crefname{{subfigure}}{{рис.}}{{рис.}}
\Crefname{{subfigure}}{{Рис.}}{{Рис.}}
\crefname{{equation}}{{}}{{}}
\Crefname{{equation}}{{}}{{}}
\crefname{{longtblr}}{{табл.}}{{табл.}}
\Crefname{{longtblr}}{{Табл.}}{{Табл.}}
\crefname{{table}}{{табл.}}{{табл.}}
\Crefname{{table}}{{Табл.}}{{Табл.}}
\crefname{{section}}{{раздел}}{{раздел}}
\Crefname{{section}}{{Раздел}}{{Раздел}}
\crefname{{subsection}}{{подраздел}}{{подраздел}}
\Crefname{{subsection}}{{Подраздел}}{{Подраздел}}
\crefname{{subsubsection}}{{пункт}}{{пункт}}
\Crefname{{subsubsection}}{{Пункт}}{{Пункт}}

% Пакет для настройки заголовков
\usepackage{{titlesec}}
\titleformat{{\section}}
    {{\normalfont\Large\bfseries}}{{\thesection}}{{1em}}{{}}
\titleformat{{\subsection}}
    {{\normalfont\large\bfseries}}{{\thesubsection}}{{1em}}{{}}
\titleformat{{\subsubsection}}
    {{\normalfont\normalsize\bfseries}}{{\thesubsubsection}}{{1em}}{{}}

% Настройка отступов для заголовков
\titlespacing*{{\section}}{{0pt}}{{3.5ex plus 1ex minus .2ex}}{{2.3ex plus .2ex}}
\titlespacing*{{\subsection}}{{0pt}}{{3.25ex plus 1ex minus .2ex}}{{1.5ex plus .2ex}}
\titlespacing*{{\subsubsection}}{{0pt}}{{3.25ex plus 1ex minus .2ex}}{{1.5ex plus .2ex}}

\DeclareFieldFormat{{author}}{{\textit{{#1}}}}
\DeclareFieldFormat{{journaltitle}}{{#1}}
\DeclareFieldFormat{{title}}{{#1}}

\usepackage{{indentfirst}}
\usepackage{{minted}} % Выделение кода   

\usepackage{{tabularx,ragged2e}}
\usepackage{{float}}

\makeatletter
\newcommand{{\keepwithnext}}{{\@beginparpenalty 10000}}
\makeatother

% УСОВЕРШЕНСТВОВАННЫЕ ТАБЛИЦЫ
\usepackage{{tabularray}}
\UseTblrLibrary{{booktabs}}
\DefTblrTemplate{{contfoot-text}}{{default}}{{Продолжение на следующей странице}}
\DefTblrTemplate{{conthead-text}}{{default}}{{(Продолжение)}}

\usepackage{{tocbibind}}

% TIKZ
\usepackage{{pgfplots}}
\DeclareUnicodeCharacter{{2212}}{{−}}
\usepgfplotslibrary{{groupplots,dateplot}}
\usetikzlibrary{{patterns,shapes.arrows}}
\pgfplotsset{{compat=newest}}
\usetikzlibrary{{shapes.geometric, arrows, positioning}}
\tikzstyle{{block}} = [rectangle, draw, text centered, text width=10.5cm, minimum height=1.5cm, align=center]
\tikzstyle{{line}} = [draw, -latex']



%-------------------------------Settings--------------------------------

% Настройки отступов
\geometry{{
    a4paper, 
    left={SettingsPreamble.Article.left}, 
    right={SettingsPreamble.Article.right}, 
    top={SettingsPreamble.Article.top}, 
    bottom={SettingsPreamble.Article.bottom}
}}

% Настройки нумерации уравнений. 
% Честно, совсем не понимаю, как оно работает, и пусть.
%\numberwithin{{equation}}{{subsubsection}}

% В преамбуле


\usepackage{{xpatch}}
\xapptocmd\normalsize{{%
 \abovedisplayskip=-10pt plus 15pt minus 5pt
 \abovedisplayshortskip=-10pt plus 15pt minus 5pt
 \belowdisplayskip=3pt plus 5pt minus 5pt
 \belowdisplayshortskip=3pt plus 5pt minus 5pt
}}{{}}{{}}


% Adjust spacing for equation environment
\usepackage{{etoolbox}}
%\BeforeBeginEnvironment{{equation}}{{\vspace{{0pt}}}}
%\AfterEndEnvironment{{itemize}}{{\vspace{{-10pt}}}}


{NewComands.fill()}

%\let\oldsection\section% Store \section
%\renewcommand{{\section}}{{% Update \section
%  \renewcommand{{\theequation}}{{\thesection.\arabic{{equation}}}}% Update equation number
%  \oldsection}}% Regular \section
%\let\oldsubsection\subsection% Store \subsection
%\renewcommand{{\subsection}}{{% Update \subsection
%  \renewcommand{{\theequation}}{{\thesubsection.\arabic{{equation}}}}% Update equation number
%  \oldsubsection}}% Regular \subsubsection 
%\let\oldsubsubsection\subsubsection% Store \subsubsection 
%\renewcommand{{\subsubsection}}{{% Update \subsubsection 
%  \renewcommand{{\theequation}}{{\thesubsubsection.\arabic{{equation}}}}% Update equation number
%  \oldsubsubsection}}% Regular \subsubsection 


\tikzset{{>=latex}}
\definecolor{{mintgreen}}{{RGB}}{{220,255,220}}
\DeclareUnicodeCharacter{{202F}}{{\,}}
"""
        return string

    def _generate_beamer_preamble(self) -> str:
        """Compose LaTeX preamble for beamer presentations."""
        from ..tools import Settings
        from ..tools import SettingsPreamble

        title_line = (
            f"\\title{{{SettingsPreamble.Beamer.title}}}"
            if SettingsPreamble.Beamer.title
            else ""
        )
        author_line = (
            f"\\author{{{SettingsPreamble.Beamer.author}}}"
            if SettingsPreamble.Beamer.author
            else ""
        )
        institute_line = (
            f"\\institute{{{SettingsPreamble.Beamer.institute}}}"
            if SettingsPreamble.Beamer.institute
            else ""
        )
        date_line = (
            f"\\date{{{SettingsPreamble.Beamer.date}}}"
            if SettingsPreamble.Beamer.date
            else "\\setbeamertemplate{date}{}"
        )

        if any([title_line, author_line, institute_line, date_line]):
            self.beamer_titlepage = True

        # SettingsPreamble.Beamer.check()

        string = rf"""
\documentclass[{SettingsPreamble.Beamer.fontsize}]{{beamer}}

%-------------------------Basic Packages-----------------------------
%\usepackage{{mathtext}}
\usepackage[T2A]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage[russian]{{babel}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{graphicx}}
\usepackage{{isomath}}
\usepackage{{arevtext,arevmath}}

%\geometry{{
%    left={SettingsPreamble.Beamer.left}, 
%    right={SettingsPreamble.Beamer.right}, 
%    top={SettingsPreamble.Beamer.top}, 
%    bottom={SettingsPreamble.Beamer.bottom}
%}}

\setlength{{\topmargin}}{{-2cm}}
\setlength{{\headheight}}{{{SettingsPreamble.Beamer.top}}}
%\setlength{{\topmargin}}{{{SettingsPreamble.Beamer.top}}}
\setbeamersize{{text margin left={SettingsPreamble.Beamer.left}, text margin right={SettingsPreamble.Beamer.right}}}

%----------------------Scientific Packages---------------------------

\usepackage{{geometry}}    % Настройка отступов
\usepackage[version = 4]{{mhchem}}      % Химические формулы через \ce{{}}   
\usepackage{{chemgreek}}

\usepackage{{xcolor}}      % Выделение цветом
\usepackage{{tcolorbox}}
\usepackage{{soul}}        % Выделение цветов
\usepackage{{pdflscape}}   % Для горизонтальной ориентации
\usepackage{{cancel}}      % Зачеркивание
\usepackage{{ulem}}
\usepackage{{gensymb}}
\usepackage{{subcaption}}    % Подписи к картинкам 
\counterwithin{{subfigure}}{{figure}}
\usepackage{{caption}}
\captionsetup[figure]{{skip=1pt}}
\captionsetup[subfigure]{{skip=1pt}}
\captionsetup[table]{{skip=1pt}}
\captionsetup[longtblr]{{skip=1pt}}
\renewcommand{{\thesubfigure}}{{Рис \thefigure.\arabic{{figure}}.}} 
\usepackage{{floatrow}}
\usepackage{{underscore}}  % Чтобы подчеркивания нормально вставлялись
\usepackage{{svg}}
\usepackage{{collectbox}}

%\usepackage[backend=biber, style=ieee]{{biblatex}}
%\usepackage[hidelinks]{{hyperref}}
\usepackage[capitalize]{{cleveref}}
\crefname{{figure}}{{рис.}}{{рис.}}
\Crefname{{figure}}{{Рис.}}{{Рис.}}
\crefname{{subfigure}}{{рис.}}{{рис.}}
\Crefname{{subfigure}}{{Рис.}}{{Рис.}}
\crefname{{equation}}{{}}{{}}
\Crefname{{equation}}{{}}{{}}
\crefname{{longtblr}}{{табл.}}{{табл.}}
\Crefname{{longtblr}}{{Табл.}}{{Табл.}}
\crefname{{table}}{{табл.}}{{табл.}}
\Crefname{{table}}{{Табл.}}{{Табл.}}
\crefname{{section}}{{раздел}}{{раздел}}
\Crefname{{section}}{{Раздел}}{{Раздел}}
\crefname{{subsection}}{{подраздел}}{{подраздел}}
\Crefname{{subsection}}{{Подраздел}}{{Подраздел}}
\crefname{{subsubsection}}{{пункт}}{{пункт}}
\Crefname{{subsubsection}}{{Пункт}}{{Пункт}}

% Пакет для настройки заголовков
\usepackage{{titlesec}}

\usepackage[version=4]{{mhchem}}

\usepackage{{tabularray}}
\UseTblrLibrary{{booktabs}}
\DefTblrTemplate{{contfoot-text}}{{default}}{{Продолжение на следующей странице}}
\DefTblrTemplate{{conthead-text}}{{default}}{{(Продолжение)}}

{NewComands.fill()}

%----------------------Code Highlighting-----------------------------
\usepackage{{minted}}
\usepackage{{adjustbox}}
%----------------------Style Settings--------------------------------
\usetheme{{{SettingsPreamble.Beamer.theme}}}
\usecolortheme{{{SettingsPreamble.Beamer.colortheme}}}
%\usefonttheme{{{SettingsPreamble.Beamer.fonttheme}}}

\setbeamertemplate{{navigation symbols}}{{}} % Эта команда УДАЛЯЕТ все навигационные символы
\setbeamertemplate{{caption}}[numbered]
%----------------------Presentation Info-----------------------------

{title_line}
{author_line}
{institute_line}
{date_line}

"""
        return string

    def _to_latex_project(self):
        """Return preamble string for project export context."""
        return self.to_latex()

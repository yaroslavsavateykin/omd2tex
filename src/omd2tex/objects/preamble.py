import json
import os
from typing import Dict

from ..tools import Settings


class Preamble:
    def __init__(self) -> None:
        pass

    def to_latex(self):
        preamble = os.path.expanduser(Settings.Preamble.settings_json)

        with open(preamble) as f:
            preamble = json.load(f)

        string = rf"""
\documentclass[{preamble["fontsize"]}]{{{preamble["documentclass"]}}} % Дополнительные размеры
\linespread{{{preamble["linespread"]}}}
\usepackage{{mathtext}}

% Шрифты и кодировка
\usepackage[T2A]{{fontenc}}
\usepackage[utf8]{{inputenc}}
%\usepackage{{lmodern}} % Latin Modern (улучшенный Computer Modern)
%\renewcommand{{\ttdefault}}{{lmtt}} % Для моноширинного
%\usepackage[T1,T2A]{{fontenc}}
\usepackage{{cmap}}
\usepackage{{textcomp}}
\usepackage[russian]{{babel}}
\usepackage{{extsizes}}

%% Fonts
%\defaultfontfeatures{{Mapping=tex-text}}
%\setmainfont{{CMU Serif}}
%\setsansfont{{CMU Sans Serif}}
%\setmonofont{{CMU Typewriter Text}}

%------------------------------Packages---------------------------------$

\usepackage{{geometry}}    % Настрока отступов
\usepackage[version = 4]{{mhchem}}      % Химические формулы черех \ce{{}}   
\usepackage{{chemgreek}}

%\usepackage{{chemformula}}
%\NewCommandCopy{{\ce}}{{\ch}}
%\let\ch\relax

\usepackage{{xcolor}}      % Выделение цветом
\usepackage{{tcolorbox}}
\usepackage{{soul}}        % Выделение цветов
\usepackage{{pdflscape}}   % Для горизонтальной ориентации
\usepackage{{cancel}}      % Для горизонтальной ориентации
\usepackage{{amsmath}}
\usepackage{{ulem}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{gensymb}}
\usepackage{{graphicx}}    % Вставка картинок 
\usepackage{{subcaption}}    % Вставка картинок 
\counterwithin{{subfigure}}{{figure}}
\usepackage{{caption}}
\captionsetup[figure]{{skip=1pt}} % Уменьшает отступ (по умолчанию ~10pt)
\captionsetup[subfigure]{{skip=1pt}} % Уменьшает отступ (по умолчанию ~10pt)
\captionsetup[table]{{skip=1pt}} % Уменьшает отступ (по умолчанию ~10pt)
\captionsetup[longtblr]{{skip=1pt}} % Уменьшает отступ (по умолчанию ~10pt)
\renewcommand{{\thesubfigure}}{{Рис \thefigure.\arabic{{figure}}.}} 
\usepackage{{floatrow}}  % Чтобы подчеркивания нормально вставлялись вне окружения математики
\usepackage{{underscore}}  % Чтобы подчеркивания нормально вставлялись вне окружения математики
%\usepackage{{hyphenat}}  % улучшает алгоритм переносов
\usepackage{{svg}}
%\pagestyle{{empty}}
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
% Настройка стилей заголовков как в стандартном article
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
%\DeclareFieldFormat{{url}}{{}}
%\DeclareFieldFormat{{doi}}{{}}

%\usepackage{{hyperref}}

\usepackage{{indentfirst}}

% Чтобы minted сохрагял все там, где нужно
%\usepackage{{currfile-abspath}}
%\usepackage{{ifthen}}
%\getabspath{{\jobname.log}}
%\ifthenelse{{\equal{{\theabsdir}}{{\thepwd}}}}% using ifthen package
%\ifdefstrequal{{\theabsdir}}{{\thepwd}}% using etoolbox package
%    {{}}{{\PassOptionsToPackage{{outputdir=../created_files}}{{minted}}}}

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

%\usepackage{{fancyvrb}}
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

% Заголовки
%\usepackage{{titlesec}}

%\titleformat{{\section}}{{\normalfont\Large\bfseries}}{{\thesection}}{{1em}}{{}}
%\titlespacing*{{\section}}{{0pt}}{{3.5ex plus 1ex minus .2ex}}{{2.3ex plus .2ex}}
%\titlespacing*{{\subsection}}{{0pt}}{{3.5ex plus 1ex minus .2ex}}{{2.3ex plus .2ex}}
%\titlespacing*{{\subsubsection}}{{0pt}}{{3.5ex plus 1ex minus .2ex}}{{2.3ex plus .2ex}}

%-------------------------------Settings--------------------------------%

% Настройки отступов
\geometry{{
    a4paper, 
    left={preamble["left"]}, 
    right={preamble["right"]}, 
    top={preamble["top"]}, 
    bottom={preamble["bottom"]}
    }}

% Настройки нумерации уравнений. 
% Честно, совсем не понимаю, как оно работает, и пусть.
%\numberwithin{{equation}}{{subsubsection}}

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

\newtcolorbox{{box1}}{{
  colframe=black, % Цвет рамки
  colback=white, % Цвет фона
  arc=3pt, % Закругление углов
  boxrule=0.5pt, % Толщина основной линии рамки
  boxsep=5pt, % Отступ внутри блока
  left=10pt, % Отступ слева
  right=10pt, % Отступ справа
  top=5pt, % Отступ сверху
  bottom=5pt, % Отступ снизу
  %before upper={{\begin{{quote}}}}, % Начинаем окружение quote
  %after upper={{\end{{quote}}}}, % Заканчиваем окружение quote
  enlarge left by=0pt, % Убираем лишний отступ слева
  enlarge right by=0pt, % Убираем лишний отступ справа
  width=\linewidth-60pt, % Ширина коробки равна ширине строки
  before=\vspace{{5pt}}, % Отступ перед коробкой
  after=\vspace{{5pt}} % Отступ после коробки
}}

\definecolor{{mintgreen}}{{RGB}}{{220,255,220}}

\DeclareUnicodeCharacter{{202F}}{{\,}}
"""
        return string

    def _to_latex_project(self, settings={}):
        """
        with open(self.parrentdir + "/" + "preamble.tex", "w") as f:

            f.write(self.to_latex())

        return f"\\include{{preabmble.tex}}"
        """

        return self.to_latex()

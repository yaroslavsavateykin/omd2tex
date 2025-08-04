import json
import os
import shutil 

from .preamble import Preamble
from .file import File

GLOBAL_REFERENCE_DICT = {}

class Document():

    def __init__(self, 
                 filename: str, 
                 settings = "default/settings.json", 
                 preamble = "default/preamble.json"):

        self.filename = filename  
        
        with open(settings, "r") as f: self.settings = json.load(f)

        if self.settings["preamble"]:
            with open(preamble, "r") as f: self.preamble = Preamble(json.load(f))
        else:
            self.preamble = ""


    def to_latex(self):
    
        if self.preamble:
            preamble = self.preamble.to_latex()
        else:
            preamble = ""

        file = File(self.filename, self.settings).to_latex()

        document = rf"""
{preamble}

\begin{{document}}

{file}

\end{{document}}"""

        return document
    
    
    def to_latex_file(self, filename: str = "") -> None:

        file = self.to_latex()

        if filename:
            print()
        else:
            filename = self.filename.strip(".md") + ".tex"
    
        #with open(os.getcwd() + "/" + filename, "w") as f:
        dir = self.settings["output_dir"]
        dir = os.path.expanduser(dir.strip("/") if dir.endswith("/") else dir) 
        with open(dir + "/" + filename, "w") as f:

            f.write(file)

        if self.settings["makefile"]:
            shutil.copy2("default/Makefile", dir)

    def to_latex_porject(self, 
                         filename = "") -> None:
        a = 1



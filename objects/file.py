from .markdownparser import MarkdownParser
from tools.attach_reference import attach_reference 


class File:

    def __init__(self, 
                 filename: str, 
                 settings: dict,
                 depth: int = 0,
                 parrentfilename: str = "") -> None:
        
        self.filename = filename
        self.parrentfilename = parrentfilename
        self.settings = settings
        self.depth = depth

        self.elements = MarkdownParser(filename, settings, depth).parse() 

    def to_latex(self, settings = {}):
        
        #print(len(self.elements))
        print(self.elements)
        
        elements = attach_reference(self.elements) 

        #print(len(elements))
        #print(elements)

        text = "\n\n".join([elem.to_latex(self.settings) for elem in elements])
        
        
        return text


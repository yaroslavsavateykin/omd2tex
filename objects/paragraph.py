import re
import json

class Paragraph:

    def __init__(self, 
                 text: str) -> None:
        
        self.text = self._parse_text(text)

        self.reference = None    

    def to_latex(self, settings = {}):

        return self.text
    
    def to_latex_project(self,
                         settings = {}):

        return self.to_latex(settings)
    
    @staticmethod
    def _change_letters_for_equations(text, 
                                      dict_file = "default/formulas4equations.json"):
        
        with open(dict_file, "r") as f:
            change_dict = json.load(f)
        

        for key in change_dict:
    
            text = text.replace(key, change_dict[key])

        return text 

    def _parse_text(self, text: str) -> str:
        
        print(text)
        
        
        text = re.sub(r"\$(?:[^$\\]|\\\$|\\[^$])*?\$", 
                      lambda x: f"${self._change_letters_for_equations(x.group(0).strip("$"))}$", 
                      text)
        

        print(text)


        return text


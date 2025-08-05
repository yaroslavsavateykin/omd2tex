class Equation:

    

    def __init__(self, 
                 equation: str) -> None:
        
        self.equation = equation

        self.reference = None 

    def to_latex(self, 
                 settings = {}):
        from .document import GLOBAL_REFERENCE_DICT
        global GLOBAL_REFERENCE_DICT
        

        if self.reference:

            GLOBAL_REFERENCE_DICT[self.reference] = "eq"
            
            equation = rf"""
\begin{{equation}}
{self.equation}
\label{{eq:{self.reference}}}
\end{{equation}}
"""     
        else:
             
            equation = rf"""
\begin{{equation*}}
{self.equation}
\end{{equation*}}
"""     
        return equation

    def to_latex_project(self, 
                         settings = {}):

        return self.to_latex(settings)
        

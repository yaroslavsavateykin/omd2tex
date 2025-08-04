class Paragraph:

    def __init__(self, text) -> None:
        
        self.text = text

        self.reference = None    

    def to_latex(self, settings = {}):

        return self.text


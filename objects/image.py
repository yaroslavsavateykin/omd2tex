
from PIL import Image as PillowImage

from tools.search import find_file

class Image:

    def _get_image_dimensions(self):
        try:
            with PillowImage.open(self.dir) as img:
                return img.width, img.height
        except FileNotFoundError:
            return None, None

    def __init__(self, 
                 filename: str,
                 parrentfilename: str,
                 caption = "",
                 width = None, 
                 height = None,
                 settings = {}) -> None:
        
        self.filename = filename
        self.parrentfilename = parrentfilename
        
        self.dir = find_file(filename, 
                             settings = settings["dir"])

        self.caption = caption

        if not width and not height:
            
            self.width, self.hight = self._get_image_dimensions() 
         

        self.reference = None
       

class 

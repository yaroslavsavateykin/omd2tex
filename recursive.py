from os import rmdir
from omd2tex.objects import Document
from omd2tex.tools import ErrorCompileCatcher, Settings

Settings.Export.search_dir ="~/vzlet_vault/" 

#doc = Document().from_file("Исследование кинетики ферментативной реакции.md")
doc = Document().from_file("2025-11-20.md")
#doc = Document().from_file("Практикум.md")
# doc = Document().from_file("Методичка.md")
# doc = Document().from_file("2025-10-21.md")
# doc = Document().from_file("газовая фаза.md")




a = ErrorCompileCatcher(doc)

a.analyze( total_errors=10)

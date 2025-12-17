from omd2tex.tools.database import MdDataBase
from omd2tex.tools.settings import Settings

Settings.Export.search_dir = "~/vzlet_vault/"

md_db = MdDataBase(search_path="~/vzlet_vault/Взлёт/База задач/")


md_db.to_df().to_csv("test.csv")

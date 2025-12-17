import pandas as pd
import os

from .settings import Settings
from .frontmatter_parser import FrontMatterParser


class MdDataBase:
    def __init__(self, search_path=None) -> None:
        if search_path is None:
            self.search_path = Settings.Export.search_dir
        else:
            self.search_path = search_path

        self.search_path = os.path.expanduser(self.search_path)

    # @property
    def to_df(self):
        all_dict = []

        for root, dirs, files in os.walk(self.search_path):
            if any(dir in Settings.Export.search_ignore_dirs for dir in dirs):
                continue

            for file in files:
                if not file.endswith(".md"):
                    continue
                abs_file = os.path.join(root, file)
                fmp = FrontMatterParser(abs_path=abs_file)
                fmp_dict = fmp.yaml
                fmp_dict["filename"] = file
                fmp_dict["abs_path"] = abs_file

                all_dict.append(fmp_dict)

        return pd.DataFrame(all_dict)

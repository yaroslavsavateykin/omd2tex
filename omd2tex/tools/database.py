import pandas as pd
import os

from .settings import Settings
from .frontmatter_parser import FrontMatterParser


class MdDataBase:
    def __init__(self, search_path: str = None) -> None:
        """Create a markdown database scanner over a search path.

        Args:
            search_path: Root directory to traverse; defaults to ``Settings.Export.search_dir`` when None.

        Returns:
            None
        """
        if search_path is None:
            self.search_path = Settings.Export.search_dir
        else:
            self.search_path = search_path

        self.search_path = os.path.expanduser(self.search_path)

    # @property
    def to_df(self) -> pd.DataFrame:
        """Collect frontmatter from markdown files into a DataFrame.

        Walks the search path, parses frontmatter of each ``.md`` file, and aggregates metadata into a pandas DataFrame.

        Args:
            None

        Returns:
            pandas.DataFrame containing one row per markdown file with frontmatter fields plus filename and absolute path.

        Side Effects:
            Reads files from disk.
        """
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

from objects.document import Document
from tools.settings import Settings


def main():
    with open("default/current", "r") as f:
        filename = f.read().strip()

    Settings.Export.search_dir = "~/Vzlet/"
    Settings.Export.export_dir = "~/omd2tex/test/"

    doc = Document(filename)

    # Settings.check()

    # doc.check()
    doc.to_latex_porject()


if __name__ == "__main__":
    main()

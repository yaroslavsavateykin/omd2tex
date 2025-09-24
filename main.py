from omd2tex.tools.globals import Global


def time(func):
    def wrapper(*args, **kwargs):
        import time

        start = time.time()

        r = func(*args, **kwargs)
        end = time.time()
        print(f"Time used: {(end - start):.2f} seconds")
        return r

    return wrapper


@time
def main():
    from omd2tex.objects.document import Document
    from omd2tex.tools.settings import Settings

    with open("omd2tex/default/current", "r") as f:
        filename = f.read().strip()

    Settings.Export.search_dir = "~/vzlet_vault/"
    Settings.Export.export_dir = "~/omd2tex/test_projects/"
    Settings.Paragraph.latinify = False
    Settings.Headline.clean_markdown_numeration = True

    filename = "Методичка.md"
    filename = "2025-09-17.md"

    doc = Document()
    doc.from_file(filename)

    # Settings.Export.check()

    # doc.check()
    Global.check()
    doc.to_latex_project()


if __name__ == "__main__":
    main()

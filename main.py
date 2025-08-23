from objects.headline import Headline


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
    from objects.document import Document
    from tools.settings import Settings

    with open("default/current", "r") as f:
        filename = f.read().strip()

    Settings.Export.search_dir = "~/Vzlet/"
    Settings.Export.export_dir = "~/omd2tex/test/"

    doc = Document()
    doc.from_file(filename)

    # Settings.Export.check()

    # doc.check()
    doc.to_latex_project()


if __name__ == "__main__":
    main()

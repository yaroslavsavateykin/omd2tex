from objects.document import Document


def main():
    with open("default/current", "r") as f:
        filename = f.read().strip()

    doc = Document(filename)

    doc.to_latex_porject()


if __name__ == "__main__":
    main()

from objects.document import GLOBAL_REFERENCE_DICT, Document

def main():
 
    with open("default/current.md", "r") as f: 
        
        filename = f.read().strip() 

    doc = Document(filename)

    text = doc.to_latex()

    doc.to_latex_file("test.tex")

    print(text)


if __name__ == "__main__":

    main()

    print(GLOBAL_REFERENCE_DICT)

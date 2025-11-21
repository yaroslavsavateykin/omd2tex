from ..tools.frontmatter_parser import FrontMatterParser


filename = "test.md"

a = FrontMatterParser(filename=filename)

print(a.yaml)

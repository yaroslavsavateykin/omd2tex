import pytest

from omd2tex import File

file = File().from_text("# File test")
print(file.to_latex())

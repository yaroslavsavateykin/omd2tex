from setuptools import setup, find_packages


def parse_requirements(filename):
    requirements = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    line
                    and not line.startswith("#")
                    and not line.startswith("-e")
                    and not line.startswith("git+")
                ):
                    if "#" in line:
                        line = line.split("#")[0].strip()
                    if line:
                        requirements.append(line)
    except FileNotFoundError:
        print("requirements.txt not found, using minimal dependencies")
        requirements = ["numpy", "PyYAML"]
    return requirements


def find_additional_files(directory):
    result = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            result.append(os.path.join(root, file))
    return result


setup(
    name="omd2tex",
    version="0.1.0",
    description="Markdown to LaTeX converter specicified on using in Obsidian",
    author="Savateykin Yaroslav",
    author_email="yaroslavsavateykin@yandex.ru",
    package_dir={"omd2tex": "omd2tex"},
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=parse_requirements("requirements.txt"),
    package_data={"omd2tex": ["default/*.json", "default/beamer-themes/*.sty"]},
    include_package_data=True,
)

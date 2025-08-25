from setuptools import setup, find_packages


def parse_requirements(filename):
    """Парсит requirements.txt, исключая editable installs и комментарии"""
    requirements = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Пропускаем пустые строки, комментарии и editable installs
                if (
                    line
                    and not line.startswith("#")
                    and not line.startswith("-e")
                    and not line.startswith("git+")
                ):
                    # Убираем inline комментарии
                    if "#" in line:
                        line = line.split("#")[0].strip()
                    if line:
                        requirements.append(line)
    except FileNotFoundError:
        print("requirements.txt not found, using minimal dependencies")
        requirements = ["numpy", "PyYAML"]
    return requirements


setup(
    name="omd2tex",
    version="0.1.0",
    description="Markdown to LaTeX converter specicified on using in Obsidian",
    author="Savateykin Yaroslav",
    author_email="yaroslavsavateykin@yandex.ru",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=parse_requirements("requirements.txt"),
)

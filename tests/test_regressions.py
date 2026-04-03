import datetime
import json

import pytest
import yaml
from PIL import Image as PillowImage

from omd2tex.objects.citation import Citation
from omd2tex.objects.document import Document
from omd2tex.objects.file import File
from omd2tex.objects.footnote import Footnote
from omd2tex.objects.fragment import Caption, SplitLine
from omd2tex.objects.image import Image as MdImage
from omd2tex.objects.paragraph import Paragraph
from omd2tex.objects.preamble import Preamble
from omd2tex.objects.quote import Quote
from omd2tex.objects.reference import Reference
from omd2tex.tools.config_base import ConfigBase
from omd2tex.tools.frontmatter_parser import FrontMatterParser
from omd2tex.tools.globals import Global
from omd2tex.tools.markdown_parser import MarkdownParser
from omd2tex.tools.settings import Settings
from omd2tex.tools.settings_preamble import SettingsPreamble


@pytest.fixture(autouse=True)
def reset_state():
    Settings.to_default()
    SettingsPreamble.to_default()
    Global.to_default()
    yield
    Settings.to_default()
    SettingsPreamble.to_default()
    Global.to_default()


def test_config_to_default_restores_nested_defaults():
    class Demo(ConfigBase):
        value = 1

        class Nested(ConfigBase):
            value = 10

    Demo.value = 2
    Demo.Nested.value = 20

    Demo.to_default()

    assert Demo.value == 1
    assert Demo.Nested.value == 10


def test_frontmatter_handles_empty_blank_and_unterminated_input():
    assert FrontMatterParser(text=[]).yaml == {}

    blank = FrontMatterParser(text="---\n\n---\nbody")
    assert blank.yaml == {}
    assert blank.yaml_line_end == 3

    parser = MarkdownParser().from_text("---\n\n---\nbody")
    assert [type(el).__name__ for el in parser.elements] == ["Paragraph"]
    assert parser.elements[0].text == "body"

    unterminated = FrontMatterParser(text="---\na: 1\nbody")
    assert unterminated.yaml == {}
    assert unterminated.yaml_line_end == 0


def test_frontmatter_loader_does_not_modify_global_yaml_safe_loader():
    loaded = yaml.safe_load("date: 2024-01-02\n")
    assert loaded["date"] == datetime.date(2024, 1, 2)


def test_frontmatter_obsidian_keys_update_preamble_settings():
    MarkdownParser().from_text("---\narticle.left: 9cm\ndocumentclass: beamer\n---\ntext")

    assert SettingsPreamble.Article.left == "9cm"
    assert SettingsPreamble.documentclass == "beamer"


def test_markdown_parser_handles_file_and_image_lines_without_sticky_state(tmp_path):
    PillowImage.new("RGB", (10, 20), "red").save(tmp_path / "pic.png")
    Settings.Export.search_dir = str(tmp_path)

    parser = MarkdownParser().from_text("[[note]]\n![[pic.png]]\n[x](other.md)")

    assert [type(el).__name__ for el in parser.elements] == ["File", "Image", "File"]
    assert parser.elements[0].filename == "note.md"
    assert parser.elements[2].filename == "other.md"


def test_markdown_parser_from_elements_runs_post_processing():
    parser = MarkdownParser().from_elements(
        [Paragraph("text"), Reference("ref123"), Caption("cap")]
    )

    assert len(parser.elements) == 1
    assert parser.elements[0].reference == "ref123"
    assert parser.elements[0].caption == "cap"


def test_image_explicit_size_and_project_export_keep_source_path(tmp_path):
    source = tmp_path / "src.png"
    PillowImage.new("RGB", (100, 200), "red").save(source)
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    image = MdImage(
        filename="src.png",
        parrentdir=str(project_dir),
        dir=str(source),
        width=50,
        height=100,
    )

    latex = image.to_latex()
    assert "width = {0.5}\\textwidth" in latex
    assert "height = {0.5}\\textheight" in latex

    latex_project = image._to_latex_project()
    assert "./images/src.png" in latex_project
    assert (project_dir / "images" / "src.png").exists()
    assert image.dir == str(source)


def test_image_project_export_refinds_missing_source_by_filename(tmp_path):
    source_root = tmp_path / "vault"
    source_root.mkdir()
    source = source_root / "src.png"
    PillowImage.new("RGB", (20, 40), "blue").save(source)

    project_dir = tmp_path / "project"
    project_dir.mkdir()
    Settings.Export.search_dir = str(source_root)

    image = MdImage(filename="src.png", parrentdir=str(project_dir), dir=str(source))
    image.source_dir = str(tmp_path / "missing.png")

    image._to_latex_project()

    assert (project_dir / "images" / "src.png").exists()


def test_beamer_preamble_loads_tikz_and_keeps_last_frame():
    SettingsPreamble.documentclass = "beamer"

    preamble = Preamble().to_latex()
    assert "\\usepackage{tikz}" in preamble
    assert preamble.index("\\usepackage{tikz}") < preamble.index(
        "\\usetikzlibrary{arrows.meta, positioning}"
    )

    frames = SplitLine.make_beamer([SplitLine("Title"), Paragraph("Body")])
    assert len(frames) == 1
    assert frames[0].title == "Title"
    assert frames[0].elements[0].text == "Body"


def test_preamble_settings_json_updates_from_obsidian_style_json(tmp_path):
    config_path = tmp_path / "preamble.json"
    config_path.write_text(
        json.dumps(
            {
                "documentclass": "beamer",
                "beamer.theme": "Madrid",
                "beamer.title": "Deck",
                "article.left": "7cm",
            }
        ),
        encoding="utf-8",
    )

    Settings.Preamble.settings_json = str(config_path)

    preamble = Preamble().to_latex()

    assert SettingsPreamble.documentclass == "beamer"
    assert SettingsPreamble.Beamer.theme == "Madrid"
    assert SettingsPreamble.Beamer.title == "Deck"
    assert SettingsPreamble.Article.left == "7cm"
    assert "\\usetheme{Madrid}" in preamble


def test_document_and_file_avoid_previous_none_branches(tmp_path):
    Settings.Export.export_dir = str(tmp_path)
    Settings.Preamble.create_preamble = False

    latex = Document().from_text("hello").to_latex()
    assert "\\begin{document}" in latex

    child = File()
    document = Document().from_elements([child])
    assert isinstance(document.file.elements[0], File)
    assert document.file.elements[0].parrentdir

    Settings.Export.branching_project = True
    exported = File().from_text("hello")._to_latex_project()
    assert exported.startswith("\\input{")


def test_missing_citation_and_global_reset_are_safe(tmp_path):
    Settings.Export.search_dir = str(tmp_path)

    citation = Citation("@missing")
    assert citation.to_latex() == ""
    assert Citation.to_latex_preamble() == ""

    Footnote.collection["x"] = "note"
    Global.to_default()

    assert Citation.citation_list == []
    assert Footnote.collection == {}


def test_quote_type_is_case_insensitive():
    task = Quote.create(["> [!Task] Build", "> body"])
    upper = Quote.create(["> [!TASK] Build", "> body"])
    lower = Quote.create(["> [!task] Build", "> body"])

    assert task.to_latex() == upper.to_latex() == lower.to_latex()


def test_task_quote_uses_numbered_environment_by_default():
    preamble = Preamble().to_latex()
    task = Quote.create(["> [!task] Build", "> body"])

    assert "\\newcounter{exercise}[section]" in preamble
    assert "\\renewcommand{\\theexercise}{\\thesection.\\arabic{exercise}}" in preamble
    assert "\\newenvironment{exercise}" in preamble
    assert "\\begin{breakableframe}" in task.to_latex()
    assert "\\begin{exercise}" in task.to_latex()


def test_task_quote_rule_is_customizable():
    Settings.Quote.task_preamble = r"\newtheorem{exercise}{Упражнение}"
    Settings.Quote.task_rule = r"\begin{exercise}[%(title)s]" "\n%(content)s\n" r"\end{exercise}"

    preamble = Preamble().to_latex()
    task = Quote.create(["> [!task] Custom title", "> body"])

    assert "\\newtheorem{exercise}{Упражнение}" in preamble
    assert "\\begin{exercise}[Custom title]" in task.to_latex()

import datetime
import json
import re

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


def test_task_quote_can_be_referenced_via_cref():
    text = (
        "> [!task]\n"
        "> Тело упражнения\n"
        "^ex0001\n\n"
        "См. [[#^ex0001|упражнение]].\n"
    )

    latex = Document().from_text(text).to_latex()

    assert "\\label{exercise:ex0001}" in latex
    assert "\\cref{exercise:ex0001}" in latex


def test_cross_file_block_reference_with_filename_prefix(tmp_path):
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()

    (sub_dir / "b.md").write_text("$$x = 1$$\n^eq1111\n", encoding="utf-8")
    (tmp_path / "root.md").write_text(
        "![[sub/b.md]]\nСм. [[sub/b#^eq1111|формулу]] и [[b#^eq1111|еще раз]].\n",
        encoding="utf-8",
    )

    Settings.Export.search_dir = str(tmp_path)
    latex = Document().from_file("root.md").to_latex()

    assert latex.count("\\cref{eq:eq1111}") == 2


def test_task_quote_reference_resolves_when_target_is_below():
    text = (
        "> [!task]\n"
        "> См. [[#^eq123|уравнение]]\n\n"
        "$$x = 1$$\n"
        "^eq123\n"
    )

    latex = Document().from_text(text).to_latex()

    assert "\\cref{eq:eq123}" in latex


def test_image_inside_quote_is_parsed_as_image(tmp_path):
    image_path = tmp_path / "pic.png"
    PillowImage.new("RGB", (16, 16), "red").save(image_path)
    Settings.Export.search_dir = str(tmp_path)

    latex = Document().from_text("> [!task]\n> ![[pic.png]]\n").to_latex()

    assert "\\includegraphics" in latex
    assert "pic.png" in latex


# ──────────────────────────────────────────────────────────────────────
# Path resolution tests
# ──────────────────────────────────────────────────────────────────────

from omd2tex.tools.path_utils import (
    export_project_name,
    normalize_export_dir,
    package_default_dir,
    stem_md,
)
from omd2tex.tools.search import find_file


def test_stem_md_removes_suffix_correctly():
    """stem_md must remove the literal '.md' suffix, NOT strip characters."""
    assert stem_md("damage.md") == "damage"
    assert stem_md("readme") == "readme"
    assert stem_md("a.md") == "a"
    assert stem_md(".md") == ""
    assert stem_md("my.module.md") == "my.module"
    # Old code used strip(".md") which would break these:
    assert stem_md("dim.md") == "dim"     # strip(".md") → ""
    assert stem_md("mad.md") == "mad"     # strip(".md") → ""


def test_find_file_absolute_path_inside_search_dir(tmp_path):
    """Absolute paths inside the configured vault remain supported."""
    f = tmp_path / "note.md"
    f.write_text("hello", encoding="utf-8")
    Settings.Export.search_dir = str(tmp_path)

    result = find_file(str(f))
    assert result == str(f)


def test_find_file_rejects_paths_outside_search_dir(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("secret", encoding="utf-8")
    source = vault / "note.md"
    source.write_text("body", encoding="utf-8")
    Settings.Export.search_dir = str(vault)

    assert find_file(str(outside)) is None
    assert find_file("../outside.md", source_dir=str(vault)) is None


def test_find_file_source_relative(tmp_path):
    """When source_dir is given, resolve paths relative to it first."""
    sub = tmp_path / "sub"
    sub.mkdir()
    target = sub / "b.md"
    target.write_text("body", encoding="utf-8")

    Settings.Export.search_dir = str(tmp_path)

    # Without source_dir — finds by basename walk
    result1 = find_file("b.md", source_dir=None)
    assert result1 is not None
    assert result1.endswith("b.md")

    # With source_dir — resolves relative to source directory
    result2 = find_file("b.md", source_dir=str(sub))
    assert result2 is not None
    assert result2.endswith("b.md")

    # Subdirectory path relative to source_dir
    result3 = find_file("sub/b.md", source_dir=str(tmp_path))
    assert result3 is not None
    assert result3.endswith("b.md")


def test_find_file_parent_traversal_stays_inside_search_dir(tmp_path):
    """Parent components are allowed only when their target remains in the vault."""
    parent = tmp_path / "parent"
    parent.mkdir()
    child = parent / "child"
    child.mkdir()
    sibling = parent / "sibling"
    sibling.mkdir()
    target = sibling / "note.md"
    target.write_text("content", encoding="utf-8")

    Settings.Export.search_dir = str(tmp_path)

    result = find_file("../sibling/note.md", source_dir=str(child))
    assert result is not None
    assert result.endswith("note.md")


def test_find_file_fallback_basename(tmp_path):
    """When source_dir doesn't contain the file, fall back to basename walk."""
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    target = deep / "hidden.md"
    target.write_text("found", encoding="utf-8")

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    Settings.Export.search_dir = str(tmp_path)

    # source_dir doesn't have it, but walk finds it
    result = find_file("hidden.md", source_dir=str(empty_dir))
    assert result is not None
    assert result.endswith("hidden.md")


def test_find_file_not_found_diagnostic(tmp_path, capsys):
    """Not-found diagnostic should include search context."""
    empty = tmp_path / "empty"
    empty.mkdir()
    Settings.Export.search_dir = str(empty)

    result = find_file("nonexistent.md", source_dir=str(tmp_path))
    assert result is None

    captured = capsys.readouterr()
    assert "nonexistent.md" in captured.out
    assert "not found" in captured.out.lower()


def test_find_file_same_name_different_dirs(tmp_path):
    """source_dir should give priority to the local copy."""
    dir_a = tmp_path / "a"
    dir_a.mkdir()
    (dir_a / "note.md").write_text("A version", encoding="utf-8")

    dir_b = tmp_path / "b"
    dir_b.mkdir()
    (dir_b / "note.md").write_text("B version", encoding="utf-8")

    Settings.Export.search_dir = str(tmp_path)

    result = find_file("note.md", source_dir=str(dir_a))
    assert result is not None
    assert "/a/" in result  # should resolve to dir_a, not arbitrary walk order


def test_package_default_dir_points_to_real_directory():
    """package_default_dir() must point to the existing default/ directory."""
    p = package_default_dir()
    assert p.is_dir()
    assert (p / "settings.json").is_file()


def test_normalize_export_dir_strips_trailing_slash():
    """normalize_export_dir should handle trailing slashes and ~."""
    result = normalize_export_dir("./output/")
    assert not result.endswith("/")
    result2 = normalize_export_dir("./output")
    assert result == result2


def test_export_project_name_cannot_escape_export_dir():
    assert export_project_name("nested/note.md") == "note"
    assert export_project_name("/tmp/note.md") == "note"
    assert export_project_name(r"nested\\note.md") == "note"
    with pytest.raises(ValueError):
        export_project_name(".md")


def test_document_project_export_uses_safe_basename(tmp_path):
    source = tmp_path / "vault" / "nested"
    source.mkdir(parents=True)
    note = source / "note.md"
    note.write_text("body", encoding="utf-8")
    export = tmp_path / "export"
    Settings.Export.search_dir = str(tmp_path / "vault")
    Settings.Export.export_dir = str(export)

    Document().from_file(str(note)).to_latex_project()

    assert (export / "note" / "main.tex").is_file()
    assert not (source / "note.tex").exists()


def test_document_file_export_rejects_output_path_escape(tmp_path):
    Settings.Export.export_dir = str(tmp_path / "export")

    Document().from_text("body").to_latex_file("../outside.tex")

    assert (tmp_path / "export" / "outside.tex").is_file()
    assert not (tmp_path / "outside.tex").exists()


def test_find_file_resolves_from_source_file_context(tmp_path):
    """End-to-end: file references should resolve relative to the referring file."""
    vault = tmp_path / "vault"
    vault.mkdir()
    sub = vault / "sub"
    sub.mkdir()
    (sub / "included.md").write_text("included content", encoding="utf-8")
    (vault / "root.md").write_text("![[sub/included]]", encoding="utf-8")

    Settings.Export.search_dir = str(vault)

    doc = Document().from_file("root.md")
    # The included file should have been found and parsed
    latex = doc.to_latex()
    assert "included content" in latex


def test_nested_file_references_resolve_relative_to_including_file(tmp_path):
    vault = tmp_path / "vault"
    (vault / "chapter" / "nested").mkdir(parents=True)
    (vault / "root.md").write_text("![[chapter/a]]", encoding="utf-8")
    (vault / "chapter" / "a.md").write_text(
        "![[nested/target]]", encoding="utf-8"
    )
    (vault / "chapter" / "nested" / "target.md").write_text(
        "correct nested file", encoding="utf-8"
    )
    (vault / "target.md").write_text("wrong global match", encoding="utf-8")
    Settings.Export.search_dir = str(vault)

    latex = Document().from_file("root.md").to_latex()

    assert "correct nested file" in latex
    assert "wrong global match" not in latex


def test_duplicate_headings_receive_distinct_labels():
    latex = Document().from_text("# Same\n\n# Same").to_latex()

    labels = re.findall(r"\\label\{sec:(head_[^}]+)\}", latex)
    assert len(labels) == 2
    assert len(set(labels)) == 2


def test_escaped_wiki_reference_is_rendered_as_literal_text():
    latex = Document().from_text(r"\[[note#^missing]]").to_latex()

    assert "\\cref{" not in latex
    assert r"[[note\#^missing]]" in latex

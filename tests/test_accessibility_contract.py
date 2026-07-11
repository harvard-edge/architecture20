from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

import pytest
import yaml

import cli.arch2 as arch2_cli


def _write_minimal_epub(path: Path, language: str) -> None:
    content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:language>{language}</dc:language>
  </metadata>
</package>
"""
    chapter = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
  <body><div class="callout-learning-objectives">Content</div></body>
</html>
"""
    with zipfile.ZipFile(path, "w") as epub:
        epub.writestr("EPUB/content.opf", content_opf)
        epub.writestr("EPUB/text/ch001.xhtml", chapter)


def test_epub_metadata_rejects_process_locale(tmp_path: Path) -> None:
    epub_path = tmp_path / "invalid-language.epub"
    _write_minimal_epub(epub_path, "C")

    findings = arch2_cli.epub_findings(epub_path)

    assert any(finding.code == "epub-language" for finding in findings)


def test_epub_metadata_accepts_bcp47_language(tmp_path: Path) -> None:
    epub_path = tmp_path / "valid-language.epub"
    _write_minimal_epub(epub_path, "en-US")

    findings = arch2_cli.epub_findings(epub_path)

    assert not any(finding.code == "epub-language" for finding in findings)


def test_epub_rejects_literal_fenced_div_markers(tmp_path: Path) -> None:
    epub_path = tmp_path / "literal-fence.epub"
    _write_minimal_epub(epub_path, "en-US")
    with zipfile.ZipFile(epub_path, "a") as epub:
        epub.writestr(
            "EPUB/text/ch002.xhtml",
            '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>:::</p></body></html>',
        )

    findings = arch2_cli.epub_findings(epub_path)

    assert any(finding.code == "epub-literal-fenced-div" for finding in findings)


@pytest.mark.parametrize("tag", ["code", "kbd", "pre", "samp"])
def test_epub_allows_fenced_div_markers_in_code_examples(
    tmp_path: Path, tag: str
) -> None:
    epub_path = tmp_path / "code-example.epub"
    _write_minimal_epub(epub_path, "en-US")
    with zipfile.ZipFile(epub_path, "a") as epub:
        epub.writestr(
            "EPUB/text/ch002.xhtml",
            '<html xmlns="http://www.w3.org/1999/xhtml"><body>'
            f"<{tag}>::: {{.callout}}\nExample\n:::</{tag}>"
            "</body></html>",
        )

    findings = arch2_cli.epub_findings(epub_path)

    assert not any(finding.code == "epub-literal-fenced-div" for finding in findings)


def test_epub_xhtml_normalization_preserves_image_alternative(tmp_path: Path) -> None:
    epub_path = tmp_path / "figure-alt.epub"
    chapter = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
  <body>
    <div class="quarto-figure" alt="Useful image alternative">
      <img src="figure.svg" alt="Useful image alternative" />
    </div>
  </body>
</html>
"""
    with zipfile.ZipFile(epub_path, "w") as epub:
        epub.writestr(
            "mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED
        )
        epub.writestr("EPUB/text/ch001.xhtml", chapter)
    original_mode = epub_path.stat().st_mode & 0o777

    changed = arch2_cli.normalize_epub_xhtml(epub_path)

    assert changed == 1
    assert epub_path.stat().st_mode & 0o777 == original_mode
    with zipfile.ZipFile(epub_path) as epub:
        assert epub.infolist()[0].filename == "mimetype"
        assert epub.infolist()[0].compress_type == zipfile.ZIP_STORED
        normalized = epub.read("EPUB/text/ch001.xhtml").decode()
    assert 'class="quarto-figure" alt=' not in normalized
    assert '<img src="figure.svg" alt="Useful image alternative"' in normalized


def test_epubcheck_is_a_pinned_required_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    epub_path = tmp_path / "book.epub"
    epub_path.touch()
    calls: list[list[str]] = []

    monkeypatch.setattr(arch2_cli.shutil, "which", lambda _: "/usr/bin/epubcheck")
    monkeypatch.setattr(
        arch2_cli,
        "_record_log",
        lambda _name, _text: tmp_path / "epubcheck.log",
    )

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        output = (
            f"EPUBCheck v{arch2_cli.EPUBCHECK_VERSION}"
            if command[-1] == "--version"
            else "Check finished with no errors"
        )
        return subprocess.CompletedProcess(command, 0, output, "")

    monkeypatch.setattr(arch2_cli, "_run", fake_run)

    arch2_cli.run_epubcheck(epub_path)

    assert calls == [
        ["/usr/bin/epubcheck", "--version"],
        ["/usr/bin/epubcheck", str(epub_path), "--failonwarnings"],
    ]


@pytest.mark.parametrize(
    "version_output",
    ["EPUBCheck v15.3.0", "EPUBCheck v5.3.0-SNAPSHOT"],
)
def test_epubcheck_rejects_nonexact_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, version_output: str
) -> None:
    epub_path = tmp_path / "book.epub"
    epub_path.touch()
    monkeypatch.setattr(arch2_cli.shutil, "which", lambda _: "/usr/bin/epubcheck")
    monkeypatch.setattr(
        arch2_cli,
        "_run",
        lambda command, **_: subprocess.CompletedProcess(
            command, 0, version_output, ""
        ),
    )

    with pytest.raises(arch2_cli.typer.Exit):
        arch2_cli.run_epubcheck(epub_path)


def test_custom_site_layout_has_one_shared_main_contract() -> None:
    root = arch2_cli.ROOT
    for project in ("www", "tools"):
        config = yaml.safe_load((root / project / "_quarto.yml").read_text())
        html = config["format"]["html"]
        assert "../_global/site-main-before.html" in html["include-before-body"]
        assert html["include-after-body"][0] == "../_global/site-main-after.html"
        assert "../_global/site-accessibility.html" in html["include-after-body"]

    main_open = (root / "_global/site-main-before.html").read_text()
    assert 'href="#main-content"' in main_open
    assert '<main id="main-content">' in main_open
    assert "<main" not in (root / "www/start.qmd").read_text()


def test_rendered_landmark_checker_accepts_one_main_and_skip_link(
    tmp_path: Path,
) -> None:
    root = arch2_cli.ROOT
    rendered = tmp_path / "page.html"
    rendered.write_text(
        '<html><body><a class="site-skip-link" href="#main-content">Skip</a>'
        '<main id="main-content"><h1>Page</h1></main>'
        '<script data-arch2-accessibility="true"></script></body></html>'
    )

    command = [
        arch2_cli.sys.executable,
        str(root / ".github/scripts/check_site_accessibility.py"),
        str(rendered),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert "Rendered landmark contract passed for 1 page(s)." in completed.stdout


def test_custom_controls_have_accessible_names_and_group_semantics() -> None:
    root = arch2_cli.ROOT
    for relative_path in ("www/readings.qmd", "www/workshops.qmd", "tools/index.qmd"):
        text = (root / relative_path).read_text()
        assert 'class="category-strip" role="group" aria-label=' in text

    for relative_path in (
        "www/submit.qmd",
        "www/submit-resource.qmd",
        "www/submit-workshop.qmd",
    ):
        text = (root / relative_path).read_text()
        assert 'id="submit-body-preview" readonly' in text
        assert 'aria-label="Generated ' in text

    initializer = (root / "_global/site-accessibility.html").read_text()
    assert ".quarto-listing-filter input.search" in initializer
    assert 'input.setAttribute("aria-label"' in initializer
    assert 'button.navbar-toggler[role="menu"]' in initializer
    assert 'toggle.removeAttribute("role")' in initializer
    assert "button.setAttribute(" in initializer
    assert '"aria-pressed"' in initializer
    assert "new URLSearchParams" in initializer
    assert 'window.addEventListener("hashchange"' in initializer


def test_publication_accessibility_styles_preserve_visible_focus() -> None:
    root = arch2_cli.ROOT
    site_css = (root / "_global/theme.scss").read_text()
    book_css = (root / "book/_styles/arch2-html.scss").read_text()

    assert "--arch2-control-border: #7c929c" in site_css
    assert "border: 1px solid var(--arch2-control-border)" in site_css
    assert ":focus-visible" in site_css
    assert ":focus-visible" in book_css
    assert "outline: 3px solid #b45309" in book_css


def test_book_hub_nav_uses_native_control_semantics() -> None:
    root = arch2_cli.ROOT
    generator = (root / ".github/scripts/render_book_navbar.py").read_text()
    rendered = (root / "book/_includes/hub-navbar.html").read_text()

    for text in (generator, rendered):
        assert 'role="menu"' not in text
        assert 'role="link"' not in text


def test_ci_installs_checksum_pinned_epubcheck() -> None:
    root = arch2_cli.ROOT
    installer = (root / ".github/scripts/install_epubcheck.sh").read_text()
    assert 'version="5.3.0"' in installer
    assert (
        'sha256="6c07e68584b2e2ce2f89fe06e1246dfead3eb36b46b340e7d93524f29dcff6c5"'
        in installer
    )
    assert "sha256sum --check --strict" in installer

    for workflow in ("validate.yml", "publish-site.yml"):
        text = (root / ".github/workflows" / workflow).read_text()
        assert "openjdk-21-jre-headless" in text
        assert ".github/scripts/install_epubcheck.sh" in text

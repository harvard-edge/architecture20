from __future__ import annotations

import pytest
from typer.testing import CliRunner

import cli.arch2 as arch2_cli


runner = CliRunner()


def test_tool_subsite_rewrites_all_root_navigation_targets() -> None:
    build_script = (
        arch2_cli.ROOT / ".github" / "scripts" / "build_site.sh"
    ).read_text()
    for target in (
        "about",
        "start",
        "readings",
        "workshops",
        "submit",
        "submit-resource",
        "submit-workshop",
    ):
        assert (
            f's#href="\\./{target}\\.html"#href="../{target}.html"#g;' in build_script
        )
    assert "assembled tool pages retain root-relative navigation links" in build_script


def test_build_help_matches_standard_artifact_contract() -> None:
    result = runner.invoke(arch2_cli.app, ["build", "--help"])
    assert result.exit_code == 0, result.output
    assert "Defaults to HTML + PDF + EPUB" in result.output
    assert "arch2 check standard" in result.output


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ([], "all"),
        (["--all"], "all"),
        (["--html", "--pdf", "--epub"], "all"),
        (["--pdf"], "pdf"),
        (["--html", "--pdf"], "html,pdf"),
    ],
)
def test_build_selects_coherent_format_set(
    monkeypatch: pytest.MonkeyPatch, args: list[str], expected: str
) -> None:
    calls: list[str] = []

    def fake_render(to: str, **_: object) -> None:
        calls.append(to)

    monkeypatch.setattr(arch2_cli, "_render_one", fake_render)
    result = runner.invoke(arch2_cli.app, ["build", *args])
    assert result.exit_code == 0, result.output
    assert calls == [expected]

from __future__ import annotations

import pytest
from typer.testing import CliRunner

import cli.arch2 as arch2_cli


runner = CliRunner()


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

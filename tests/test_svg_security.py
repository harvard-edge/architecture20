from pathlib import Path

import cli.arch2 as arch2_cli


def test_svg_validation_rejects_entity_declarations(tmp_path: Path) -> None:
    path = tmp_path / "hostile.svg"
    path.write_text(
        """<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY payload "expanded text">]>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <text x="10" y="20">&payload;</text>
</svg>
""",
        encoding="utf-8",
    )

    findings = arch2_cli.svg_text_findings_for_file(path)

    assert len(findings) == 1
    assert findings[0].code == "svg-parse"
    assert "EntitiesForbidden" in findings[0].message

from __future__ import annotations

import importlib.util
from pathlib import Path

NOTEBOOKS = [
    Path("examples/scale_proxy_mirage/lab.py"),
    Path("notebooks/lab_01_prompt_to_card.py"),
    Path("notebooks/lab_02_scissors_gap.py"),
]


def test_marimo_notebooks_import() -> None:
    labs_root = Path(__file__).resolve().parents[1]
    for index, notebook in enumerate(NOTEBOOKS):
        path = labs_root / notebook
        spec = importlib.util.spec_from_file_location(f"arch2_notebook_{index}", path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.app is not None

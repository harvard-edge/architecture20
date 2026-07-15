from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]
FIGURE_ID_RE = re.compile(r"#(fig-[A-Za-z0-9_-]+)")
CHUNK_LABEL_RE = re.compile(r"^#\|\s*label:\s*(fig-[A-Za-z0-9_-]+)\s*$", re.MULTILINE)


class NoDuplicateKeysLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(
    loader: NoDuplicateKeysLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


NoDuplicateKeysLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


class PermissionsLedgerTests(unittest.TestCase):
    def test_every_labeled_figure_has_a_permissions_entry(self) -> None:
        source_labels: set[str] = set()
        for path in (ROOT / "book").rglob("*.qmd"):
            text = path.read_text(encoding="utf-8")
            source_labels.update(FIGURE_ID_RE.findall(text))
            source_labels.update(CHUNK_LABEL_RE.findall(text))

        ledger = yaml.load(
            (ROOT / "compliance" / "permissions-ledger.yml").read_text(
                encoding="utf-8"
            ),
            Loader=NoDuplicateKeysLoader,
        )
        entries = ledger.get("figures", [])
        ledger_labels = [entry.get("label") for entry in entries]

        duplicates = sorted(
            label for label in set(ledger_labels) if ledger_labels.count(label) > 1
        )
        self.assertEqual(duplicates, [], f"duplicate permissions entries: {duplicates}")

        missing = sorted(source_labels - set(ledger_labels))
        self.assertEqual(
            missing, [], f"figures missing from permissions ledger: {missing}"
        )


if __name__ == "__main__":
    unittest.main()

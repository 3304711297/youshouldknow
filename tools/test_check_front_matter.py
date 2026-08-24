import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_front_matter.py")
SPEC = importlib.util.spec_from_file_location("check_front_matter", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FrontMatterValidationTests(unittest.TestCase):
    def test_accepts_complete_front_matter(self):
        errors = MODULE.validate_text(
            """---
status: reference
risk: low
applies_to:
  - Windows 10/11
verified_on: 2026-08-21
---
# Article
""",
            "docs/example.md",
        )
        self.assertEqual(errors, [])

    def test_allows_legacy_document_without_front_matter(self):
        errors = MODULE.validate_text(
            "# Article\n\n---\n\n## Section\n",
            "docs/legacy.md",
        )
        self.assertEqual(errors, [])

    def test_accepts_utf8_bom(self):
        errors = MODULE.validate_text(
            "\ufeff---\nstatus: stable\nrisk: low\napplies_to: [Windows 11]\nverified_on: 2026-08-21\n---\n# Article\n",
            "docs/bom.md",
        )
        self.assertEqual(errors, [])

    def test_rejects_missing_required_field(self):
        errors = MODULE.validate_text(
            """---
status: stable
risk: low
applies_to:
  - Windows 11
---
# Article
""",
            "docs/missing.md",
        )
        self.assertTrue(any("verified_on" in error for error in errors))

    def test_rejects_unknown_field(self):
        errors = MODULE.validate_text(
            """---
status: stable
risk: low
applies_to:
  - Windows 11
verified_on: 2026-08-21
title: Duplicate title source
---
# Article
""",
            "docs/unknown.md",
        )
        self.assertTrue(any("unknown field" in error for error in errors))

    def test_rejects_invalid_enum(self):
        errors = MODULE.validate_text(
            """---
status: draft
risk: critical
applies_to:
  - Windows 11
verified_on: 2026-08-21
---
# Article
""",
            "docs/enum.md",
        )
        self.assertTrue(any("status" in error for error in errors))
        self.assertTrue(any("risk" in error for error in errors))

    def test_rejects_invalid_applies_to(self):
        errors = MODULE.validate_text(
            """---
status: stable
risk: low
applies_to: Windows 11
verified_on: 2026-08-21
---
# Article
""",
            "docs/applies-to.md",
        )
        self.assertTrue(any("applies_to" in error for error in errors))

    def test_rejects_invalid_date(self):
        errors = MODULE.validate_text(
            """---
status: stable
risk: low
applies_to:
  - Windows 11
verified_on: 2026-02-30
---
# Article
""",
            "docs/date.md",
        )
        self.assertTrue(any("verified_on" in error for error in errors))

    def test_rejects_unclosed_front_matter(self):
        errors = MODULE.validate_text(
            """---
status: stable
risk: low
applies_to:
  - Windows 11
verified_on: 2026-08-21
# Article
""",
            "docs/unclosed.md",
        )
        self.assertTrue(any("closing" in error for error in errors))

    def test_scans_only_markdown_files_under_docs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "valid.md").write_text(
                "---\nstatus: stable\nrisk: low\napplies_to: [Windows 11]\nverified_on: 2026-08-21\n---\n# Valid\n",
                encoding="utf-8",
            )
            (docs / "ignored.txt").write_text("not markdown", encoding="utf-8")
            result = MODULE.check_tree(root)
            self.assertEqual(result.files_checked, 1)
            self.assertEqual(result.files_with_front_matter, 1)
            self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()

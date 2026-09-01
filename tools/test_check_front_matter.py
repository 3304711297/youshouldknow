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
tweak_module: [3, 7]
---
# Article
""",
            "docs/example.md",
        )
        self.assertEqual(errors, [])

    def test_status_and_verified_on_are_optional(self):
        # P2-13 契约:必填三字段为 applies_to/risk/tweak_module;status/verified_on 提供时才校验
        errors = MODULE.validate_text(
            """---
risk: medium
applies_to: [Windows 11]
tweak_module: []
---
# Article
""",
            "docs/minimal.md",
        )
        self.assertEqual(errors, [])

    def test_validate_text_tolerates_legacy_document_without_front_matter(self):
        # validate_text 层兼容无 front matter 旧文;强制入口在 check_tree(全站必填)
        errors = MODULE.validate_text(
            "# Article\n\n---\n\n## Section\n",
            "docs/legacy.md",
        )
        self.assertEqual(errors, [])

    def test_accepts_utf8_bom(self):
        errors = MODULE.validate_text(
            "\ufeff---\nstatus: stable\nrisk: low\napplies_to: [Windows 11]\nverified_on: 2026-08-21\ntweak_module: [1]\n---\n# Article\n",
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
        self.assertTrue(any("tweak_module" in error for error in errors))

    def test_rejects_invalid_tweak_module(self):
        errors = MODULE.validate_text(
            """---
risk: low
applies_to: [Windows 11]
tweak_module: [0, 12, x]
---
# Article
""",
            "docs/bad-module.md",
        )
        self.assertTrue(any("tweak_module" in error and "1-11" in error for error in errors))

    def test_tweak_module_allows_empty_and_non_empty_lists(self):
        for mods in ("[]", "[1]", "[2, 3, 4]", "[10, 11]"):
            errors = MODULE.validate_text(
                f"---\nrisk: low\napplies_to: [Windows 11]\ntweak_module: {mods}\n---\n# Article\n",
                "docs/mods.md",
            )
            self.assertEqual(errors, [], f"tweak_module: {mods} 应合法")

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
                "---\nstatus: stable\nrisk: low\napplies_to: [Windows 11]\nverified_on: 2026-08-21\ntweak_module: []\n---\n# Valid\n",
                encoding="utf-8",
            )
            (docs / "ignored.txt").write_text("not markdown", encoding="utf-8")
            result = MODULE.check_tree(root)
            self.assertEqual(result.files_checked, 1)
            self.assertEqual(result.files_with_front_matter, 1)
            self.assertEqual(result.errors, [])

    def test_check_tree_requires_front_matter_on_every_doc(self):
        # P2-13 契约:全部 docs/*.md 必须携带 front matter
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "with.md").write_text(
                "---\nrisk: low\napplies_to: [Windows 11]\ntweak_module: []\n---\n# With\n",
                encoding="utf-8",
            )
            (docs / "without.md").write_text("# Without\n", encoding="utf-8")
            result = MODULE.check_tree(root)
            self.assertEqual(result.files_checked, 2)
            self.assertEqual(result.files_with_front_matter, 1)
            self.assertEqual(len(result.errors), 1)
            self.assertIn("missing Front Matter", result.errors[0])


class NavCoverageTests(unittest.TestCase):
    def _make_tree(self, root: Path) -> None:
        docs = root / "docs"
        (docs / "分类A").mkdir(parents=True)
        (docs / "README.md").write_text("# 首页\n[分类A](./分类A/README.md)\n", encoding="utf-8")
        (docs / "分类A" / "README.md").write_text("# 索引\n[文章](./文章一.md)\n", encoding="utf-8")
        (docs / "分类A" / "文章一.md").write_text("# 文章一\n", encoding="utf-8")
        (root / "mkdocs.yml").write_text(
            "nav:\n  - 首页: README.md\n  - 分类A:\n    - 分类A/README.md\n    - 文章: 分类A/文章一.md\n",
            encoding="utf-8",
        )

    def test_complete_tree_passes_both_directions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_tree(root)
            self.assertEqual(MODULE.check_nav_coverage(root), [])
            self.assertEqual(MODULE.check_index_coverage(root), [])

    def test_file_missing_from_nav_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_tree(root)
            (root / "docs" / "分类A" / "文章二.md").write_text("# 文章二\n", encoding="utf-8")
            errors = MODULE.check_nav_coverage(root)
            self.assertEqual(errors, ["docs/分类A/文章二.md: 文件未收录进 mkdocs.yml nav"])

    def test_nav_pointing_to_missing_file_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_tree(root)
            (root / "docs" / "分类A" / "文章一.md").unlink()
            errors = MODULE.check_nav_coverage(root)
            self.assertEqual(
                errors,
                ["mkdocs.yml nav 指向不存在的文件: docs/分类A/文章一.md"],
            )

    def test_external_links_in_nav_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_tree(root)
            mkdocs = root / "mkdocs.yml"
            mkdocs.write_text(
                "nav:\n  - 首页: README.md\n  - 外部: https://example.com/x\n  - 分类A:\n"
                "    - 分类A/README.md\n    - 文章: 分类A/文章一.md\n",
                encoding="utf-8",
            )
            self.assertEqual(MODULE.check_nav_coverage(root), [])

    def test_unlinked_article_in_category_index_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_tree(root)
            (root / "docs" / "分类A" / "文章二.md").write_text("# 文章二\n", encoding="utf-8")
            (root / "mkdocs.yml").write_text(
                "nav:\n  - 首页: README.md\n  - 分类A:\n    - 分类A/README.md\n"
                "    - 文章: 分类A/文章一.md\n    - 文章: 分类A/文章二.md\n",
                encoding="utf-8",
            )
            errors = MODULE.check_index_coverage(root)
            self.assertEqual(
                errors,
                ["docs/分类A/README.md: 未链接同分类文章 文章二.md"],
            )

    def test_category_missing_from_home_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_tree(root)
            home = root / "docs" / "README.md"
            home.write_text("# 首页\n", encoding="utf-8")
            errors = MODULE.check_index_coverage(root)
            self.assertEqual(
                errors,
                ["docs/README.md: 未链接分类索引 分类A/README.md"],
            )


if __name__ == "__main__":
    unittest.main()

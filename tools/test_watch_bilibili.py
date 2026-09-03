#!/usr/bin/env python3
"""
单元测试：watch_bilibili.py
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tools.watch_bilibili import (
    BilibiliClient,
    build_issue_content,
    collect_documented_bvids,
    create_github_issue,
    extract_bvids_from_text,
    format_duration,
    get_existing_issue_bvids,
    main,
)


class TestWatchBilibili(unittest.TestCase):
    def test_extract_bvids_from_text(self):
        text = "Check out https://www.bilibili.com/video/BV1BdtX6XEdu and BV1jKtW6eEAd."
        bvids = set()
        extract_bvids_from_text(text, bvids)
        self.assertIn("BV1BdtX6XEdu", bvids)
        self.assertIn("BV1jKtW6eEAd", bvids)
        self.assertEqual(len(bvids), 2)

    def test_collect_documented_bvids(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            docs_path = Path(tmp_dir)
            (docs_path / "sub").mkdir()
            (docs_path / "test1.md").write_text("Reference: BV1YA8r67EwX", encoding="utf-8")
            (docs_path / "sub" / "test2.md").write_text("Link: BV1a88c6iE6G and BV1YA8r67EwX", encoding="utf-8")

            res = collect_documented_bvids(docs_path)
            self.assertEqual(res, {"BV1YA8r67EwX", "BV1a88c6iE6G"})

    def test_format_duration(self):
        self.assertEqual(format_duration(0), "未知")
        self.assertEqual(format_duration(45), "00:45")
        self.assertEqual(format_duration(922), "15:22")
        self.assertEqual(format_duration(3665), "01:01:05")

    def test_build_issue_content(self):
        video = {
            "bvid": "BV1BdtX6XEdu",
            "title": "电脑BIOS选项全科普EP15/NVMe识别全链路",
            "pubdate": 1788410174,
            "duration": 922,
            "mid": 589200735,
        }
        title, body = build_issue_content(
            video=video,
            up_name="所盼皆欣然",
            category="BIOS与固件",
            season_name="电脑BIOS/UEFI选项内容全科普【重制版】",
            season_id=8897657,
        )
        self.assertIn("BV1BdtX6XEdu", title)
        self.assertIn("所盼皆欣然", title)
        self.assertIn("https://www.bilibili.com/video/BV1BdtX6XEdu", body)
        self.assertIn("15:22", body)
        self.assertIn("电脑BIOS/UEFI选项内容全科普【重制版】", body)
        self.assertIn("docs/BIOS与固件/", body)
        self.assertIn("Checklist", body)

    def test_create_github_issue_dry_run(self):
        res = create_github_issue(
            repo="test/repo",
            title="test",
            body="test body",
            labels=["upstream-watch"],
            dry_run=True,
        )
        self.assertTrue(res)

    @patch("tools.watch_bilibili.urllib.request.urlopen")
    def test_bilibili_client_seasons(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "code": 0,
            "data": {
                "items_lists": {
                    "seasons_list": [
                        {"meta": {"season_id": 8897657, "title": "Test Season", "total": 15}}
                    ]
                }
            }
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client = BilibiliClient()
        seasons = client.get_seasons_list(589200735)
        self.assertEqual(len(seasons), 1)
        self.assertEqual(seasons[0]["meta"]["season_id"], 8897657)


if __name__ == "__main__":
    unittest.main()

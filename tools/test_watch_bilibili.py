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
    _WBI_MIXIN_KEY_ENC_TAB,
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

    def test_wbi_mixin_key_derivation(self):
        """mixin key 由 img_url/sub_url 的文件名按固定表重排；全部为 ASCII 时长度应为 32"""
        img = "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png"
        sub = "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png"
        raw = img.rsplit("/", 1)[-1].split(".")[0] + sub.rsplit("/", 1)[-1].split(".")[0]
        mixin = "".join(raw[i] for i in _WBI_MIXIN_KEY_ENC_TAB)[:32]
        self.assertEqual(len(mixin), 32)
        self.assertEqual(len(_WBI_MIXIN_KEY_ENC_TAB), 64)

    @patch("tools.watch_bilibili.urllib.request.urlopen")
    def test_get_user_videos_parses_vlist(self, mock_urlopen):
        """投稿列表接口：解析 vlist，并在返回 HTML（412 限流）时明确报错"""

        def make_resp(payload_bytes):
            resp = MagicMock()
            resp.read.return_value = payload_bytes
            resp.__enter__.return_value = resp
            return resp

        nav_resp = make_resp(json.dumps({
            "code": -101,
            "data": {"wbi_img": {
                "img_url": "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png",
                "sub_url": "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png",
            }},
        }).encode("utf-8"))
        list_resp = make_resp(json.dumps({
            "code": 0,
            "data": {"list": {"vlist": [
                {"bvid": "BV1aaaaaaaaa", "title": "t", "pubdate": 1, "duration": 60}
            ]}},
        }).encode("utf-8"))
        # 第一次调用 nav，第二次调用投稿列表
        mock_urlopen.side_effect = [nav_resp, list_resp]

        client = BilibiliClient()
        videos = client.get_user_videos(13879658)
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]["bvid"], "BV1aaaaaaaaa")

        # 非 JSON 响应（限流 HTML）重试耗尽后必须显式失败，不能静默返回空列表
        mock_urlopen.side_effect = [nav_resp] + [make_resp(b"<!DOCTYPE html>")] * 8
        client2 = BilibiliClient()
        client2.RETRY_BACKOFF_SECONDS = 0
        with self.assertRaises(RuntimeError):
            client2.get_user_videos(13879658)

    @patch("tools.watch_bilibili.time.sleep", lambda *_: None)
    @patch("tools.watch_bilibili.urllib.request.urlopen")
    def test_business_risk_control_is_retried(self, mock_urlopen):
        """业务层风控（HTTP 200 但 code=-352 风控校验失败）同样必须重试"""

        def make_resp(payload):
            resp = MagicMock()
            resp.read.return_value = payload
            resp.__enter__.return_value = resp
            return resp

        nav_resp = make_resp(json.dumps({
            "code": -101,
            "data": {"wbi_img": {
                "img_url": "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png",
                "sub_url": "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png",
            }},
        }).encode("utf-8"))
        risk_resp = make_resp(json.dumps({"code": -352, "message": "风控校验失败"}).encode("utf-8"))
        ok_resp = make_resp(json.dumps({
            "code": 0,
            "data": {"list": {"vlist": [{"bvid": "BV1cccccccccc", "title": "t", "pubdate": 1, "duration": 60}]}},
        }).encode("utf-8"))

        mock_urlopen.side_effect = [nav_resp, risk_resp, ok_resp]
        client = BilibiliClient()
        videos = client.get_user_videos(13879658)
        self.assertEqual([v["bvid"] for v in videos], ["BV1cccccccccc"])

    @patch("tools.watch_bilibili.time.sleep", lambda *_: None)
    @patch("tools.watch_bilibili.urllib.request.urlopen")
    def test_http_error_is_retried_then_succeeds(self, mock_urlopen):
        """B 站 412 风控在签名正确时也会随机命中：单次 HTTPError 必须被重试吸收"""

        def make_resp(payload_bytes):
            resp = MagicMock()
            resp.read.return_value = payload_bytes
            resp.__enter__.return_value = resp
            return resp

        nav_resp = make_resp(json.dumps({
            "code": -101,
            "data": {"wbi_img": {
                "img_url": "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png",
                "sub_url": "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png",
            }},
        }).encode("utf-8"))
        ok_resp = make_resp(json.dumps({
            "code": 0,
            "data": {"list": {"vlist": [{"bvid": "BV1bbbbbbbbb", "title": "t", "pubdate": 1, "duration": 60}]}},
        }).encode("utf-8"))

        import urllib.error
        mock_urlopen.side_effect = [
            nav_resp,
            urllib.error.HTTPError("u", 412, "Precondition Failed", {}, None),
            ok_resp,
        ]
        client = BilibiliClient()
        videos = client.get_user_videos(13879658)
        self.assertEqual([v["bvid"] for v in videos], ["BV1bbbbbbbbb"])
        self.assertEqual(mock_urlopen.call_count, 3)  # 1 次 nav + 失败 1 次 + 重试成功 1 次

    def test_build_issue_content_uploads_mode(self):
        """无合集账号：正文应标注来源为投稿列表，而不是空白合集行"""
        video = {
            "bvid": "BV1aaaaaaaaa",
            "title": "测试投稿",
            "pubdate": 1788410174,
            "duration": 120,
            "mid": 13879658,
        }
        title, body = build_issue_content(
            video=video,
            up_name="费利克斯X",
            category="系统调优与安全",
        )
        self.assertIn("BV1aaaaaaaaa", title)
        self.assertIn("投稿列表", body)
        self.assertIn("docs/系统调优与安全/", body)

    def test_watch_sources_config_is_valid(self):
        """配置自身必须可解析：mid 存在、模式合法、baseline 全为 BV 号"""
        cfg_path = Path(__file__).resolve().parent / "watch_sources.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        self.assertIn("channels", cfg)
        for ch in cfg["channels"]:
            self.assertIsInstance(ch.get("mid"), int)
            self.assertIn(ch.get("watch_mode", "seasons"), {"seasons", "uploads"})
            for b in ch.get("baseline_bvids", []) or []:
                self.assertRegex(b, r"^BV[0-9a-zA-Z]{10}$")
            if ch.get("watch_mode") == "uploads":
                self.assertTrue(ch.get("baseline_bvids"), "uploads 模式应带基线，避免一次性开历史单")


if __name__ == "__main__":
    unittest.main()

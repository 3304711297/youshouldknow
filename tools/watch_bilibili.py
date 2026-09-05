#!/usr/bin/env python3
"""
Bilibili UP主视频更新看门检测脚本 (watch_bilibili.py)

功能：
1. 依据 tools/watch_sources.json 配置的 UP 主与合集列表，获取最新视频；
2. 扫描 docs/ 目录与 GitHub Issues，自动跳过已收录或已开单的 BVID；
3. 发现上游新视频后自动创建 Issue，打上 upstream-watch / bilibili 标签并附带收录清单。
"""

import argparse
import datetime
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class BilibiliClient:
    """轻量稳定 B 站 API 客户端（无第三方依赖，支持合集与系列归档接口）"""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.bilibili.com/",
        }

    def get_seasons_list(self, mid: int) -> List[Dict[str, Any]]:
        """获取 UP 主公开的合集列表 (B站该接口 page_size 最大为 20)"""
        url = f"https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num=1&page_size=20"
        headers = dict(self.headers)
        headers["Referer"] = f"https://space.bilibili.com/{mid}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("code") == 0:
                return data.get("data", {}).get("items_lists", {}).get("seasons_list", [])
            raise RuntimeError(f"Failed to fetch seasons: code={data.get('code')}, msg={data.get('message')}")

    def get_season_archives(self, mid: int, season_id: int, page_size: int = 30) -> List[Dict[str, Any]]:
        """获取指定合集下的视频列表"""
        url = (
            f"https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?"
            f"mid={mid}&season_id={season_id}&page_num=1&page_size={page_size}"
        )
        headers = dict(self.headers)
        headers["Referer"] = f"https://space.bilibili.com/{mid}/channel/collectiondetail?sid={season_id}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("code") == 0:
                return data.get("data", {}).get("archives", [])
            raise RuntimeError(
                f"Failed to fetch season {season_id} archives: code={data.get('code')}, msg={data.get('message')}"
            )


def extract_bvids_from_text(text: str, bvids_set: Set[str]) -> None:
    """提取文本中的所有 BV 编号"""
    matches = re.findall(r"BV[0-9a-zA-Z]{10}", text)
    for m in matches:
        bvids_set.add(m)


def collect_documented_bvids(docs_dir: Path) -> Set[str]:
    """扫描本地 docs/ 目录，提取已写入文档的 BVID"""
    documented = set()
    if not docs_dir.exists():
        return documented

    for p in docs_dir.rglob("*.md"):
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            extract_bvids_from_text(content, documented)
        except Exception:
            pass
    return documented


def get_existing_issue_bvids(repo: str, token: Optional[str] = None) -> Set[str]:
    """获取 GitHub Issues 中已存在的 BVID"""
    bvids = set()

    # 优先使用 gh CLI
    try:
        cmd = ["gh", "issue", "list", "--repo", repo, "--state", "all", "--limit", "200", "--json", "title,body"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issues = json.loads(res.stdout)
        for issue in issues:
            text = f"{issue.get('title', '')} {issue.get('body', '')}"
            extract_bvids_from_text(text, bvids)
        return bvids
    except Exception:
        # 退回直接请求 GitHub REST API
        if token:
            url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "youshouldknow-bilibili-watch",
            }
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    issues = json.loads(resp.read().decode("utf-8"))
                    for issue in issues:
                        text = f"{issue.get('title', '')} {issue.get('body', '')}"
                        extract_bvids_from_text(text, bvids)
            except Exception as api_err:
                print(f"[WARN] Failed to fetch issues via REST API: {api_err}", file=sys.stderr)

    return bvids


def format_duration(seconds: int) -> str:
    """将秒数格式化为 mm:ss 或 hh:mm:ss"""
    if not seconds:
        return "未知"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def build_issue_content(
    video: Dict[str, Any],
    up_name: str,
    category: str,
    season_name: str = "",
    season_id: Optional[int] = None
) -> tuple[str, str]:
    """构造 Issue 标题与规范 Markdown 正文"""
    bvid = video.get("bvid", "")
    v_title = video.get("title", "")
    title = f"[Upstream Watch] {up_name} 发布新视频：《{v_title}》（{bvid}）"

    pubdate = video.get("pubdate", 0)
    if pubdate:
        pub_str = datetime.datetime.fromtimestamp(pubdate, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        pub_str = "未知"

    duration_str = format_duration(video.get("duration", 0))

    collection_line = ""
    if season_name:
        if season_id:
            collection_line = f"- **所属合集**：[{season_name}](https://space.bilibili.com/{video.get('mid', 589200735)}/channel/collectiondetail?sid={season_id})"
        else:
            collection_line = f"- **所属合集**：{season_name}"

    body_lines = [
        "### 📺 上游视频更新通知",
        "",
        f"- **UP 主**：[{up_name}](https://space.bilibili.com/{video.get('mid', 589200735)})",
        f"- **视频标题**：{v_title}",
        f"- **BV 号**：`{bvid}`",
        f"- **视频链接**：https://www.bilibili.com/video/{bvid}",
        f"- **发布时间**：{pub_str}",
        f"- **视频时长**：{duration_str}",
    ]
    if collection_line:
        body_lines.append(collection_line)
    body_lines.extend([
        f"- **建议归档分类**：`docs/{category}/`",
        "",
        "---",
        "",
        "### 📋 知识库收录待办 (Checklist)",
        "- [ ] 视频内容初审与价值评估（是否需要收录进知识库）",
        "- [ ] 本地 Whisper / 语音转录提取文稿",
        "- [ ] 硬件术语校对与文章整理",
        f"- [ ] 补充 YAML Front Matter 并加入 `docs/{category}/`",
        "- [ ] 运行 `python tools/check_front_matter.py` 与 `python scripts/gen-matrix.py` 验证",
        "- [ ] PR 合并上线后自动/手动关闭此 Issue",
        "",
        "> 🤖 *本 Issue 由 GitHub Actions `bilibili-watch` 定时看门任务自动生成。*",
    ])

    return title, "\n".join(body_lines)


def create_github_issue(
    repo: str,
    title: str,
    body: str,
    labels: List[str],
    token: Optional[str] = None,
    dry_run: bool = False
) -> bool:
    """创建 GitHub Issue（支持 gh CLI 与 REST API 双通道）"""
    if dry_run:
        print(f"[DRY-RUN] Would create issue in {repo}:")
        print(f"Title: {title}")
        print(f"Labels: {labels}")
        print(f"Body preview:\n{body}\n")
        return True

    # 1. 尝试 gh CLI
    try:
        cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]
        for l in labels:
            cmd.extend(["--label", l])
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[SUCCESS] Created issue via gh CLI: {res.stdout.strip()}")
        return True
    except Exception as gh_err:
        print(f"[WARN] Failed to create issue via gh CLI: {gh_err}", file=sys.stderr)
        gh_stderr = (getattr(gh_err, "stderr", "") or "").strip()
        if gh_stderr:
            print(f"[WARN] gh CLI stderr: {gh_stderr}", file=sys.stderr)

    # 2. 尝试 REST API
    if token:
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "youshouldknow-bilibili-watch",
            "Content-Type": "application/json",
        }
        payload = json.dumps({"title": title, "body": body, "labels": labels}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"[SUCCESS] Created issue via REST API: {data.get('html_url')}")
                return True
        except Exception as api_err:
            print(f"[ERROR] Failed to create issue via REST API: {api_err}", file=sys.stderr)

    print(f"[ERROR] Could not create issue: no gh CLI or valid GH_TOKEN", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor Bilibili UP updates and open GitHub issues.")
    parser.add_argument("--config", default="tools/watch_sources.json", help="Path to sources config JSON")
    parser.add_argument("--docs-dir", default="docs", help="Path to docs directory")
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", "3304711297/youshouldknow"), help="GitHub repo")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without creating issues")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[ERROR] Config not found: {config_path}", file=sys.stderr)
        return 1

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    channels = config_data.get("channels", [])
    if not channels:
        print("[INFO] No channels configured.")
        return 0

    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

    # 1. 扫描文档中已收录的 BVID
    docs_dir = Path(args.docs_dir)
    doc_bvids = collect_documented_bvids(docs_dir)
    print(f"[INFO] Found {len(doc_bvids)} documented BVIDs in {docs_dir}")

    # 2. 查询已建 Issue 中的 BVID
    issue_bvids = get_existing_issue_bvids(args.repo, token)
    print(f"[INFO] Found {len(issue_bvids)} existing BVIDs in GitHub issues")

    tracked_bvids = doc_bvids | issue_bvids
    print(f"[INFO] Total tracked BVIDs (docs + issues): {len(tracked_bvids)}")

    client = BilibiliClient()
    new_video_count = 0
    failed_count = 0

    for ch in channels:
        if not ch.get("enabled", True):
            continue

        mid = ch["mid"]
        up_name = ch.get("name", f"UID:{mid}")
        category = ch.get("target_category", "BIOS与固件")
        target_season_ids = ch.get("season_ids")
        watch_all = ch.get("watch_all_seasons", True)

        print(f"\n[INFO] Checking UP: {up_name} (mid={mid})...")
        try:
            seasons = client.get_seasons_list(mid)
        except Exception as e:
            print(f"[ERROR] Failed to fetch seasons for {up_name}: {e}", file=sys.stderr)
            continue

        for season in seasons:
            meta = season.get("meta", {})
            sid = meta.get("season_id")
            stitle = meta.get("title", "")

            # 若配置了指定合集且非 watch_all，则过滤
            if target_season_ids and (sid not in target_season_ids) and not watch_all:
                continue

            try:
                archives = client.get_season_archives(mid=mid, season_id=sid, page_size=30)
            except Exception as e:
                print(f"  [ERROR] Failed to fetch archives for season {stitle} ({sid}): {e}", file=sys.stderr)
                continue

            for v in archives:
                v["mid"] = mid
                bvid = v.get("bvid")
                if not bvid:
                    continue

                if bvid in tracked_bvids:
                    continue

                print(f"  + [NEW] Found unrecorded video: {v.get('title')} ({bvid}) in [{stitle}]")
                title, body = build_issue_content(
                    video=v,
                    up_name=up_name,
                    category=category,
                    season_name=stitle,
                    season_id=sid,
                )
                labels = ["upstream-watch", "bilibili"]

                success = create_github_issue(
                    repo=args.repo,
                    title=title,
                    body=body,
                    labels=labels,
                    token=token,
                    dry_run=args.dry_run,
                )
                if success:
                    tracked_bvids.add(bvid)
                    new_video_count += 1
                else:
                    failed_count += 1

    if failed_count:
        # 有新视频但 Issue 创建失败：看门失效，必须让 workflow 变红（区别于"无新视频"的正常 0）
        print(f"\n[ERROR] Failed to create {failed_count} new video issue(s).", file=sys.stderr)
        print(f"\n[SUMMARY] Inspection completed. Newly tracked videos: {new_video_count}")
        return 1

    print(f"\n[SUMMARY] Inspection completed. Newly tracked videos: {new_video_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

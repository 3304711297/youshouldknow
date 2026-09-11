"""ysk 站点排版/布局审计 v2——修正滚动容器判断，增加移动端与表格结构分析。

用法: python tools/audit_layout.py <urls_file> <out_file> [width] [height]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

from websocket import create_connection

CDP = "http://127.0.0.1:9333"

PROBE_JS = r"""
(() => {
  const issues = [];
  const docEl = document.documentElement;
  const vw = docEl.clientWidth;

  const desc = (el) => {
    if (!el || el.nodeType !== 1) return '?';
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const c = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).slice(0, 3).join('.');
    if (c) s += '.' + c;
    const t = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 50);
    return s + (t ? ` «${t}»` : '');
  };
  const sel = (el) => {
    if (!el || el.nodeType !== 1) return '?';
    const parts = [];
    let n = el;
    while (n && n.nodeType === 1 && parts.length < 5) {
      let p = n.tagName.toLowerCase();
      if (n.id) { p += '#' + n.id; parts.unshift(p); break; }
      const cls = (n.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean)[0];
      if (cls) p += '.' + cls;
      parts.unshift(p);
      n = n.parentElement;
    }
    return parts.join(' > ');
  };

  // 滚动容器判定（v2 修正版）：
  //   auto/scroll 祖先 = 内容可滚动到达（正常）
  //   hidden 祖先     = 仅当元素真的超出该祖先的内容盒时才算裁切
  //   visible 祖先    = 继续向上找
  const reachability = (el) => {
    let n = el.parentElement;
    while (n && n !== document.documentElement) {
      const st = getComputedStyle(n);
      const ox = st.overflowX;
      if (ox === 'auto' || ox === 'scroll') return 'scrollable';
      if (ox === 'hidden' || ox === 'clip') {
        const nr = n.getBoundingClientRect();
        const er = el.getBoundingClientRect();
        // 只有真正越出该祖先盒子才被裁切；祖先被内容撑开则不裁切
        if (er.right > nr.right + 1 || er.left < nr.left - 1) return 'clipped';
      }
      n = n.parentElement;
    }
    return 'free';
  };

  // ---- H1 文档级水平溢出 ----
  if (docEl.scrollWidth > vw + 1) {
    issues.push({ code: 'H1', sev: 'high', msg: `文档水平溢出: scrollWidth=${docEl.scrollWidth} > clientWidth=${vw}` });
  }

  const contentRoot = document.querySelector('.md-content') || document.body;

  // ---- H2 正文元素超出视口 ----
  const overflowers = [];
  contentRoot.querySelectorAll('*').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    if (r.right > vw + 4) {
      const kind = reachability(el);
      if (kind === 'scrollable') return;                  // 正常横向滚动
      if (kind === 'clipped') {
        overflowers.push({ kind: 'CLIPPED', el: desc(el), right: Math.round(r.right), w: Math.round(r.width) });
        return;
      }
      overflowers.push({ kind: 'OVERFLOW', el: desc(el), right: Math.round(r.right), w: Math.round(r.width) });
    }
  });
  if (overflowers.length) {
    issues.push({ code: 'H2', sev: 'high', count: overflowers.length, items: overflowers.slice(0, 8) });
  }

  // ---- H3 表格：裁切 / 需滚动 / 列宽失衡 ----
  document.querySelectorAll('.md-typeset table').forEach(tb => {
    const parent = tb.closest('.md-typeset__scrollwrap') || tb.parentElement;
    const pw = parent.clientWidth, tw = tb.scrollWidth;
    if (tw > pw + 2) {
      const st = getComputedStyle(parent);
      const canScroll = (st.overflowX === 'auto' || st.overflowX === 'scroll');
      issues.push({ code: canScroll ? 'H3s' : 'H3', sev: canScroll ? 'info' : 'high',
                    msg: `表格${canScroll ? '需横向滚动' : '被裁切'}: table=${tw} > container=${pw}`,
                    path: sel(tb) });
    }
    // 列宽失衡：最长列与最短列宽度比
    const rows = tb.rows;
    if (rows.length > 1) {
      const cols = rows[0].cells.length;
      const widths = [];
      for (let c = 0; c < cols; c++) {
        let mx = 0;
        for (let ri = 0; ri < Math.min(rows.length, 12); ri++) {
          if (rows[ri].cells[c]) mx = Math.max(mx, rows[ri].cells[c].getBoundingClientRect().width);
        }
        widths.push(Math.round(mx));
      }
      const nonZero = widths.filter(w => w > 0);
      if (nonZero.length > 1) {
        const mn = Math.min(...nonZero), mx = Math.max(...nonZero);
        if (mx > 0 && mn > 0 && mx / mn > 6 && mn < 70) {
          issues.push({ code: 'H3w', sev: 'low', msg: `表格列宽失衡 ${mx/mn > 100 ? '>100' : (mx/mn).toFixed(1)}x (min=${mn}px): cols=[${widths.join(',')}]`, path: sel(tb) });
        }
      }
    }
  });

  // ---- H4 pre 代码块 ----
  document.querySelectorAll('.md-typeset pre').forEach(pre => {
    const r = pre.getBoundingClientRect();
    if (r.right > vw + 4) {
      const kind = reachability(pre);
      if (kind === 'clipped' || kind === 'free') {
        issues.push({ code: 'H4', sev: 'high', msg: `代码块溢出视口: right=${Math.round(r.right)} > vw=${vw}`, path: sel(pre) });
      }
    }
  });

  // ---- H5 元素重叠 ----
  const blocks = [];
  document.querySelectorAll('.md-typeset > *, .md-typeset .admonition, .md-typeset table, .doc-meta').forEach(el => {
    const r = el.getBoundingClientRect();
    const dsp = getComputedStyle(el).display;
    if (dsp === 'inline' || dsp === 'inline-block') return;   // 行内元素跨行换行时包围盒天然相交，不算重叠
    if (r.width > 40 && r.height > 10) blocks.push({ el, r, d: desc(el) });
  });
  for (let i = 0; i < blocks.length; i++) {
    for (let j = i + 1; j < blocks.length; j++) {
      const a = blocks[i], b = blocks[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const ox = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const oy = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (ox > 8 && oy > 8) {
        issues.push({ code: 'H5', sev: 'high', msg: `元素重叠 ${Math.round(ox)}x${Math.round(oy)}px: [${a.d}] ↔ [${b.d}]`, path: sel(a.el) });
      }
    }
  }

  // ---- H6 doc-meta 元数据卡 ----
  document.querySelectorAll('.doc-meta').forEach(dm => {
    const r = dm.getBoundingClientRect();
    if (r.right > vw + 2) issues.push({ code: 'H6', sev: 'high', msg: `元数据卡溢出: right=${Math.round(r.right)}` });
    const items = dm.querySelectorAll('.doc-meta__item');
    items.forEach(it => {
      if (it.scrollWidth > it.clientWidth + 2) {
        issues.push({ code: 'H6', sev: 'medium', msg: `元数据项内容溢出: «${it.textContent.trim().slice(0, 40)}»` });
      }
      const label = it.querySelector('.doc-meta__label');
      const val = it.querySelector('.doc-meta__badge, .doc-meta__value');
      if (label && val) {
        const lr = label.getBoundingClientRect(), vr = val.getBoundingClientRect();
        if (lr.right > vr.left + 2 && Math.abs(lr.top - vr.top) < Math.max(lr.height, vr.height) / 2) {
          issues.push({ code: 'H6', sev: 'medium', msg: `元数据标签与值重叠: ${label.textContent}` });
        }
      }
    });
    if (items.length % 2 === 1 && r.width > 600) {
      issues.push({ code: 'H6', sev: 'low', msg: `元数据卡 2 列网格奇数项(${items.length})，末行右侧留白` });
    }
  });

  // ---- H7 空/塌陷容器 ----
  document.querySelectorAll('.md-typeset__scrollwrap').forEach(sw => {
    if (sw.getBoundingClientRect().height < 2) {
      issues.push({ code: 'H7', sev: 'low', msg: `表格滚动容器塌陷`, path: sel(sw) });
    }
  });

  // ---- H8 表格列过窄 ----
  document.querySelectorAll('.md-typeset td, .md-typeset th').forEach(cell => {
    const r = cell.getBoundingClientRect();
    if (r.width > 0 && r.width < 46 && (cell.textContent || '').trim().length > 1) {
      issues.push({ code: 'H8', sev: 'low', msg: `表格列过窄(${Math.round(r.width)}px): «${cell.textContent.trim().slice(0, 24)}»` });
    }
  });

  // ---- H9 长不可断字符串（英文/路径/URL 硬撑列宽） ----
  document.querySelectorAll('.md-typeset p, .md-typeset li').forEach(el => {
    const txt = (el.textContent || '');
    const m = txt.match(/[A-Za-z0-9_\-\/\.\\%:]{40,}/g);
    if (!m) return;
    const st = getComputedStyle(el);
    const protectedBreak = st.overflowWrap === 'anywhere' || st.wordBreak === 'break-all' || st.wordBreak === 'break-word';
    if (!protectedBreak && el.scrollWidth > el.clientWidth + 2) {
      issues.push({ code: 'H9', sev: 'medium', msg: `长串撑破容器(${Math.max(...m.map(x=>x.length))} 字符, ${el.scrollWidth}>${el.clientWidth}): «${m[0].slice(0,40)}…»`, path: sel(el) });
    }
  });

  // ---- H10 标题锚点与文本重叠（permalink 定位） ----
  document.querySelectorAll('.md-typeset .headerlink').forEach(hl => {
    const h = hl.closest('h1,h2,h3,h4,h5,h6');
    if (!h) return;
    const hr = h.getBoundingClientRect();
    if (hr.right > vw + 2) issues.push({ code: 'H10', sev: 'low', msg: `标题锚点溢出: ${h.textContent.trim().slice(0,30)}` });
  });

  // ---- 表格结构统计（供人工判读列数过宽） ----
  const tableStats = [];
  document.querySelectorAll('.md-typeset table').forEach(tb => {
    if (tb.rows.length) {
      tableStats.push({ cols: tb.rows[0].cells.length, rows: tb.rows.length,
                        w: Math.round(tb.getBoundingClientRect().width) });
    }
  });

  const meta = {
    vw, title: document.title,
    docScrollW: docEl.scrollWidth,
    contentW: contentRoot ? Math.round(contentRoot.getBoundingClientRect().width) : 0,
    tables: tableStats.length, pres: document.querySelectorAll('.md-typeset pre').length,
    hasMeta: !!document.querySelector('.doc-meta'),
  };
  return { meta, issues, tableStats };
})()
"""


def cdp_http(path: str, method: str = "GET"):
    req = urllib.request.Request(CDP + path, method=method)
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode("utf-8", "replace")
    return json.loads(body) if body.strip() else {}


class Session:
    def __init__(self):
        vers = cdp_http("/json/version")
        self.ws = create_connection(vers["webSocketDebuggerUrl"], timeout=40, suppress_origin=True)
        self.mid = 0

    def send(self, method, params=None, session_id=None, timeout=40):
        self.mid += 1
        msg = {"id": self.mid, "method": method, "params": params or {}}
        if session_id:
            msg["sessionId"] = session_id
        self.ws.send(json.dumps(msg))
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.ws.settimeout(max(1, deadline - time.time()))
            try:
                raw = self.ws.recv()
            except Exception as e:
                raise RuntimeError(f"ws recv fail on {method}: {e}")
            data = json.loads(raw)
            if data.get("id") == self.mid:
                if "error" in data:
                    raise RuntimeError(f"{method}: {data['error']}")
                return data.get("result", {})
        raise RuntimeError(f"timeout waiting {method}")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def main():
    urls_file, out_file = sys.argv[1], sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1440
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 900
    urls = [u.strip() for u in Path(urls_file).read_text(encoding="utf-8").splitlines() if u.strip()]

    sess = Session()
    try:
        tgt = cdp_http("/json/new?about:blank", method="PUT")
    except Exception:
        tgt = cdp_http("/json/new?about:blank")
    sid = sess.send("Target.attachToTarget", {"targetId": tgt["id"], "flatten": True})["sessionId"]
    sess.send("Page.enable", session_id=sid)
    sess.send("Runtime.enable", session_id=sid)
    sess.send("Emulation.setDeviceMetricsOverride",
              {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 700},
              session_id=sid)

    results = []
    for i, url in enumerate(urls, 1):
        try:
            sess.send("Page.navigate", {"url": url}, session_id=sid)
            time.sleep(0.6)
            res = sess.send("Runtime.evaluate",
                            {"expression": PROBE_JS, "returnByValue": True},
                            session_id=sid)
            val = res.get("result", {}).get("value")
            if val is None:
                results.append({"url": url, "error": str(res)[:200]})
            else:
                val["url"] = url
                results.append(val)
        except Exception as e:
            results.append({"url": url, "error": str(e)[:200]})
        if i % 20 == 0:
            print(f"  [{i}/{len(urls)}]", file=sys.stderr)

    sess.close()
    Path(out_file).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"written {out_file} ({len(results)} pages)")


if __name__ == "__main__":
    main()

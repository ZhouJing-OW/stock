#!/usr/bin/env python3
"""
A股上涨逻辑最硬 TOP20 看板生成器
读取 data/hardlogic.json，输出单文件 HTML 看板。
核心特性：两周内新增概念自动高亮标记。
"""

import json
import os
import struct
from datetime import datetime, date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_PATH = PROJECT_DIR / "data" / "hardlogic.json"
OUTPUT_PATH = PROJECT_DIR / "hardlogic.html"
VIEWER_URL = "http://localhost:8899/viewer.html"
TDX_DIR = Path("C:/new_tdx/vipdoc")

# ===================== 加载数据 =====================
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

meta = data["meta"]
stocks = data["stocks"]
stats = data["stats"]

updated_date = datetime.strptime(meta["updated"], "%Y-%m-%d").date()
highlight_cutoff = updated_date - timedelta(days=meta["highlightWindowDays"])
hot_cutoff = updated_date - timedelta(days=3)  # 3天内超级新
today = updated_date

# ===================== 工具函数 =====================
def is_recent_concept(stock):
    """判断概念是否在两周内新增"""
    added = datetime.strptime(stock["conceptAdded"], "%Y-%m-%d").date()
    return added >= highlight_cutoff

def is_hot_concept(stock):
    """判断概念是否在3天内新增"""
    added = datetime.strptime(stock["conceptAdded"], "%Y-%m-%d").date()
    return added >= hot_cutoff

def weeks_since(date_str):
    """计算距今周数（向上取整）"""
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    days = (updated_date - d).days
    return max(1, (days + 6) // 7)

def concept_age_badge(stock):
    """概念年龄标签：3天内🔥，两周内NEW，否则显示已过N周"""
    if is_hot_concept(stock):
        return '<span class="hot-badge pulse">NEW</span>'
    if is_recent_concept(stock):
        return '<span class="new-badge pulse">NEW</span>'
    w = weeks_since(stock["conceptAdded"])
    color_class = "age-fresh" if w <= 4 else ("age-warm" if w <= 8 else "age-old")
    return f'<span class="age-badge {color_class}">已过{w}周</span>'

def tag_badge_html(tag):
    return f'<span class="tag">{tag}</span>'

# ===================== 60日均线退出检测 =====================
def check_exit_signal(stock):
    """
    退出逻辑：
    1. 概念触发后，10日线是否曾 > 60日线 × 1.10（概念曾"激活"）
    2. 只有曾激活，才检查当前是否跌破60日线
    3. 从未激活的概念不标记退出
    """
    code = stock["code"]
    added = datetime.strptime(stock["conceptAdded"], "%Y-%m-%d").date()
    
    if code.startswith("6") or code.startswith("688"):
        subdir, fname = TDX_DIR / "sh" / "lday", f"sh{code}.day"
    else:
        subdir, fname = TDX_DIR / "sz" / "lday", f"sz{code}.day"
    filepath = subdir / fname
    if not filepath.exists():
        return ("ok", "")
    
    records = []
    with open(filepath, "rb") as f:
        data = f.read()
    for i in range(0, len(data), 32):
        if i + 32 > len(data): break
        d_int = struct.unpack("I", data[i:i+4])[0]
        dt = date(d_int // 10000, (d_int % 10000) // 100, d_int % 100)
        close = struct.unpack("I", data[i+16:i+20])[0] / 100.0
        records.append({"date": dt, "close": close})
    
    if len(records) < 60:
        return ("ok", "")
    
    # 筛选概念启动后的数据
    post_records = [r for r in records if r["date"] >= added]
    if len(post_records) < 5:
        return ("ok", "")
    
    # 检查是否曾经"激活"
    activated = False
    for i, r in enumerate(post_records):
        r_date = r["date"]
        hist = [x for x in records if x["date"] <= r_date]
        if len(hist) < 60:
            continue
        ma10 = sum(x["close"] for x in hist[-10:]) / 10
        ma60 = sum(x["close"] for x in hist[-60:]) / 60
        if ma10 > ma60 * 1.10:
            activated = True
            break
    
    if not activated:
        return ("ok", "")  # 概念从未激活，不标记退出
    
    # 已激活：检查最近是否跌破60日线
    last_records = post_records[-5:]
    for r in last_records:
        r_date = r["date"]
        hist = [x for x in records if x["date"] <= r_date and x["date"] >= r_date - timedelta(days=90)]
        if len(hist) >= 40:
            ma60 = sum(x["close"] for x in hist[-60:]) / 60
            if r["close"] < ma60:
                pct = (r["close"] / ma60 - 1) * 100
                return ("exit", f"跌破60日线({pct:.1f}%) | {r_date}")
    
    return ("ok", "")

def render_reinforcement_timeline(reinfs, concept_added_date):
    """渲染概念增强时间线，含信息源链接"""
    if not reinfs:
        return ""
    items = []
    for r in reinfs:
        src_html = ""
        if r.get("source"):
            src_html = f'<a href="{r["source"]}" class="tl-source" target="_blank" rel="noopener">[源]</a>'
        items.append(f"""
          <div class="tl-item">
            <span class="tl-dot"></span>
            <span class="tl-date">{r['date']}</span>
            <span class="tl-desc">{r['desc']}</span>
            {src_html}
          </div>""")
    return f"""
      <div class="card-section reinforcement-section">
        <div class="section-title">概念增强 </div>
        <div class="timeline">{''.join(items)}</div>
      </div>"""

def render_stock_card(s, idx):
    """渲染单张标的卡片"""
    recent = is_recent_concept(s)
    hot = is_hot_concept(s)
    age_badge = concept_age_badge(s)
    
    # 60日均线退出检测
    exit_status, exit_desc = check_exit_signal(s)
    
    card_class = "card"
    if hot:
        card_class += " card-hot"
    elif recent:
        card_class += " card-recent"
    if exit_status == "exit":
        card_class += " card-exit"
    
    # 逻辑要点（短摘要）
    core_short = s["coreLogic"]
    
    tags_html = "".join(tag_badge_html(t) for t in s["tags"])
    
    # 概念增强时间线
    reinfs = s.get("conceptReinforcements", [])
    reinf_html = render_reinforcement_timeline(reinfs, s["conceptAdded"])
    
    # 概念来源链接
    source_url = s.get("conceptSourceUrl", "")
    source_link_html = ""
    if source_url:
        source_link_html = f'<a href="{source_url}" class="concept-source-link" target="_blank" rel="noopener">信息源 ↗</a>'
    
    # 评分
    score = s.get("score", 5.0)
    score_color = "score-high" if score >= 9.0 else ("score-mid" if score >= 8.0 else "score-ok")
    score_html = f'<span class="score-badge {score_color}">{score:.1f}</span>'
    
    return f"""
    <div class="{card_class}" id="s{s['id']}" data-concept-date="{s['conceptAdded']}">
      <div class="card-header">
        <span class="card-idx">#{s['id']:02d}</span>
        <div class="card-category">
          <span class="cat">{s['category']}</span>
          <span class="subcat">{s['subCategory']}</span>
        </div>
        {score_html}
        {age_badge}
        {'<span class="exit-badge" title="' + exit_desc + '">⚠ 退出</span>' if exit_status == "exit" else ""}
      </div>
      <div class="card-title-row">
        <a href="{VIEWER_URL}?code={s['code']}" class="stock-link" target="_blank" rel="noopener" title="查看基本面分析">
          <span class="stock-name">{s['name']}</span>
          <span class="stock-code">{s['code']} · {s['market']}</span>
        </a>
        <button class="tdx-btn" onclick="navigator.clipboard.writeText('TDX_JUMP:{s['code']}').then(()=>{{this.textContent='✓';setTimeout(()=>{{this.textContent='TDX'}},800)}})" title="复制代码到剪贴板，AHK自动打开通达信">TDX</button>
      </div>
      <div class="card-section">
        <div class="section-title">上涨硬逻辑</div>
        <p class="logic-text">{core_short}</p>
      </div>
      <div class="card-section">
        <div class="section-title">供需格局</div>
        <p class="sd-text">{s['supplyDemand']}</p>
      </div>
      <div class="card-metrics">
        <div class="metric">
          <span class="metric-label">价格信号</span>
          <span class="metric-value">{s['priceSignal']}</span>
        </div>
        <div class="metric">
          <span class="metric-label">核心催化</span>
          <span class="metric-value">{s['catalyst']}</span>
        </div>
      </div>
      {reinf_html}
      <div class="card-footer">
        <div class="tags-row">{tags_html}</div>
        <div class="concept-date" data-recent="{str(recent).lower()}" data-hot="{str(hot).lower()}">
          概念触发：{s['conceptAdded']}
          {" NEW" if (hot or recent) else ""}
          {source_link_html}
        </div>
      </div>
      <div class="card-risk">
        <span class="risk-icon">⚠</span> {s['riskNote'][:100]}{'...' if len(s['riskNote']) > 100 else ''}
      </div>
    </div>"""

def render_category_section(cat_name, cat_stocks):
    """渲染分类板块"""
    cards = "\n".join(render_stock_card(s, s["id"]) for s in cat_stocks)
    return f"""
    <div class="category-section">
      <h2 class="cat-title">{cat_name}</h2>
      <div class="cards-grid">{cards}</div>
    </div>"""

# ===================== 分类排序（按标的数量降序，数量多的为主线板块靠前） =====================
from collections import Counter
cat_counts = Counter(s["category"] for s in stocks)
category_order = sorted(set(s["category"] for s in stocks), key=lambda c: -cat_counts[c])

grouped = {}
for cat in category_order:
    grouped[cat] = [s for s in stocks if s["category"] == cat]

# ===================== 统计摘要 =====================
total_stocks = len(stocks)
recent_count = sum(1 for s in stocks if is_recent_concept(s))
recent_names = [s["name"] for s in stocks if is_recent_concept(s)]

# 统计最近两周内的概念增强事件(仅用于统计计数，不在顶部提示中展示)
recent_reinforcement_count = 0
for s in stocks:
    for r in s.get("conceptReinforcements", []):
        rd = datetime.strptime(r["date"], "%Y-%m-%d").date()
        if rd >= highlight_cutoff:
            recent_reinforcement_count += 1

market_stats = stats["totalMarkets"]
market_summary = " · ".join(f"{m} {n}只" for m, n in market_stats.items())

# ===================== 生成HTML =====================
category_sections = "\n".join(
    render_category_section(cat, grouped.get(cat, []))
    for cat in category_order if grouped.get(cat)
)

# 顶部提示：仅显示真正的新增概念，不展示增强事件
recent_highlight = ""
if recent_names:
    recent_highlight = f"""
    <div class="recent-alert">
      <span class="alert-dot"></span>
      近{meta['highlightWindowDays']}天新增概念：<strong>{'、'.join(recent_names)}</strong>（卡片右上角 NEW 标记）
    </div>"""

# ===================== 快速索引 =====================
def one_liner(s):
    """提取一句话硬逻辑"""
    logic = s["coreLogic"]
    # 取第一句或前60字
    first_sentence = logic.split("。")[0].split("；")[0]
    if len(first_sentence) > 50:
        first_sentence = first_sentence[:50] + "…"
    return first_sentence

def render_index():
    """生成顶部快速索引（按板块标的数量降序）"""
    # 按板块数量降序排列
    from collections import Counter
    idx_cat_counts = Counter(s["category"] for s in stocks)
    idx_order = sorted(set(s["category"] for s in stocks), key=lambda c: -idx_cat_counts[c])
    
    items = []
    for cat in idx_order:
        cat_stocks = sorted([s for s in stocks if s["category"] == cat], key=lambda x: -x.get("score", 5.0))
        for s in cat_stocks:
            recent = is_recent_concept(s)
            hot = is_hot_concept(s)
            if hot:
                new_mark = '<span class="idx-hot">N</span>'
            elif recent:
                new_mark = '<span class="idx-new">N</span>'
            else:
                new_mark = ''
            # 退出标记
            exit_mark = '<span class="idx-exit">✕</span>' if check_exit_signal(s)[0] == "exit" else ''
            short = one_liner(s)
            items.append(f"""
        <a href="#s{s['id']}" class="idx-item" data-concept-date="{s['conceptAdded']}">
          <span class="idx-code">{s['code']}</span>
          <span class="idx-name">{s['name']}{new_mark}{exit_mark}</span>
          <span class="idx-logic">{short}</span>
        </a>""")
    return f"""
    <div class="quick-index">
      <div class="idx-header">
        <span class="idx-title">快速索引</span>
        <span class="idx-count">{len(stocks)} 只标的</span>
      </div>
      <div class="idx-grid">{''.join(items)}</div>
    </div>"""

index_html = render_index()

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A股上涨逻辑最硬 · {meta['updated']}</title>
<style>
/* =============== Modern Dashboard =============== */
:root {{
  --accent: #5B9BD5;
  --accent-hover: #4A8AC4;
  --accent-light: rgba(91,155,213,.12);
  --bg: #2A2E36;
  --bg-elevated: #32363E;
  --card-bg: #ECEEF1;
  --card-hover: #F2F3F6;
  --text-on-dark: #D8DBE0;
  --text-on-dark-secondary: #959AA2;
  --text-on-dark-muted: #6C7178;
  --text: #1E2024;
  --text-secondary: #585C63;
  --text-muted: #90949B;
  --line: rgba(0,0,0,.08);
  --line-dark: rgba(255,255,255,.07);
  --shadow-sm: 0 2px 6px rgba(0,0,0,.18);
  --shadow-md: 0 4px 16px rgba(0,0,0,.22);
  --shadow-lg: 0 8px 28px rgba(0,0,0,.28);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --overlay1: rgba(0,0,0,.03);
  --overlay2: rgba(0,0,0,.06);
  --success: #52B788;
  --danger: #E05565;
  --coral: #E8877B;
  --new-glow: rgba(91,155,213,.22);
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  font-family: system-ui,-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}

.container {{
  max-width: 1800px;
  margin: 0 auto;
  padding: 56px 40px 96px;
}}

/* =============== Header =============== */
.header {{
  text-align: center;
  margin-bottom: 48px;
}}

.header h1 {{
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-on-dark);
  letter-spacing: -.01em;
  margin-bottom: 6px;
}}

.header .subtitle {{
  font-size: 0.95rem;
  color: var(--text-on-dark-secondary);
  font-weight: 400;
}}

.header .meta-row {{
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 28px;
  flex-wrap: wrap;
}}

.meta-item {{
  font-size: 0.8rem;
  color: var(--text-on-dark-muted);
}}

.meta-item strong {{
  color: var(--text-on-dark-secondary);
  font-weight: 600;
}}

/* =============== Stats Bar =============== */
.stats-bar {{
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 32px;
}}

.stat-chip {{
  font-size: 0.78rem;
  color: var(--text-on-dark-secondary);
  background: var(--bg-elevated);
  border: 1px solid var(--line-dark);
  border-radius: 100px;
  padding: 4px 14px;
}}

.stat-chip .num {{
  color: var(--accent);
  font-family: 'JetBrains Mono',ui-monospace,monospace;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}}

/* =============== Filter Bar =============== */
.filter-bar {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
}}

.filter-label {{
  font-size: 0.8rem;
  color: var(--text-on-dark-secondary);
  margin-right: 4px;
}}

.filter-btn {{
  font-family: system-ui,-apple-system,'PingFang SC',sans-serif;
  font-size: 0.76rem;
  color: var(--text-on-dark-secondary);
  background: var(--bg-elevated);
  border: 1px solid var(--line-dark);
  border-radius: 100px;
  padding: 5px 18px;
  cursor: pointer;
  transition: all .15s;
}}

.filter-btn:hover {{
  border-color: rgba(91,155,213,.3);
  color: var(--text-on-dark);
}}

.filter-btn.active {{
  color: #fff;
  background: var(--accent);
  border-color: var(--accent);
}}

.filter-sep {{
  color: var(--text-on-dark-muted);
  font-size: 0.7rem;
  margin: 0 4px;
  opacity: 0.5;
}}

.toggle-btn.active {{
  color: #fff;
  background: #DC3545;
  border-color: #DC3545;
}}

.exit-toggle-btn {{
  font-family: system-ui,-apple-system,'PingFang SC',sans-serif;
  font-size: 0.76rem;
  color: var(--text-on-dark-secondary);
  background: var(--bg-elevated);
  border: 1px solid var(--line-dark);
  border-radius: 100px;
  padding: 5px 18px;
  cursor: pointer;
  transition: all .15s;
}}

.exit-toggle-btn:hover {{
  border-color: rgba(220,53,69,.35);
}}

.exit-toggle-btn.active {{
  color: #fff;
  background: #DC3545;
  border-color: #DC3545;
}}

/* 默认隐藏退出标的 */
.card-exit {{
  display: none;
}}

.card-exit.visible {{
  display: block;
  border-color: rgba(220,53,69,.35);
  box-shadow: var(--shadow-sm);
  opacity: 0.85;
}}

.card.hidden, .idx-item.hidden {{
  display: none;
}}

/* =============== Recent Alert =============== */
.recent-alert {{
  background: var(--bg-elevated);
  border: 1px solid rgba(91,155,213,.18);
  border-radius: var(--radius-sm);
  padding: 10px 18px;
  margin-bottom: 32px;
  font-size: 0.88rem;
  color: var(--text-on-dark);
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}}

.alert-dot {{
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--accent);
  animation: alertPulse 2s ease-in-out infinite;
}}

@keyframes alertPulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.3; }}
}}

/* =============== Quick Index =============== */
.quick-index {{
  margin-bottom: 40px;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--line);
}}

.idx-header {{
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
}}

.idx-title {{
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-on-dark);
}}

.idx-count {{
  font-size: 0.75rem;
  color: var(--text-on-dark-muted);
}}

.idx-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 4px;
}}

.idx-item {{
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  text-decoration: none;
  transition: background .12s;
}}

.idx-item:hover {{
  background: var(--accent-light);
}}

.idx-code {{
  font-family: 'JetBrains Mono',ui-monospace,monospace;
  font-size: 0.68rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  min-width: 54px;
}}

.idx-name {{
  font-size: 0.85rem;
  color: var(--text);
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}}

.idx-new {{
  font-size: 0.58rem;
  color: #fff;
  background: var(--accent);
  padding: 1px 5px;
  border-radius: 6px;
  margin-left: 3px;
  font-weight: 600;
  vertical-align: middle;
}}

.idx-hot {{
  font-size: 0.58rem;
  color: #fff;
  background: #E86A4D;
  padding: 1px 5px;
  border-radius: 6px;
  margin-left: 3px;
  font-weight: 600;
  vertical-align: middle;
}}

.idx-exit {{
  font-size: 0.58rem;
  color: #fff;
  background: #DC3545;
  padding: 1px 5px;
  border-radius: 6px;
  margin-left: 3px;
  font-weight: 600;
  vertical-align: middle;
}}

.idx-logic {{
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}

/* =============== Category Section =============== */
.category-section {{
  margin-bottom: 48px;
}}

.cat-title {{
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-on-dark);
  padding-left: 14px;
  border-left: 3px solid var(--accent);
  margin-bottom: 18px;
  letter-spacing: -.01em;
}}

/* =============== Cards Grid =============== */
.cards-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}}

/* =============== Card =============== */
.card {{
  background: var(--card-bg);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  padding: 22px 24px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow .2s ease, transform .2s ease, border-color .2s ease;
  position: relative;
}}

.card:hover {{
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: rgba(74,144,217,.12);
}}

.card-hot {{
  border-color: rgba(232,106,77,.4);
  box-shadow: var(--shadow-md), 0 0 24px rgba(232,106,77,.18);
}}

.exit-badge {{
  font-size: 0.66rem;
  font-weight: 600;
  color: #fff;
  background: #DC3545;
  padding: 2px 8px;
  border-radius: 100px;
  letter-spacing: .03em;
  white-space: nowrap;
}}

.card-header {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}}

.card-idx {{
  font-family: 'JetBrains Mono',ui-monospace,monospace;
  font-size: 0.78rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}}

.card-category {{
  display: flex;
  gap: 6px;
  align-items: baseline;
}}

.cat {{
  font-size: 0.74rem;
  font-weight: 500;
  color: var(--accent);
}}

.subcat {{
  font-size: 0.72rem;
  color: var(--text-muted);
}}

/* =============== Score Badge =============== */
.score-badge {{
  font-family: 'JetBrains Mono',ui-monospace,monospace;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 1px 9px;
  border-radius: 100px;
  letter-spacing: -.01em;
  font-variant-numeric: tabular-nums;
  margin-left: auto;
  margin-right: 6px;
}}

.score-high {{
  color: #1A7D4F;
  background: rgba(26,125,79,.12);
  border: 1px solid rgba(26,125,79,.22);
}}

.score-mid {{
  color: #A6792B;
  background: rgba(166,121,43,.10);
  border: 1px solid rgba(166,121,43,.18);
}}

.score-ok {{
  color: var(--text-muted);
  background: var(--overlay1);
  border: 1px solid var(--line);
}}

.new-badge {{
  font-size: 0.66rem;
  font-weight: 600;
  color: #fff;
  background: var(--accent);
  padding: 2px 8px;
  border-radius: 100px;
  margin-left: auto;
  letter-spacing: .03em;
}}

.hot-badge {{
  font-size: 0.66rem;
  font-weight: 600;
  color: #fff;
  background: #E86A4D;
  padding: 2px 8px;
  border-radius: 100px;
  margin-left: auto;
  letter-spacing: .03em;
}}

/* Hot card glow */
.card-hot {{
  border-color: rgba(232,106,77,.4);
  box-shadow: var(--shadow-md), 0 0 24px rgba(232,106,77,.18);
}}

.pulse {{
  animation: badgePulse 3s ease-in-out infinite;
}}

@keyframes badgePulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.65; }}
}}

/* =============== Age Badge =============== */
.age-badge {{
  font-size: 0.66rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 100px;
  margin-left: auto;
  white-space: nowrap;
}}

.age-fresh {{
  color: #3B8C5A;
  background: rgba(59,140,90,.1);
  border: 1px solid rgba(59,140,90,.2);
}}

.age-warm {{
  color: #B37A3A;
  background: rgba(179,122,58,.1);
  border: 1px solid rgba(179,122,58,.18);
}}

.age-old {{
  color: var(--text-muted);
  background: var(--overlay1);
  border: 1px solid var(--line);
}}

/* =============== Card Title =============== */
.card-title-row {{
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
}}

.stock-link {{
  display: flex;
  align-items: baseline;
  gap: 8px;
  text-decoration: none;
  transition: opacity .15s;
}}

.stock-link:hover {{
  opacity: 0.78;
}}

.stock-name {{
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
}}

.stock-code {{
  font-family: 'JetBrains Mono',ui-monospace,monospace;
  font-size: 0.76rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}}

.tdx-btn {{
  font-size: 0.65rem;
  font-weight: 600;
  font-family: 'JetBrains Mono',ui-monospace,monospace;
  color: var(--text-muted);
  background: var(--overlay1);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 2px 7px;
  cursor: pointer;
  margin-left: auto;
  transition: all .15s;
  letter-spacing: .02em;
}}

.tdx-btn:hover {{
  background: var(--accent-light);
  border-color: rgba(91,155,213,.25);
}}

/* =============== Card Content =============== */
.card-section {{
  margin-bottom: 10px;
}}

.section-title {{
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: .05em;
  margin-bottom: 4px;
}}

.logic-text, .sd-text {{
  font-size: 0.88rem;
  color: var(--text);
  line-height: 1.6;
}}

.sd-text {{
  font-size: 0.84rem;
  color: var(--text-secondary);
}}

/* =============== Metrics =============== */
.card-metrics {{
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 12px 0;
  padding: 10px 12px;
  background: var(--overlay1);
  border-radius: var(--radius-sm);
  border: 1px solid var(--line);
}}

.metric {{
  display: flex;
  gap: 8px;
  align-items: baseline;
}}

.metric-label {{
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--text-muted);
  white-space: nowrap;
  min-width: 52px;
}}

.metric-value {{
  font-size: 0.86rem;
  color: var(--text);
}}

/* =============== Reinforcement Timeline =============== */
.reinforcement-section {{
  margin: 10px 0;
  padding: 10px 12px;
  background: rgba(74,144,217,.03);
  border-radius: var(--radius-sm);
  border: 1px dashed rgba(74,144,217,.15);
}}

.reinforcement-section .section-title {{
  margin-bottom: 6px;
}}

.timeline {{
  display: flex;
  flex-direction: column;
  gap: 5px;
}}

.tl-item {{
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-size: 0.78rem;
}}

.tl-dot {{
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  margin-top: 5px;
}}

.tl-date {{
  font-family: 'JetBrains Mono',ui-monospace,monospace;
  font-size: 0.7rem;
  color: var(--accent);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  flex-shrink: 0;
}}

.tl-desc {{
  color: var(--text-secondary);
  line-height: 1.45;
}}

.tl-source {{
  font-size: 0.66rem;
  color: var(--accent);
  text-decoration: none;
  opacity: 0.65;
  flex-shrink: 0;
  transition: opacity .15s;
  font-weight: 500;
}}

.tl-source:hover {{
  opacity: 1;
  text-decoration: underline;
}}

.concept-source-link {{
  font-size: 0.68rem;
  color: var(--accent);
  text-decoration: none;
  opacity: 0.65;
  margin-left: 4px;
  transition: opacity .15s;
  font-weight: 500;
}}

.concept-source-link:hover {{
  opacity: 1;
  text-decoration: underline;
}}

/* =============== Card Footer =============== */
.card-footer {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid var(--line);
  margin-top: 4px;
}}

.tags-row {{
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}}

.tag {{
  font-size: 0.7rem;
  color: var(--text-muted);
  background: var(--overlay1);
  padding: 2px 7px;
  border-radius: 4px;
}}

.concept-date {{
  font-size: 0.73rem;
  color: var(--text-muted);
  white-space: nowrap;
}}

.concept-date[data-recent="true"] {{
  color: var(--accent);
  font-weight: 600;
}}

.concept-date[data-hot="true"] {{
  color: #E86A4D;
  font-weight: 600;
}}

/* =============== Risk =============== */
.card-risk {{
  margin-top: 8px;
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.45;
  font-style: italic;
}}

.risk-icon {{
  color: var(--coral);
  margin-right: 1px;
}}

/* =============== Footer =============== */
.page-footer {{
  text-align: center;
  padding-top: 40px;
  border-top: 1px solid var(--line-dark);
  margin-top: 56px;
}}

.page-footer p {{
  font-size: 0.8rem;
  color: var(--text-on-dark-muted);
}}

/* =============== Responsive =============== */
@media (max-width: 920px) {{
  .cards-grid {{
    grid-template-columns: 1fr;
  }}
  .idx-grid {{
    grid-template-columns: 1fr;
  }}
  .container {{
    padding: 24px 16px 48px;
  }}
  .header h1 {{
    font-size: 1.5rem;
  }}
}}

/* =============== Print =============== */
@media print {{
  body {{ background: #fff; }}
  .card {{ box-shadow: none; border: 1px solid #ddd; break-inside: avoid; }}
}}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <header class="header">
    <h1>{meta['title']}</h1>
    <p class="subtitle">{meta['subtitle']}</p>
    <div class="meta-row">
      <span class="meta-item">更新日期 <strong>{meta['updated']}</strong></span>
      <span class="meta-item">标的数量 <strong>{total_stocks}只</strong></span>
      <span class="meta-item">覆盖市场 <strong>{market_summary}</strong></span>
      <span class="meta-item">更新频率 <strong>{meta['updateFreq']}</strong></span>
    </div>
  </header>

  <!-- Stats Chips -->
  <div class="stats-bar">
    {''.join(f'<span class="stat-chip">{sc["name"]} <span class="num">{sc["count"]}</span></span>' for sc in stats['categories'])}
    <span class="stat-chip">🆕 近{meta['highlightWindowDays']}天新增 <span class="num">{recent_count}</span> 个</span>
    <span class="stat-chip">🔺 近{meta['highlightWindowDays']}天增强 <span class="num">{recent_reinforcement_count}</span> 次</span>
  </div>

  <!-- Concept Age Filter -->
  <div class="filter-bar">
    <span class="filter-label">概念周期</span>
    <button class="filter-btn active" data-filter="all">全部</button>
    <button class="filter-btn" data-filter="w4">4周内</button>
    <button class="filter-btn" data-filter="new">NEW</button>
    <span class="filter-sep">|</span>
    <button class="exit-toggle-btn" id="toggle-exit">显示已退出</button>
  </div>

  <!-- Recent Alert -->
  {recent_highlight}

  <!-- Quick Index -->
  {index_html}

  <!-- Category Sections -->
  {category_sections}

  <!-- Footer -->
  <footer class="page-footer">
    <p>{meta['author']} · 数据更新于 {meta['updated']} · 脚本：python generate_dashboard.py</p>
    <p style="margin-top:4px">⚠ 本看板仅供研究参考，不构成任何投资建议。市场有风险，投资需谨慎。</p>
  </footer>

</div>"""

# 注入概念周期筛选器
filter_js = f"""<script>
(function() {{
  var cutoffNew = 14;
  var cutoffW4 = 28;
  var today = new Date('{meta["updated"]}');
  function daysSince(d) {{ return Math.floor((today - new Date(d)) / 86400000); }}
  function applyFilter(filter) {{
    document.querySelectorAll(".card, .idx-item").forEach(function(el) {{
      var d = el.getAttribute("data-concept-date");
      if (!d) return;
      // 退出标的由切换按钮控制，不参与周期筛选
      if (el.classList.contains("card-exit") || (el.tagName === "A" && el.getAttribute("href") && document.querySelector(el.getAttribute("href") + ".card-exit"))) return;
      var days = daysSince(d);
      var show = filter === "new" ? days <= cutoffNew : (filter === "w4" ? days <= cutoffW4 : true);
      el.classList.toggle("hidden", !show);
    }});
  }}
  document.querySelectorAll(".filter-btn").forEach(function(btn) {{
    btn.addEventListener("click", function() {{
      document.querySelectorAll(".filter-btn").forEach(function(b) {{ b.classList.remove("active"); }});
      this.classList.add("active");
      applyFilter(this.getAttribute("data-filter"));
    }});
  }});

  // 已退出标的切换
  var exitToggle = document.getElementById("toggle-exit");
  if (exitToggle) {{
    exitToggle.addEventListener("click", function() {{
      this.classList.toggle("active");
      var show = this.classList.contains("active");
      document.querySelectorAll(".card-exit").forEach(function(card) {{
        card.classList.toggle("visible", show);
      }});
      // 同步切换索引中的对应条目
      document.querySelectorAll(".idx-item").forEach(function(item) {{
        var href = item.getAttribute("href");
        if (href && document.querySelector(href + ".card-exit")) {{
          item.classList.toggle("hidden", !show);
        }}
      }});
    }});
    // 初始状态：隐藏退出标的的索引条目
    document.querySelectorAll(".idx-item").forEach(function(item) {{
      var href = item.getAttribute("href");
      if (href && document.querySelector(href + ".card-exit")) {{
        item.classList.add("hidden");
      }}
    }});
  }}
}})();
</script>
</body>
</html>
"""
html += filter_js

# ===================== 写入文件 =====================
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 看板已生成: {OUTPUT_PATH}")
print(f"   标的总数: {total_stocks}")
print(f"   最近{meta['highlightWindowDays']}天新增概念: {recent_count}个")
print(f"   覆盖分类: {len(cat_counts)} 个大类")

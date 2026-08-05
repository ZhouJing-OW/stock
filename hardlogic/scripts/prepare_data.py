#!/usr/bin/env python3
"""
硬逻辑看板生成器 v4.0
职责：
1. 读取 data/hardlogic.json + 通达信日K → 计算退出信号
2. 输出 data/dashboard_data.json（富数据，供 HTML 运行时 fetch）
3. 输出 hardlogic.html（静态模板，不含业务数据，JS 运行时渲染）
"""

import json
import struct
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_PATH = PROJECT_DIR / "data" / "hardlogic.json"
OUTPUT_DATA = PROJECT_DIR / "data" / "dashboard_data.json"
OUTPUT_HTML = PROJECT_DIR / "hardlogic.html"
TEMPLATE_HTML = SCRIPT_DIR / "hardlogic.template.html"
VIEWER_URL = "http://localhost:8899/viewer.html"
TDX_DIR = Path("C:/new_tdx/vipdoc")

# ===================== 加载数据 =====================
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

meta = data["meta"]
stocks = data["stocks"]

updated_date = datetime.strptime(meta["updated"], "%Y-%m-%d").date()
highlight_cutoff = updated_date - timedelta(days=meta["highlightWindowDays"])
hot_cutoff = updated_date - timedelta(days=3)


def is_hot(added_str):
    return datetime.strptime(added_str, "%Y-%m-%d").date() >= hot_cutoff


def is_recent(added_str):
    return datetime.strptime(added_str, "%Y-%m-%d").date() >= highlight_cutoff


def weeks_since(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    days = (updated_date - d).days
    return max(1, (days + 6) // 7)


# ===================== 60日均线退出检测 =====================
def check_exit_signal(code, added_str):
    """退出逻辑：先验证概念曾激活（10日线曾>60日线×1.10），再检查当前是否跌破60日线"""
    added = datetime.strptime(added_str, "%Y-%m-%d").date()

    if code.startswith("6"):
        subdir, fname = TDX_DIR / "sh" / "lday", f"sh{code}.day"
    else:
        subdir, fname = TDX_DIR / "sz" / "lday", f"sz{code}.day"
    filepath = subdir / fname
    if not filepath.exists():
        return ("ok", "")

    records = []
    with open(filepath, "rb") as f:
        raw = f.read()
    for i in range(0, len(raw), 32):
        if i + 32 > len(raw):
            break
        d_int = struct.unpack("I", raw[i:i+4])[0]
        dt = date(d_int // 10000, (d_int % 10000) // 100, d_int % 100)
        close = struct.unpack("I", raw[i+16:i+20])[0] / 100.0
        records.append({"date": dt, "close": close})

    if len(records) < 60:
        return ("ok", "")

    post = [r for r in records if r["date"] >= added]
    if len(post) < 5:
        return ("ok", "")

    # 激活检测：10日线曾 > 60日线 × 1.10
    activated = False
    for r in post:
        hist = [x for x in records if x["date"] <= r["date"]]
        if len(hist) < 60:
            continue
        ma10 = sum(x["close"] for x in hist[-10:]) / 10
        ma60 = sum(x["close"] for x in hist[-60:]) / 60
        if ma10 > ma60 * 1.10:
            activated = True
            break

    if not activated:
        return ("ok", "")

    # 检查最近5日是否跌破60日线
    for r in post[-5:]:
        r_date = r["date"]
        hist = [x for x in records if x["date"] <= r_date and x["date"] >= r_date - timedelta(days=90)]
        if len(hist) >= 40:
            ma60 = sum(x["close"] for x in hist[-60:]) / 60
            if r["close"] < ma60:
                pct = (r["close"] / ma60 - 1) * 100
                return ("exit", f"跌破60日线({pct:.1f}%) | {r_date}")
    return ("ok", "")


# ===================== 构建富数据 =====================
enriched = []
for s in stocks:
    code = s["code"]
    exit_status, exit_desc = check_exit_signal(code, s["conceptAdded"])

    # 概念年龄类别: hot / new / aged
    if is_hot(s["conceptAdded"]):
        age_class = "hot"
    elif is_recent(s["conceptAdded"]):
        age_class = "new"
    else:
        age_class = f"aged{weeks_since(s['conceptAdded'])}"

    enriched.append({
        **s,
        "ageClass": age_class,
        "ageWeeks": weeks_since(s["conceptAdded"]),
        "exitStatus": exit_status,
        "exitDesc": exit_desc,
        "viewerUrl": VIEWER_URL,
    })

# 分类排序（按标的数量降序），组内按评分降序
cat_counts = Counter(s["category"] for s in enriched)
category_order = sorted(set(s["category"] for s in enriched), key=lambda c: -cat_counts[c])

grouped = {}
for cat in category_order:
    cat_stocks = sorted(
        [s for s in enriched if s["category"] == cat],
        key=lambda x: -x.get("score", 5.0)
    )
    grouped[cat] = cat_stocks

# ===================== 输出 dashboard_data.json =====================
dashboard = {
    "meta": meta,
    "categoryOrder": category_order,
    "groups": grouped,
    "viewerUrl": VIEWER_URL,
    "recentNames": [s["name"] for s in enriched if is_recent(s["conceptAdded"])],
    "exitCount": sum(1 for s in enriched if s["exitStatus"] == "exit"),
    "hotCount": sum(1 for s in enriched if s["ageClass"] == "hot"),
}

OUTPUT_DATA.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_DATA, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, ensure_ascii=False, indent=2)

# ===================== 输出 hardlogic.html（静态模板） =====================
if TEMPLATE_HTML.exists():
    with open(TEMPLATE_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 静态看板已生成: {OUTPUT_HTML}")

print(f"✅ 富数据已生成: {OUTPUT_DATA}")
print(f"   标的总数: {len(stocks)} | 已退出: {dashboard['exitCount']} | 3天内新增: {dashboard['hotCount']}")

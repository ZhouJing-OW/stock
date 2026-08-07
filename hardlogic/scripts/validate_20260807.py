# -*- coding: utf-8 -*-
"""校验 hardlogic.json 迁移结果"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "hardlogic.json"
with open(DATA, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]
errors = []

# 1. id 连续性
ids = [s["id"] for s in stocks]
if ids != list(range(1, len(stocks) + 1)):
    errors.append(f"id 不连续: {ids[:10]}...")

# 2. 分类内评分降序
cat_order = []
for s in stocks:
    if s["category"] not in cat_order:
        cat_order.append(s["category"])
for cat in cat_order:
    cat_stocks = [s for s in stocks if s["category"] == cat]
    scores = [s["score"] for s in cat_stocks]
    if scores != sorted(scores, reverse=True):
        errors.append(f"分类 {cat} 未按评分降序: {scores}")

# 3. reinforcements 上限 + 日期降序
for s in stocks:
    r = s.get("conceptReinforcements", [])
    if len(r) > 3:
        errors.append(f"{s['name']} reinforcements 超过3条: {len(r)}")
    dates = [e["date"] for e in r]
    if dates != sorted(dates, reverse=True):
        errors.append(f"{s['name']} reinforcements 未按日期降序: {dates}")

# 4. 新卡片
new_cards = {
    "301308": ("江波龙", "2026-08-05", 4.25),
    "600176": ("中国巨石", "2026-08-04", 4.0),
    "688120": ("华海清科", "2026-08-03", 4.25),
    "300604": ("长川科技", "2026-08-05", 3.75),
}
for code, (name, added, score) in new_cards.items():
    s = next((x for x in stocks if x["code"] == code), None)
    if s is None:
        errors.append(f"缺少新卡片 {code} {name}")
    else:
        if s["conceptAdded"] != added:
            errors.append(f"{name} conceptAdded 应为 {added}, 实际 {s['conceptAdded']}")
        if s["score"] != score:
            errors.append(f"{name} score 应为 {score}, 实际 {s['score']}")

# 5. 评分调整
score_checks = {"688525": 8.5, "300480": 8.5, "688170": 8.0, "603256": 8.0,
                "002409": 7.0, "301377": 8.0, "000962": 8.5}
for code, want in score_checks.items():
    s = next((x for x in stocks if x["code"] == code), None)
    if s is None or s["score"] != want:
        errors.append(f"{code} score 应为 {want}, 实际 {s['score'] if s else '缺失'}")

# 6. stats 一致性
from collections import Counter
cat_counts = Counter(s["category"] for s in stocks)
for c in data["stats"]["categories"]:
    if cat_counts[c["name"]] != c["count"]:
        errors.append(f"stats 分类计数不一致: {c['name']} 应 {cat_counts[c['name']]} 实 {c['count']}")
mkt = Counter(s["market"] for s in stocks)
if data["stats"]["totalStocks"] != len(stocks):
    errors.append("totalStocks 不一致")
if data["stats"]["totalMarkets"] != {"主板": mkt["主板"], "创业板": mkt["创业板"], "科创板": mkt["科创板"]}:
    errors.append(f"totalMarkets 不一致: {data['stats']['totalMarkets']} vs {dict(mkt)}")

# 7. meta.updated
if data["meta"]["updated"] != "2026-08-07":
    errors.append("meta.updated 未更新")

# 8. 输出各分类概况
print(f"✅ JSON 有效 | 标的: {len(stocks)} | meta.updated: {data['meta']['updated']}")
for cat in cat_order:
    cat_stocks = [s for s in stocks if s["category"] == cat]
    brief = " | ".join(f"{s['name']}{s['score']}" for s in cat_stocks)
    print(f"  [{cat}] {len(cat_stocks)}只: {brief}")

print(f"\n⚠️ 校验错误 {len(errors)} 条:")
for e in errors:
    print("  -", e)
if not errors:
    print("  （无错误，全部通过）")

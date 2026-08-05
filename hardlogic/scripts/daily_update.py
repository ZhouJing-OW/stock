#!/usr/bin/env python3
"""硬逻辑看板每日更新脚本（处理定时任务超时后的持久化操作）"""

import json
import os
import sys
from pathlib import Path
from datetime import date

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR.parent / "data" / "hardlogic.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]
today = date.today().isoformat()  # 2026-07-31

changes_log = []

# ═══════════════════════════════════════
# 1. 修复所有ID冲突和重复
# ═══════════════════════════════════════

# 1a. 查重 id 和 股票代码
seen_ids = {}
seen_codes = {}
for i, s in enumerate(stocks):
    sid = s.get("id")
    code = s.get("code")
    if sid in seen_ids:
        changes_log.append(f"ID冲突修复: {s['name']}({code}) id={sid} 与 {seen_ids[sid]['name']}({seen_ids[sid]['code']}) 冲突，重新编号")
    seen_ids[sid] = s
    
    if code in seen_codes:
        changes_log.append(f"代码重复: {code} ({s['name']}) 已存在索引{seen_codes[code]}")
    seen_codes[code] = i

# 1b. 合并 风华高科 重复 (id:16 和 id:20)
fenghua_to_remove = None
fenghua_to_keep = None
for s in stocks:
    if s.get("code") == "000636":
        if s.get("id") == 16:
            fenghua_to_remove = s
        elif s.get("id") == 20:
            fenghua_to_keep = s

if fenghua_to_remove and fenghua_to_keep:
    # 把旧id=16的逻辑合并到新id=20的coreLogic中（旧版有一些细节新版没有）
    old_logic = fenghua_to_remove.get("coreLogic", "")
    new_logic = fenghua_to_keep.get("coreLogic", "")
    # 添加旧版catalyst字段
    old_catalyst = fenghua_to_remove.get("catalyst", "")
    if old_catalyst and old_catalyst not in new_logic:
        fenghua_to_keep["coreLogic"] = new_logic + f"\n【旧版保留】催化剂: {old_catalyst}"
    # 合并旧版tags
    old_tags = set(fenghua_to_remove.get("tags", []))
    new_tags = set(fenghua_to_keep.get("tags", []))
    fenghua_to_keep["tags"] = sorted(new_tags | old_tags)
    # 移除旧条目
    stocks.remove(fenghua_to_remove)
    changes_log.append("风华高科重复合并: 移除id=16旧条目，保留id=20新条目")

# 1c. 给 联合化学 补 category 字段并修正id
for s in stocks:
    if s.get("code") == "301209" and "category" not in s:
        s["category"] = "半导体上游"
        s["subCategory"] = "光刻胶单体"
        changes_log.append(f"联合化学: 补category=半导体上游, subCategory=光刻胶单体")

# ═══════════════════════════════════════
# 2. 添加 reinforcements（来自7/30快讯）
# ═══════════════════════════════════════

# 2a. MLCC涨价：三星电机8/1起+30%，太阳诱电9/1起涨价
#   影响：风华高科、国瓷材料、洁美科技、博迁新材
mlcc_reinforcement = {
    "date": "2026-07-30",
    "desc": "三星电机宣布自8月1日起MLCC价格上调30%，所有出货产品执行新价格；日本太阳诱电通知自9月1日起MLCC涨价。日韩龙头加速消费级转AI高端，消费级中高容MLCC产能受挤压，订单外溢至国产厂商",
    "source": "https://www.cls.cn/detail/2438573"
}

# 风华高科(id=20 after merge)
for s in stocks:
    if s.get("code") == "000636":
        # 检查是否已有同日期条目
        existing_dates = [r.get("date") for r in s.get("conceptReinforcements", [])]
        if "2026-07-30" not in existing_dates:
            if "conceptReinforcements" not in s:
                s["conceptReinforcements"] = []
            s["conceptReinforcements"].append(mlcc_reinforcement)
            changes_log.append(f"风华高科: 追加7/30三星MLCC涨价30%reinforcement")
    
    # 国瓷材料(id=15) - 追加MLCC涨价reinforcement
    if s.get("code") == "300285":
        existing_dates = [r.get("date") for r in s.get("conceptReinforcements", [])]
        if "2026-07-30" not in existing_dates:
            s["conceptReinforcements"].append(mlcc_reinforcement)
            changes_log.append(f"国瓷材料: 追加7/30三星MLCC涨价30%reinforcement")
    
    # 洁美科技(id=22)
    if s.get("code") == "002859":
        existing_dates = [r.get("date") for r in s.get("conceptReinforcements", [])]
        if "2026-07-30" not in existing_dates:
            s["conceptReinforcements"].append(mlcc_reinforcement)
            changes_log.append(f"洁美科技: 追加7/30三星MLCC涨价30%reinforcement")

# 2b. 中钨高新 - 中金研报
for s in stocks:
    if s.get("code") == "000657":
        existing_dates = [r.get("date") for r in s.get("conceptReinforcements", [])]
        if "2026-07-30" not in existing_dates:
            if "conceptReinforcements" not in s:
                s["conceptReinforcements"] = []
            s["conceptReinforcements"].append({
                "date": "2026-07-30",
                "desc": "中金公司研报：中国钨业龙头有望迎来量价齐升；国内钨价7月下跌企稳后再现涨价迹象，海外溢价率创历史新高，当前估值已具较大吸引力",
                "source": "https://www.cls.cn/detail/2438573"
            })
            changes_log.append(f"中钨高新: 追加7/30中金研报reinforcement")

# 2c. 三孚股份 - 检查7/31复查备注
for s in stocks:
    if s.get("code") == "603938":  # 三孚股份
        if "riskNote" in s and "7/31复查" not in s["riskNote"]:
            # riskNote already has 7/30 and 7/31 notes, OK

# 2d. 功率半导体 - 熊本地震消息
for s in stocks:
    if s.get("code") == "300373":  # 扬杰科技
        existing_dates = [r.get("date") for r in s.get("conceptReinforcements", [])]
        if "2026-07-30" not in existing_dates:
            if "conceptReinforcements" not in s:
                s["conceptReinforcements"] = []
            s["conceptReinforcements"].append({
                "date": "2026-07-30",
                "desc": "熊本地震致多家半导体工厂停工检修，涉及的车规芯片/功率半导体短期交货节奏存在不确定性；功率半导体市场已处于涨价周期，地震可能进一步推升价格预期",
                "source": "https://www.cls.cn/detail/2438573"
            })
            changes_log.append(f"扬杰科技: 追加7/30熊本地震+功率涨价reinforcement")

# ═══════════════════════════════════════
# 3. 确保每个stock有category字段
# ═══════════════════════════════════════
category_defaults = {
    "000636": {"category": "被动元件", "subCategory": "MLCC全品类龙头"},
    "000657": {"category": "小金属(AI金属)", "subCategory": "钨"},
    "000960": {"category": "小金属(AI金属)", "subCategory": "锡"},
    "301209": {"category": "半导体上游", "subCategory": "光刻胶单体"}
}
for s in stocks:
    code = s.get("code", "")
    if "category" not in s or not s["category"]:
        if code in category_defaults:
            s["category"] = category_defaults[code]["category"]
            s["subCategory"] = category_defaults[code]["subCategory"]
            changes_log.append(f"{s['name']}({code}): 补category={s['category']}")

# ═══════════════════════════════════════
# 4. 限制reinforcements最多3条+重要事件归纳到coreLogic
# ═══════════════════════════════════════
for s in stocks:
    if "conceptReinforcements" in s and len(s["conceptReinforcements"]) > 3:
        # 排序：按日期升序
        s["conceptReinforcements"].sort(key=lambda x: x.get("date", ""))
        # 检查最旧的是否含重要事件
        oldest = s["conceptReinforcements"][0]
        important_keywords = ["涨价", "认证", "量产", "停产", "突破", "大单", "签约", "投产", "断供"]
        is_important = any(kw in oldest.get("desc", "") for kw in important_keywords)
        if is_important:
            # 归纳到coreLogic
            core = s.get("coreLogic", "")
            brief = oldest["desc"][:100]
            if brief not in core:
                s["coreLogic"] = core + f"\n【重要事件归纳】{oldest['date']}: {oldest['desc'][:150]}"
                changes_log.append(f"{s['name']}: 归纳reinforcement到coreLogic（{oldest['date']}）")
        # 移除最旧
        s["conceptReinforcements"].pop(0)

# ═══════════════════════════════════════
# 5. 按category+score降序重排序+刷新id
# ═══════════════════════════════════════
category_order = [
    "PCB产业链",
    "电子特气",
    "被动元件",
    "光互连",
    "半导体上游",
    "半导体设备零部件",
    "先进封装",
    "制造与存储",
    "功率半导体",
    "医疗材料",
    "小金属(AI金属)"
]

def sort_key(s):
    cat = s.get("category", "ZZZ")
    try:
        cat_idx = category_order.index(cat)
    except ValueError:
        cat_idx = 999
    score = -s.get("score", 0)  # 降序
    return (cat_idx, score, s.get("name", ""))

stocks.sort(key=sort_key)

# 刷新id（从1开始连续编号）
for i, s in enumerate(stocks, 1):
    s["id"] = i

# ═══════════════════════════════════════
# 6. 更新 stats
# ═══════════════════════════════════════
from collections import Counter

cat_counter = Counter()
market_counter = Counter()
for s in stocks:
    cat = s.get("category", "其他")
    cat_counter[cat] += 1
    market = s.get("market", "其他")
    market_counter[market] += 1

new_stats = {
    "categories": [{"name": k, "count": v} for k, v in sorted(cat_counter.items(), 
                   key=lambda x: -x[1])],
    "totalMarkets": dict(market_counter),
    "totalStocks": len(stocks)
}

data["stats"] = new_stats
data["meta"]["updated"] = today

# ═══════════════════════════════════════
# 7. 写回
# ═══════════════════════════════════════
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"看板已更新至 {today}")
print(f"总标的数: {len(stocks)}")
print(f"分类数: {len(cat_counter)}")
print("\n=== 变更日志 ===")
for log in changes_log:
    print(f"  ✓ {log}")

print("\n=== 赛道统计 ===")
for c in new_stats["categories"]:
    print(f"  {c['name']}: {c['count']}只")

#!/usr/bin/env python3
"""Apply Ming's hard logic scan report edits to hardlogic.json"""

import json
import copy
from datetime import datetime

JSON_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# ============================================================
# 辅助函数
# ============================================================

def has_keyword(desc, keywords):
    """Check if desc contains any of the keywords"""
    return any(kw in desc for kw in keywords)

IMPORTANT_KEYWORDS = ["涨价", "认证通过", "量产", "停产", "突破", "大单签约", "断供"]

def trim_reinforcements(stock, max_count=3):
    """Keep at most max_count newest reinforcements; merge important removed ones into coreLogic"""
    reifs = stock.get("conceptReinforcements", [])
    if len(reifs) <= max_count:
        return
    # Sort by date descending
    reifs_sorted = sorted(reifs, key=lambda r: r["date"], reverse=True)
    keep = reifs_sorted[:max_count]
    removed = reifs_sorted[max_count:]

    merged_descs = []
    for r in removed:
        if has_keyword(r["desc"], IMPORTANT_KEYWORDS):
            merged_descs.append(f'[{r["date"]}] {r["desc"]}')

    if merged_descs:
        suffix = "。" + "；".join(merged_descs)
        # Append to coreLogic, avoiding duplication
        if suffix not in stock.get("coreLogic", ""):
            stock["coreLogic"] = stock.get("coreLogic", "") + suffix

    stock["conceptReinforcements"] = keep

def add_reinforcement(stock, date, desc, source):
    """Add a reinforcement event; trim to 3 afterwards"""
    reifs = stock.get("conceptReinforcements", [])
    # Avoid exact duplicates
    for r in reifs:
        if r["date"] == date and r["desc"][:30] == desc[:30]:
            return  # already exists
    reifs.append({"date": date, "desc": desc, "source": source})
    stock["conceptReinforcements"] = reifs
    trim_reinforcements(stock)

def find_stock(code):
    """Find stock by code"""
    for s in data["stocks"]:
        if s["code"] == code:
            return s
    return None

# ============================================================
# Step 4: 新增标的 - 中船特气 (688146)
# ============================================================

zhongchuan = {
    "category": "电子特气",
    "subCategory": "六氟化钨(WF6)",
    "code": "688146",
    "name": "中船特气",
    "market": "科创板",
    "coreLogic": (
        "全球最大六氟化钨(WF6)产能2000吨/年，在建1000吨/年（2027年投产）。"
        "日本关东电化(KDK，产能约1400吨/年)与中央硝子(产能约700吨/年)因高纯钨粉原料断供，"
        "自2026年7月起永久停产六氟化钨，合计退出全球有效供给近30%(约2100吨/年)。"
        "公司长期稳定供应台积电/美光/SK海力士/中芯国际。六氟化钨价格同比涨232.7%"
        "（523→1750元/kg）。2026H1公司六氟化钨营收同比增长近3倍，总营收+83%，"
        "归母净利润+95.63%。"
    ),
    "supplyDemand": (
        "日本KDK+中央硝子合计退出约2100吨/年产能，占全球有效供给近30%。"
        "国内6N级六氟化钨价格：1670-1810元/kg（2026年6月），较2025年同期523元/kg +232.7%。"
        "中船特气现有产能2000吨/年，在建1000吨/年（2027年投产）。"
        "日本两家公司4月初已发函预警，原料库存仅支撑至5-6月，7月正式停产。"
    ),
    "priceSignal": (
        "六氟化钨价格同比涨232.7%（523→1750元/kg）；"
        "2026H1六氟化钨营收同比增近3倍；总营收+83%归母净利润+95.63%"
    ),
    "catalyst": (
        "日本KDK+中央硝子7月永久停产六氟化钨；"
        "全球供给缺口30%短期无替代产能；"
        "AI/存储芯片需求持续增长拉动六氟化钨用量；"
        "在建1000吨产能2027年投产"
    ),
    "conceptAdded": "2026-06-15",
    "conceptSource": "日本KDK+中央硝子永久停产六氟化钨→全球供给缺口30%→中船特气全球最大产能2000吨/年",
    "conceptSourceUrl": "https://www.cnfin.com/yw-lb/detail/20260615/4426975_1.html",
    "riskNote": (
        "⚠️ 股价从低点涨865%后回调48%，市场情绪过热曾遭监管停牌核查；"
        "2026H1经营现金流-2.41亿（上年+3.3亿），应收账款/存货均翻倍；"
        "「以钼代钨」技术路线（SK海力士375层3D NAND试验）的潜在替代风险；"
        "整体毛利率仅从30.35%升至31.79%（原材料涨价对冲了部分涨价红利）"
    ),
    "tags": ["全球最大产能", "海外永久停产", "供给硬约束", "价格暴涨232%", "AI存储链"],
    "conceptReinforcements": [
        {
            "date": "2026-07-23",
            "desc": (
                "中船特气半年报披露：六氟化钨营收同比暴涨近3倍；"
                "总营收+83%归母净利润+95.63%；日本KDK+中央硝子7月永久停产确认全球供给缺口30%"
            ),
            "source": "https://finance.sina.com.cn/stock/2026-07-23/doc-inihmvtq3581298.shtml"
        }
    ],
    "score": 8.5
}

# Check if already exists
if find_stock("688146") is None:
    data["stocks"].append(zhongchuan)
    print("✅ 新增: 中船特气 (688146) 六氟化钨, score=8.5")
else:
    print("⚠️ 中船特气 (688146) 已存在，跳过新增")

# ============================================================
# Step 5: 修正 conceptAdded（如有需要）
# 深南电路 - Ming标注"建议核查"但无具体替换日期，维持原样
# 圣泉/博云/洁美 - Ming确认 ✓
# ============================================================

# ============================================================
# Step 3: 博云新材 - 维持7.5但逻辑已弱化，Mark在riskNote已覆盖
# ============================================================
boyun = find_stock("002297")
if boyun:
    # riskNote already has the clarification; just ensure score stays at 7.5
    boyun["score"] = 7.5
    print("✅ 博云新材 (002297): 维持7.5分, riskNote已覆盖澄清公告")

# ============================================================
# Step 5.1: 圣泉集团 8.0 → 8.5
# ============================================================
shengquan = find_stock("605589")
if shengquan:
    shengquan["score"] = 8.5
    # Add SABIC 120+ days no recovery reinforcement
    add_reinforcement(shengquan,
        "2026-07-24",
        "SABIC朱拜勒工厂停产进入第120+天仍无复产迹象；全球PPE树脂替代需求加速向圣泉转移；2000吨新产能Q4投产在即；涨价15-20%确认执行满11天下游接受度良好",
        "https://news.chemnet.com/toutiao/detail-72779.html"
    )
    print("✅ 圣泉集团 (605589): 8.0→8.5, 新增SABIC停产120天强化事件")

# ============================================================
# Step 5.2: 顺络电子 8.5 → 9.0
# ============================================================
shunluo = find_stock("002138")
if shunluo:
    shunluo["score"] = 9.0
    add_reinforcement(shunluo,
        "2026-07-15",
        "日系电感7月第二轮涨价正式执行：村田/太阳诱电电感再涨25-35%高端料号涨超70%；TLVR电感涨70%+；日系涨价必然带动国内跟涨AI项目制新项目价格更好；稀土出口管制使日系电感厂商原材料持续吃紧",
        "https://m.36kr.com/p/3845611027728640"
    )
    print("✅ 顺络电子 (002138): 8.5→9.0, 新增7月第二轮涨价强化事件")

# ============================================================
# Step 6: 有新催化的现有标的 - 添加强化事件
# ============================================================

# 深南电路 - 高端PCB涨超300%央视财经
shennan = find_stock("002916")
if shennan:
    add_reinforcement(shennan,
        "2026-07-23",
        "央视财经报道高端PCB价格涨超300%头部厂商订单排到2027年；建滔第6轮涨价+15%确认PCB全产业链景气；ABF载板缺口高盛报告大修至2028年51%",
        "https://www.cls.cn/detail/2428607"
    )
    print("✅ 深南电路 (002916): 新增央视财经7/23强化事件")

# 鼎泰高科 - 日系钻针涨价300%+Kyber延期
dingtai = find_stock("301377")
if dingtai:
    add_reinforcement(dingtai,
        "2026-07-23",
        "日系钻针涨价最高300%确认；英伟达Kyber NVL144因78层正交背板PCB良率不足延期至2028年；PCB层数提升→钻针消耗量非线性暴增逻辑进一步强化",
        "https://36kr.com/p/3886635992314120"
    )
    print("✅ 鼎泰高科 (301377): 新增7/23强化事件")

# ============================================================
# Step 7: 对所有标的修剪 conceptReinforcements 到最多3条
# ============================================================
trim_count = 0
for stock in data["stocks"]:
    reifs = stock.get("conceptReinforcements", [])
    if len(reifs) > 3:
        before = len(reifs)
        trim_reinforcements(stock, 3)
        after = len(stock.get("conceptReinforcements", []))
        if before != after:
            trim_count += 1
            print(f"  ✂ {stock['name']}({stock['code']}): {before}→{after}条强化事件, 重要事件已归入coreLogic")

if trim_count == 0:
    print("✅ 无需修剪强化事件（均≤3条）")

# ============================================================
# Step 8: 回顾已有 score 是否仍合理
# 已处理的变更在上面。其余标的维持现分不变。
# ============================================================

# ============================================================
# Step 9: 按评分降序在每个 category 内重排标的，刷新 id
# ============================================================

# Group by category
from collections import OrderedDict
categories_order = [
    "PCB产业链", "电子特气", "被动元件", "光互连",
    "半导体上游", "半导体设备零部件", "先进封装",
    "制造与存储", "功率半导体", "医疗材料", "小金属(AI金属)"
]

cat_stocks = {}
for s in data["stocks"]:
    cat = s["category"]
    if cat not in cat_stocks:
        cat_stocks[cat] = []
    cat_stocks[cat].append(s)

new_stocks = []
new_id = 1
for cat in categories_order:
    if cat not in cat_stocks:
        continue
    # Sort by score descending, then by code for tie-breaking
    sorted_list = sorted(cat_stocks[cat], key=lambda s: (-s["score"], s["code"]))
    for s in sorted_list:
        s["id"] = new_id
        new_id += 1
        new_stocks.append(s)

# Add any categories not in the predefined order
for cat, stocks in cat_stocks.items():
    if cat not in categories_order:
        sorted_list = sorted(stocks, key=lambda s: (-s["score"], s["code"]))
        for s in sorted_list:
            s["id"] = new_id
            new_id += 1
            new_stocks.append(s)

data["stocks"] = new_stocks

# ============================================================
# Step 9 (cont): 更新 stats
# ============================================================

stats_categories = []
for cat in categories_order:
    count = sum(1 for s in new_stocks if s["category"] == cat)
    if count > 0:
        stats_categories.append({"name": cat, "count": count})

# Also catch any leftover categories
seen_cats = set(c["name"] for c in stats_categories)
for s in new_stocks:
    if s["category"] not in seen_cats:
        seen_cats.add(s["category"])
        count = sum(1 for x in new_stocks if x["category"] == s["category"])
        stats_categories.append({"name": s["category"], "count": count})

market_counts = {}
for s in new_stocks:
    m = s["market"]
    market_counts[m] = market_counts.get(m, 0) + 1

data["stats"] = {
    "categories": stats_categories,
    "totalMarkets": market_counts,
    "totalStocks": len(new_stocks)
}

# ============================================================
# Step 10: 更新 meta.updated
# ============================================================
data["meta"]["updated"] = "2026-07-24"

# ============================================================
# 写回
# ============================================================
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"✅ hardlogic.json 更新完成")
print(f"   总标的: {len(new_stocks)}")
print(f"   meta.updated: 2026-07-24")
print(f"   评分变动: 圣泉8.0→8.5, 顺络8.5→9.0, 中船特气新增8.5")
print(f"   类别统计: {', '.join(f'{c[\"name\"]}({c[\"count\"]})' for c in stats_categories)}")
print(f"{'='*60}")

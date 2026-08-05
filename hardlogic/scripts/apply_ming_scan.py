#!/usr/bin/env python3
"""
Apply Ming's 硬逻辑扫描报告 edits to hardlogic.json.
Run this first, then run generate_dashboard.py.
"""
import json
import os
from datetime import datetime, timedelta
from copy import deepcopy

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "hardlogic.json")

# --------------- helpers ---------------

def load():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def sort_key(stock):
    """Sort by score descending."""
    return -float(stock.get("score", 0))

def trim_reinforcements(stock, max_keep=3):
    """
    Keep at most max_keep newest reinforcements.
    Important events from dropped ones are summarized into coreLogic.
    """
    reif = stock.get("conceptReinforcements", [])
    if len(reif) <= max_keep:
        return

    # Sort by date desc
    reif.sort(key=lambda x: x.get("date", "1970-01-01"), reverse=True)

    kept = reif[:max_keep]
    dropped = reif[max_keep:]

    # Extract important keywords from dropped
    important_keywords = ["涨价", "认证通过", "量产", "停产", "突破", "大单签约", "断供", "禁令", "出口管制"]
    summaries = []
    for r in dropped:
        desc = r.get("desc", "")
        if any(kw in desc for kw in important_keywords):
            # Extract a short summary
            short = desc.split("；")[0] if "；" in desc else desc[:80]
            summaries.append(short)

    if summaries:
        # Append to coreLogic
        old_logic = stock.get("coreLogic", "")
        stock["coreLogic"] = old_logic.rstrip("。") + "。" + "。".join(summaries) + "。"

    stock["conceptReinforcements"] = kept

def add_reinforcement(stock, date, desc, source=""):
    """Add a reinforcement event. Dedup on same date+similar desc."""
    reif = stock.setdefault("conceptReinforcements", [])
    # Check for duplicate (same date and desc prefix overlap)
    desc_prefix = desc[:30]
    for existing in reif:
        if existing.get("date") == date and existing.get("desc", "")[:30] == desc_prefix:
            return  # Already exists
    entry = {"date": date, "desc": desc}
    if source:
        entry["source"] = source
    reif.append(entry)

# --------------- main logic ---------------

def main():
    data = load()
    stocks = data["stocks"]
    today = "2026-07-27"

    # ===== 1. Update meta =====
    data["meta"]["updated"] = today

    # ===== 2. Score adjustments =====
    for s in stocks:
        code = s.get("code", "")

        # 金宏气体 688106: 7.5 → 8.0 + add helium ban reinforcement
        if code == "688106":
            old_score = s.get("score", 0)
            s["score"] = 8.0
            add_reinforcement(s, "2026-07-10",
                "商务部+海关总署公告第29号：对氦气实施临时禁止出口管理（7月10日起执行）；"
                "中国氦气对外依存度84%，卡达海运因霍尔木兹海峡冲突切断+俄2027年底出口管制；"
                "国内氦气缺口60%+，利好金宏气体氦气回收/分装业务国产替代窗口",
                "https://wms.mofcom.gov.cn/zcfb/wmgl/art/2026/art_2a795a0d55df4cada91c9fbd2a2cc13a.html")
            # Also add to riskNote the caveat about verifying helium business proportion
            old_risk = s.get("riskNote", "")
            if "氦气" not in old_risk:
                s["riskNote"] = old_risk + "；⚠️ 新增氦气禁令逻辑：7/10商务部禁止氦气出口以堵住转口通道，国内氦气缺口60%+利好氦气回收业务，但需核查公司氦气业务实际营收占比及弹性"

        # 东方锆业 002167: set score 8.5
        if code == "002167":
            s["score"] = 8.5

        # 斯达半导 603290: set score 7.5
        if code == "603290":
            s["score"] = 7.5

    # ===== 3. New reinforcements for existing stocks =====

    # 深南电路: add 7/26 ABF缺口报道
    for s in stocks:
        if s.get("code") == "002916":
            add_reinforcement(s, "2026-07-26",
                "台媒FTNN报道ABF载板缺口2028年或达29%（多家国际大厂排队锁定产能至2029年）；"
                "法人大幅上调欣兴/南电目标价；ABF载板缺口持续超预期上修叠加高端PCB涨超300%",
                "https://money.udn.com/money/story/5607/9624978")

    # 生益科技: add 7/15 证券时报H1业绩报道
    for s in stocks:
        if s.get("code") == "600183":
            add_reinforcement(s, "2026-07-15",
                "证券时报报道：H1归母净利预增117-131%（31-33亿元）超预期；M7/M8/M9高端覆铜板量价齐升；"
                "建滔第6轮涨价向CCL传导顺畅，全年业绩有望再超市场一致预期",
                "https://m.21jingji.com/article/20260715/herald/4f1b8723a475f4c118f9d6820dc5b451.html")

    # 华正新材: add H1业绩+新reinforcement (7/24 + 7/13)
    for s in stocks:
        if s.get("code") == "603186":
            add_reinforcement(s, "2026-07-24",
                "H1归母净利预增263-380%业绩大爆发确认；CBF绝缘膜通过华为昇腾认证加速导入；"
                "味之素ABF膜Q3涨价30%扩大国产替代窗口；CCL+CBF膜双逻辑全面兑现",
                "https://news.chemnet.com/toutiao/detail-72779.html")

    # 中钨高新: conceptAdded stays 2026-07-17 (same as article publish date on stcn.com)
    # No change needed per verification — article was published 7/17.

    # ===== 4. Trim all reinforcements to max 3 =====
    for s in stocks:
        trim_reinforcements(s, max_keep=3)

    # ===== 5. Re-sort within each category by score desc, re-id =====
    # Group by category preserving category order
    cat_order = []
    cat_stocks = {}
    for s in stocks:
        cat = s.get("category", "")
        if cat not in cat_stocks:
            cat_stocks[cat] = []
            cat_order.append(cat)
        cat_stocks[cat].append(s)

    new_stocks = []
    new_id = 1
    for cat in cat_order:
        cat_stocks[cat].sort(key=sort_key)
        for s in cat_stocks[cat]:
            s["id"] = new_id
            new_id += 1
            new_stocks.append(s)

    data["stocks"] = new_stocks

    # ===== 6. Update stats =====
    cat_counts = {}
    market_counts = {}
    for s in new_stocks:
        cat = s.get("category", "")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        mkt = s.get("market", "")
        market_counts[mkt] = market_counts.get(mkt, 0) + 1

    data["stats"] = {
        "categories": [{"name": k, "count": v} for k, v in cat_counts.items()],
        "totalMarkets": market_counts,
        "totalStocks": len(new_stocks)
    }

    save(data)
    print(f"✅ Apply complete: {len(new_stocks)} stocks, updated to {today}")

    # Print summary of changes
    print("\n=== 变更摘要 ===")
    print("📊 评分调整:")
    print("  金宏气体 688106: 7.5 → 8.0 (+氦气禁令新逻辑)")
    print("  东方锆业 002167: 未评分 → 8.5")
    print("  斯达半导 603290: 未评分 → 7.5")
    print("\n📝 新增reinforcement:")
    print("  深南电路: 7/26 ABF载板缺口2028年或达29%")
    print("  生益科技: 7/15 证券时报H1净利预增117-131%")
    print("  华正新材: 7/24 H1净利预增263-380%")
    print("  金宏气体: 7/10 氦气出口禁令")
    print("\n🗑️ 移除标的: 无（本轮未发现需移除标的）")
    print("📅 conceptAdded修正: 无（中钨高新保持7/17与证券时报发表日期一致）")
    print(f"\n📂 输出: {JSON_PATH}")


if __name__ == "__main__":
    main()

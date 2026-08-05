"""
批量处理硬逻辑看板JSON：去重、裁剪、排序、刷新ID、更新统计。
"""
import json
import re
from datetime import datetime

JSON_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

# --- 新增强化事件（基于Ming的扫描报告） ---
NEW_REINFORCEMENTS = {
    "002916": [  # 深南电路
        # 7/16 already exists, just dedup
    ],
    "605589": [  # 圣泉集团
        {"date": "2026-07-13", "desc": "7月13日公司调研确认合成树脂板块稳健向好；SABIC CHINAPLAS 2026展会材料显示福建石化综合体2H26投产，未提及朱拜勒PPE复产任何迹象；SABIC停产进入第110+天全球替代加速", "source": "https://news.chemnet.com/toutiao/detail-72779.html"},
    ],
    "300285": [  # 国瓷材料
        {"date": "2026-07-03", "desc": "OFweek深度分析：氧化钇对日出口2026年以来连续6个月归零；氧化镝对日出口2025年以来各月归零(持续至少18个月)；氧化钇内外价差超160倍；东曹氧化锆粉体断供已满5周预计无法恢复；日系MLCC全链条原料承压系统性确认", "source": "https://ee.ofweek.com/2026-07/ART-8420-2816-30693192.html"},
    ],
    "000636": [  # 风华高科
        {"date": "2026-07-03", "desc": "OFweek深度分析确认氧化镝对日出口归零18个月+氧化钇归零6个月；日系MLCC全链条原料从理论断供变为物理层面系统性紧缺；国巨全系列电容涨价覆盖风华全品类共振", "source": "https://ee.ofweek.com/2026-07/ART-8420-2816-30693192.html"},
    ],
}

# --- 需要追加到coreLogic的重要事件关键词 ---
IMPORTANT_KEYWORDS = ["涨价", "认证", "量产", "停产", "突破", "大单签约", "断供", "归零", "缺口", "涨价执行"]

def dedup_reinforcements(reinfs):
    """去重：按date+desc前80字符"""
    seen = set()
    result = []
    for r in reinfs:
        key = (r["date"], r["desc"][:80])
        if key not in seen:
            seen.add(key)
            result.append(r)
    return result

def trim_and_induce(stock):
    """裁剪至3条，将重要事件归纳到coreLogic"""
    reinfs = stock.get("conceptReinforcements", [])
    if not reinfs:
        return
    
    # 去重
    reinfs = dedup_reinforcements(reinfs)
    
    # 按日期降序
    reinfs.sort(key=lambda x: x["date"], reverse=True)
    
    if len(reinfs) <= 3:
        stock["conceptReinforcements"] = reinfs
        return
    
    # 保留最新3条，其余检查是否重要
    keep = reinfs[:3]
    removed = reinfs[3:]
    
    induced = []
    for r in removed:
        desc = r.get("desc", "")
        if any(kw in desc for kw in IMPORTANT_KEYWORDS):
            # 提取重要事件摘要（取前100字符）
            short = desc[:120].rstrip("；。，,") 
            induced.append(short)
    
    if induced:
        current_core = stock.get("coreLogic", "")
        # 追加到coreLogic末尾
        appendix = "；" + "；".join(induced)
        if not current_core.endswith("。"):
            stock["coreLogic"] = current_core + appendix
        else:
            stock["coreLogic"] = current_core.rstrip("。") + appendix
    
    stock["conceptReinforcements"] = keep

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    stocks = data["stocks"]
    
    # 1. 为每个标的添加新的强化事件
    for stock in stocks:
        code = stock.get("code", "")
        if code in NEW_REINFORCEMENTS:
            existing = stock.get("conceptReinforcements", [])
            for new_r in NEW_REINFORCEMENTS[code]:
                # 检查是否已存在
                exists = any(
                    r["date"] == new_r["date"] and r["desc"][:40] == new_r["desc"][:40]
                    for r in existing
                )
                if not exists:
                    existing.append(new_r)
            stock["conceptReinforcements"] = existing
    
    # 2. 去重、裁剪、归纳
    for stock in stocks:
        trim_and_induce(stock)
    
    # 3. 按category分组，组内按score降序
    category_order = {}  # 保持原有顺序
    categorized = {}
    for stock in stocks:
        cat = stock.get("category", "其他")
        if cat not in category_order:
            category_order[cat] = len(category_order)
        categorized.setdefault(cat, []).append(stock)
    
    # 组内按score降序
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # 按category出现顺序重组
    new_stocks = []
    for cat in sorted(category_order, key=category_order.get):
        new_stocks.extend(categorized[cat])
    
    # 4. 刷新id
    for i, stock in enumerate(new_stocks, 1):
        stock["id"] = i
    
    data["stocks"] = new_stocks
    
    # 5. 更新stats
    cat_counts = {}
    market_counts = {}
    for stock in new_stocks:
        cat = stock.get("category", "其他")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        mkt = stock.get("market", "其他")
        market_counts[mkt] = market_counts.get(mkt, 0) + 1
    
    data["stats"]["categories"] = [
        {"name": cat, "count": count}
        for cat, count in cat_counts.items()
    ]
    data["stats"]["totalMarkets"] = market_counts
    data["stats"]["totalStocks"] = len(new_stocks)
    
    # 6. 更新meta.updated
    data["meta"]["updated"] = "2026-07-18"
    
    # 6. 写回
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"处理完成！总标数: {len(new_stocks)}")
    print("各分类统计:")
    for cat, count in cat_counts.items():
        print(f"  {cat}: {count}")
    print(f"市场分布: {market_counts}")
    
    # 打印排序后前5
    print("\n=== TOP 5 by Score ===")
    sorted_all = sorted(new_stocks, key=lambda x: x.get("score", 0), reverse=True)
    for s in sorted_all[:5]:
        print(f"  {s['id']}. {s['name']}({s['code']}) - {s['score']}分 [{s['category']}]")

if __name__ == "__main__":
    main()

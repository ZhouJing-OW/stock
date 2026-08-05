#!/usr/bin/env python3
"""
HardLogic TOP20 数据更新脚本 — 2026-06-23
读取 top20_hardlogic.json，应用评分调整/增强事件/风险更新/分类内重排，写回。
"""
import json
import copy
from collections import OrderedDict

DATA_PATH = r"E:\Hanako_WorkSpace\hardlogic_top20\data\top20_hardlogic.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f, object_pairs_hook=OrderedDict)

stocks = data["stocks"]

# 建立 name → index 的查找
name_to_idx = {}
for i, s in enumerate(stocks):
    name_to_idx[s["name"]] = i

# ──────────────────────────────────────────────
# 1. 评分调整
# ──────────────────────────────────────────────
score_changes = {
    "中船特气":   (9.5, 9.0, "停牌核查使交易层面风险显著上升，个股受益强度降分"),
    "风华高科":   (9.0, 9.5, "MLCC超级周期获外资确认（Super Cycle），AI服务器单机MLCC 44万颗×10-15倍传统"),
    "国瓷材料":   (9.0, 9.5, "MLCC超级周期向上游粉体传导，稀土管制使日系粉体供给进一步承压"),
    "三环集团":   (7.5, 8.0, "MLCC超级周期确认+Q3涨价落地确定性增强"),
    "顺络电子":   (7.5, 8.0, "日系龙头7月第二轮电感提价进入倒计时，AI服务器专用电感部分型号涨超110%"),
    "三孚股份":   (7.5, 7.0, "美伊停火协议生效霍尔木兹海峡逐步疏通，硫磺价格回落使硫酸逻辑弱化"),
}

for name, (old, new, reason) in score_changes.items():
    if name in name_to_idx:
        s = stocks[name_to_idx[name]]
        if abs(s.get("score", 0) - old) < 0.01:
            s["score"] = new
            print(f"  ✓ {name}: {old}→{new}  — {reason}")
        else:
            print(f"  ⚠ {name}: 期望旧分 {old}，实际 {s.get('score')}，跳过")
    else:
        print(f"  ✗ {name}: 未找到")

# ──────────────────────────────────────────────
# 2. 追加 conceptReinforcements
# ──────────────────────────────────────────────
reinforcements = {
    "风华高科": [
        {
            "date": "2026-06-23",
            "desc": "外资正式定调MLCC进入'超级周期(Super Cycle)'，AI服务器单机柜MLCC用量44万颗(传统10-15倍)；华强北现货一天一价部分型号翻3-5倍；外资喊国巨目标价1515元，产业景气至少延续至2028年",
            "source": "https://finance.technews.tw/2026/06/23/mlcc-supercycle/"
        }
    ],
    "国瓷材料": [
        {
            "date": "2026-06-23",
            "desc": "MLCC超级周期向上游粉体传导；氧化镝涨至141.5万/吨历史新高，日系MLCC全链条原料承压；外资确认MLCC供需缺口将延续至2028年",
            "source": "https://finance.technews.tw/2026/06/23/mlcc-supercycle/"
        }
    ],
    "三环集团": [
        {
            "date": "2026-06-23",
            "desc": "外资确认MLCC超级周期；村田计划7月第三轮涨价10-40%+三星跟涨；现货市场高端型号一天一价部分涨10倍；Q3涨价落地确定性大幅增强",
            "source": "https://36kr.com/p/3865500975715335"
        }
    ],
    "顺络电子": [
        {
            "date": "2026-06-23",
            "desc": "日系龙头7月第二轮电感提价进入倒计时；AI服务器VPD供电架构全面推广，TLVR电感需求爆发单颗价值量翻倍；日系涨价必然带动国内跟涨",
            "source": "https://m.36kr.com/p/3845611027728640"
        }
    ],
    "深南电路": [
        {
            "date": "2026-06-22",
            "desc": "ABF载板Q2现货价环比涨30-40%；建滔积层板第五次涨价+15%(累计超50%)；ABF膜味之素扩产要2032年投产，供给硬约束至少6年",
            "source": "https://www.chinairn.com/hyzx/20260617/175427297.shtml"
        }
    ],
    "东方锆业": [
        {
            "date": "2026-06-23",
            "desc": "6月22日再次涨停实现三连板；氧化锆板块全线爆发；东曹断供+涨价40%逻辑持续兑现；齿科+固态电池+MLCC+核电四重下游需求共振",
            "source": "https://36kr.com/p/3865022505686020"
        }
    ],
    "中微公司": [
        {
            "date": "2026-06-23",
            "desc": "美股7家半导体设备公司年内翻倍(AMAT创$567/LRCX创$410/KLAC全创新高)；花旗上调全球WFE预测：2026年$1450亿→2027年$2000亿→2028年$2500亿；AI算力投资向上游设备全面扩散",
            "source": "https://www.kalkine.com/news/general-news/applied-materials-amat-stock-surges-to-all-time-high-of-56725-ai-chip-buildout-fuels-equipment-supercycle"
        }
    ],
    "北方华创": [
        {
            "date": "2026-06-23",
            "desc": "美股7家半导体设备公司年内翻倍全创新高；花旗上调全球WFE预测2027年$2000亿2028年$2500亿；SK海力士规划5年晶圆产能翻倍2034年三倍，设备订单持续放量",
            "source": "https://www.kalkine.com/news/general-news/applied-materials-amat-stock-surges-to-all-time-high-of-56725-ai-chip-buildout-fuels-equipment-supercycle"
        }
    ],
    "联瑞新材": [
        {
            "date": "2026-06-23",
            "desc": "伯恩斯坦6月22日研报：2027年HBM合约价必涨2-2.5倍（因HBM晶圆利润仅为普通DRAM的1/3）；TrendForce确认HBM产能缺口持续至2028年；HBM封装填料需求指数级增长",
            "source": "https://www.mexc.co/zh-MY/news/1164564"
        }
    ],
    "江丰电子": [
        {
            "date": "2026-06-23",
            "desc": "全球半导体设备Q1出货365.5亿美元创纪录；靶材作为核心耗材需求同步爆发；国产化率不足20%替代空间巨大",
            "source": "https://www.21jingji.com/article/20260620/herald/7c929615032e5e22af2a541faa3564eb.html"
        }
    ],
    "沪硅产业": [
        {
            "date": "2026-06-23",
            "desc": "全球半导体设备超级周期向上游材料传导；12英寸硅片缺口73万片/月格局不变；信越/SUMCO/环球晶圆涨价5-22%确认供需紧张",
            "source": "https://news.qq.com/rain/a/20260611A076VZ00"
        }
    ],
}

for name, items in reinforcements.items():
    if name in name_to_idx:
        s = stocks[name_to_idx[name]]
        if "conceptReinforcements" not in s:
            s["conceptReinforcements"] = []
        existing_dates = {r["date"] for r in s["conceptReinforcements"]}
        added = 0
        for item in items:
            if item["date"] not in existing_dates:
                s["conceptReinforcements"].append(item)
                existing_dates.add(item["date"])
                added += 1
        if added:
            print(f"  ✓ {name}: +{added}条增强事件")
    else:
        print(f"  ✗ {name}: 未找到")

# ──────────────────────────────────────────────
# 3. 风险提示更新
# ──────────────────────────────────────────────
risk_updates = {
    "三孚股份": "美伊停火协议6月15日签署，霍尔木兹海峡逐步疏通（30天内排雷+1-2周观察），硫磺价格已从11000+元回落至9500-10000元/吨，SMM预计8月回落至5500-6500元/吨。电子级硫酸逻辑明显弱化。三氯氢硅/TMA逻辑仍存但权重下降",
    "雅克科技": "美伊停火协议生效霍尔木兹海峡逐步疏通，硫磺价格回落将拖累硫酸/氢氟酸价格。前驱体/SOD/光刻胶/LNG板材逻辑仍坚实，但氢氟酸催化剂弱化",
    "中船特气": "6月23日起停牌核查，52交易日涨813%触发严重异常波动；股价已定价大量未来预期，估值透支风险显著；钨粉原材料涨价压缩利润；SK海力士375层NAND在字线环节用钼替代钨(局部替代)；公司多次公告澄清未签署实质性大额长单。逻辑极致硬但交易风险极高",
}

for name, new_risk in risk_updates.items():
    if name in name_to_idx:
        s = stocks[name_to_idx[name]]
        s["riskNote"] = new_risk
        print(f"  ✓ {name}: 风险提示已更新")
    else:
        print(f"  ✗ {name}: 未找到")

# ──────────────────────────────────────────────
# 4. 三孚股份/雅克科技 catalyst 微调
# ──────────────────────────────────────────────
if "三孚股份" in name_to_idx:
    s = stocks[name_to_idx["三孚股份"]]
    s["catalyst"] = "电子级三氯氢硅/TMA领先地位；电子级二氯二氢硅国产替代；TMA海外产能退出（英力士停产）"
    print(f"  ✓ 三孚股份: catalyst 已更新（移除硫酸催化）")

if "雅克科技" in name_to_idx:
    s = stocks[name_to_idx["雅克科技"]]
    s["catalyst"] = "前驱体/SOD国产替代龙头；光刻胶进口替代；LNG板材订单饱满；HBM先进封装材料布局"
    print(f"  ✓ 雅克科技: catalyst 已更新（移除氢氟酸催化）")

# ──────────────────────────────────────────────
# 5. 按 category 分组，组内按 score 降序重排
# ──────────────────────────────────────────────
category_order = [
    "电子特气",
    "PCB产业链",
    "制造与存储",
    "被动元件",
    "半导体上游",
    "医疗材料",
    "先进封装",
]

# 分组
groups = OrderedDict()
for cat in category_order:
    groups[cat] = []

for s in stocks:
    cat = s.get("category", "")
    if cat in groups:
        groups[cat].append(s)
    else:
        # 未分类的放到最后
        if "其他" not in groups:
            groups["其他"] = []
        groups["其他"].append(s)

# 组内按 score 降序（同分按原 id 升序稳定排序）
for cat in groups:
    groups[cat].sort(key=lambda x: (-x.get("score", 0), x.get("id", 999)))

# 重新分配 id
new_stocks = []
new_id = 1
reid_map = {}  # old_id → new_id
for cat in category_order + (["其他"] if "其他" in groups else []):
    for s in groups[cat]:
        old_id = s["id"]
        s["id"] = new_id
        reid_map[old_id] = new_id
        new_stocks.append(s)
        new_id += 1

data["stocks"] = new_stocks
print(f"\n  重排完成: {len(new_stocks)}只标的，ID已刷新")

# ──────────────────────────────────────────────
# 6. 更新 stats
# ──────────────────────────────────────────────
cat_counts = OrderedDict()
market_counts = OrderedDict()
for s in new_stocks:
    cat = s["category"]
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
    mkt = s["market"]
    market_counts[mkt] = market_counts.get(mkt, 0) + 1

data["stats"]["categories"] = [{"name": k, "count": v} for k, v in cat_counts.items()]
data["stats"]["totalMarkets"] = dict(market_counts)

# 计算 avgConceptAgeDays 和 recentConcepts14d
from datetime import date, timedelta
today = date(2026, 6, 23)
ages = []
recent = 0
for s in new_stocks:
    added_str = s.get("conceptAdded", "")
    if added_str:
        try:
            added_date = date.fromisoformat(added_str)
            age = (today - added_date).days
            ages.append(age)
            if age <= 14:
                recent += 1
        except:
            pass
data["stats"]["avgConceptAgeDays"] = round(sum(ages) / len(ages)) if ages else 0
data["stats"]["recentConcepts14d"] = recent

print(f"  分类统计: {dict(cat_counts)}")
print(f"  市场统计: {dict(market_counts)}")
print(f"  平均概念年龄: {data['stats']['avgConceptAgeDays']}天")
print(f"  近14天新增: {data['stats']['recentConcepts14d']}只")

# ──────────────────────────────────────────────
# 7. 更新 meta
# ──────────────────────────────────────────────
data["meta"]["updated"] = "2026-06-23"
print(f"  meta.updated → 2026-06-23")

# ──────────────────────────────────────────────
# 8. 写回
# ──────────────────────────────────────────────
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 已写入 {DATA_PATH}")

# ──────────────────────────────────────────────
# 9. 打印变更摘要
# ──────────────────────────────────────────────
print("\n" + "="*60)
print("变更摘要")
print("="*60)

print("\n【评分变动】")
for name, (old, new, reason) in score_changes.items():
    arrow = "↑" if new > old else "↓"
    print(f"  {arrow} {name}: {old} → {new}  ({reason[:40]}...)")

print("\n【风险更新】")
for name in risk_updates:
    print(f"  ⚡ {name}: 风险提示已重写")

print("\n【增强事件】")
for name, items in reinforcements.items():
    print(f"  + {name}: {len(items)}条 ({items[-1]['date']})")

print("\n【新ID映射(部分)】")
for old, new in list(reid_map.items())[:10]:
    old_name = next((s["name"] for s in stocks if s.get("id") == old), "?")
    print(f"  #{old}→#{new}: {old_name}")
print(f"  ... 共{len(reid_map)}只重排")

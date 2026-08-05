#!/usr/bin/env python3
"""
硬逻辑看板更新脚本 - 2026-07-09
新增: 博云新材(纳米晶钨棒)
强化事件: 英伟达Kyber延期 + 三星Q2暴增 + Nor Flash涨价
"""
import json
import copy
from datetime import datetime

DATA_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

today = "2026-07-09"

# ============================================================
# 1. 新增标的: 博云新材 - 纳米晶碳化钨棒材
# ============================================================
new_stock_boyun = {
    "category": "PCB产业链",
    "subCategory": "纳米晶碳化钨棒材 (PCB钻针母材)",
    "code": "002297",
    "name": "博云新材",
    "market": "主板",
    "coreLogic": "子公司博云东方是国内唯一稳定量产≤0.17μm顶级纳米晶钨棒的企业，全球仅住友、山特维克、博云东方三家掌握该工艺。中国钨出口管制切断日系原料，住友电工7月1日全面停产(全球份额25%)、富士精工7月15日关停(15%)、三菱材料7月末停工(20%)，合计60%全球高端产能永久退出。博云东方产能从800→1200吨扩产，直接承接住友25%全球份额空缺。Q1营收+126%、净利+13362%。",
    "supplyDemand": "中国对日钨粉出口配额清零(2026年2-4月海关数据归零)，日本无钨矿资源，高纯纳米晶钨粉100%依赖中国进口。日系三大龙头合计占全球60%高端纳米晶钨棒产能，7月全面停产。海外仅瑞典山特维克剩余产能，但成本高30-50%。全球PCB微钻年消耗500亿支+，AI服务器PCB用超微钻消耗量是普通板5-8倍。",
    "priceSignal": "6月高端纳米晶钨棒单月涨幅超60%；Q1营收3.80亿(+125.94%)，净利1.32亿(+13362%)；鼎泰高科等头部客户已开始采购博云棒材",
    "catalyst": "日系三大龙头7月全面停产；中国钨出口管制长期化；AI服务器PCB微钻消耗量暴增；博云东方扩产至1200吨承接全球份额",
    "conceptAdded": today,
    "conceptSource": "中国钨出口管制→日系三大钨棒龙头全面停产→博云东方唯一国产纳米晶替代",
    "conceptSourceUrl": "https://finance.sina.com.cn/stock/wbstock/2026-07-01/doc-inifihnn0811608.shtml",
    "riskNote": "博云东方是子公司非母公司全部业务；航空航天/汽车业务有周期属性；瑞典山特维克可能扩产抢占份额；Q1暴增基数效应后续增速可能放缓",
    "tags": [
        "海外停产",
        "供给硬约束",
        "国产替代",
        "全球唯三",
        "AI钻针母材"
    ],
    "conceptReinforcements": [
        {
            "date": "2026-07-01",
            "desc": "住友电工7月1日PCB钻针钨棒全面停产正式执行，全球25%高端份额退出；富士精工7月15日关停、三菱材料7月末停工跟进；中国对日钨粉出口配额清零海关数据归零",
            "source": "https://finance.sina.com.cn/stock/wbstock/2026-07-01/doc-inifihnn0811608.shtml"
        }
    ],
    "score": 8.5
}

# Insert into stocks array (at end, will be sorted later by category)
data["stocks"].append(new_stock_boyun)

# ============================================================
# 2. 强化事件追加
# ============================================================
reinforcements_map = {
    # ---------- PCB产业链（英伟达Kyber延期验证高端PCB瓶颈）----------
    "603256": {  # 宏和科技
        "date": today,
        "desc": "英伟达Kyber NVL144因78层正交背板PCB良率不足延期至2028年(SemiAnalysis 7/6爆料)；正交背板需Q布(石英纤维布)+M9级CCL+78层PCB，电子布/Q布作为核心基材不可替代性被顶级算力系统验证",
        "source": "https://36kr.com/p/3886635992314120"
    },
    "002916": {  # 深南电路
        "date": today,
        "desc": "英伟达Kyber NVL144因78层正交背板PCB良率不足延期至2028年；高端PCB正式从'配套配角'升级为AI算力迭代'核心瓶颈'；国内头部PCB厂商技术壁垒价值重估",
        "source": "https://36kr.com/p/3886635992314120"
    },
    "600183": {  # 生益科技
        "date": today,
        "desc": "英伟达Kyber NVL144因78层正交背板需M9级CCL+Q布良率不足延期至2028年；高端CCL作为AI算力核心瓶颈被顶级产品验证，特种基材不可替代性进一步强化",
        "source": "https://36kr.com/p/3886635992314120"
    },
    "301377": {  # 鼎泰高科
        "date": today,
        "desc": "英伟达Kyber NVL144延期验证高端PCB瓶颈+日系钨棒全面停产双重催化：78层PCB微钻消耗量指数级增长+上游钨棒供给收缩→钻针量价齐升逻辑强化",
        "source": "https://36kr.com/p/3886635992314120"
    },
    "301217": {  # 铜冠铜箔
        "date": today,
        "desc": "英伟达Kyber NVL144因78层正交背板PCB延期→78层PCB对应HVLP4及以上铜箔需求刚性确认；高端铜箔作为AI算力核心导电材料不可替代性强化",
        "source": "https://36kr.com/p/3886635992314120"
    },
    "601208": {  # 东材科技
        "date": today,
        "desc": "英伟达Kyber NVL144 78层正交背板需PTFE+碳氢树脂等特种基材；高端电子树脂在极限PCB中的不可替代地位被顶级产品验证",
        "source": "https://36kr.com/p/3886635992314120"
    },
    # ---------- 被动元件 ----------
    "300726": {  # 宏达电子
        "date": today,
        "desc": "钽精矿维持257.5美元/磅高位第18天(年内涨222%)；刚果(金)鲁巴亚矿区矿难持续影响全球15%钽供应；基美/松下/国巨全品类钽电容涨价延续",
        "source": "https://qhweb.eastmoney.com/news/202606153771874648.html"
    },
    # ---------- 制造与存储 ----------
    "688008": {  # 澜起科技
        "date": today,
        "desc": "三星电子Q2营业利润89.4万亿韩元(+1810%)营收171万亿韩元(+129%)双创历史新高；AI存储需求从HBM向DDR5/NAND全线扩散；DDR5接口芯片需求确定性大幅强化",
        "source": "https://stock.jrj.com.cn/2026/07/07141657725829.shtml"
    },
    "603986": {  # 兆易创新
        "date": today,
        "desc": "三星Q2营业利润+1810%创新高+聚辰股份Nor Flash全线涨价25%7月6日生效；上半年Nor Flash/SLC NAND合约价涨幅突破100%；存储超级周期全面扩散至Nor Flash环节",
        "source": "https://stock.jrj.com.cn/2026/07/07141657725829.shtml"
    },
    "301308": {  # 江波龙
        "date": today,
        "desc": "江波龙上半年净利润92-110亿(+62204-74394%)；三星Q2营业利润+1810%创新高；存储超级周期全面验证企业级SSD受益AI数据中心扩容",
        "source": "https://www.nbd.com.cn/articles/2026-07-03/4298765.html"
    },
}

# ============================================================
# 3. 追加强化事件 & 只保留最近3条
# ============================================================
for stock in data["stocks"]:
    code = stock.get("code", "")
    if code in reinforcements_map:
        r = reinforcements_map[code]
        # Check for duplicates by date+desc similarity
        existing_dates = {e["date"] for e in stock.get("conceptReinforcements", [])}
        if r["date"] not in existing_dates:
            if "conceptReinforcements" not in stock:
                stock["conceptReinforcements"] = []
            stock["conceptReinforcements"].append(r)

    # Trim to last 3, but first fold important events into coreLogic
    reif = stock.get("conceptReinforcements", [])
    if len(reif) > 3:
        # Sort by date
        reif.sort(key=lambda x: x["date"])
        removed = reif[:-3]  # oldest ones to remove
        kept = reif[-3:]
        
        # Fold important removed events into coreLogic
        important_keywords = ["涨价", "认证通过", "量产", "停产", "突破", "断供", "归零", "管制"]
        folded_desc = []
        for evt in removed:
            desc = evt.get("desc", "")
            if any(kw in desc for kw in important_keywords):
                # Extract key sentence (take up to first period or 80 chars)
                short = desc.split("。")[0][:120]
                folded_desc.append(short)
        
        if folded_desc:
            # Append folded content after existing coreLogic
            existing = stock.get("coreLogic", "")
            fold_text = "。".join(folded_desc)
            # Avoid duplicate - check if already in coreLogic
            if fold_text[:40] not in existing:
                stock["coreLogic"] = existing + "。" + fold_text
        
        stock["conceptReinforcements"] = kept

# ============================================================
# 4. 更新meta
# ============================================================
data["meta"]["updated"] = today

# ============================================================
# 5. 按评分降序在每个分类内重排标的
# ============================================================
# Group by category
from collections import OrderedDict
cats = OrderedDict()
for s in data["stocks"]:
    c = s["category"]
    if c not in cats:
        cats[c] = []
    cats[c].append(s)

# Sort within each category by score desc
new_stocks = []
for cat, stocks in cats.items():
    stocks.sort(key=lambda x: x.get("score", 0), reverse=True)
    new_stocks.extend(stocks)

data["stocks"] = new_stocks

# Re-assign IDs
for i, s in enumerate(data["stocks"]):
    s["id"] = i + 1

# ============================================================
# 6. 更新stats
# ============================================================
cat_counts = {}
market_counts = {}
total_age = 0
recent_14d = 0
for s in data["stocks"]:
    cat = s["category"]
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    mkt = s["market"]
    market_counts[mkt] = market_counts.get(mkt, 0) + 1
    
    if "conceptAdded" in s:
        try:
            age = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(s["conceptAdded"], "%Y-%m-%d")).days
            total_age += age
            if age <= 14:
                recent_14d += 1
        except:
            pass

data["stats"] = {
    "categories": [{"name": k, "count": v} for k, v in cat_counts.items()],
    "totalMarkets": market_counts,
    "avgConceptAgeDays": round(total_age / len(data["stocks"]), 1) if data["stocks"] else 0,
    "recentConcepts14d": recent_14d
}

# ============================================================
# 7. 保存
# ============================================================
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 更新完成！共 {len(data['stocks'])} 只标的")
print(f"   meta.updated: {data['meta']['updated']}")
print(f"   categories: {[(c['name'], c['count']) for c in data['stats']['categories']]}")
print(f"   recent14d: {data['stats']['recentConcepts14d']}")
print(f"   avgConceptAgeDays: {data['stats']['avgConceptAgeDays']}")

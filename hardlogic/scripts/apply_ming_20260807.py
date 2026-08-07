# -*- coding: utf-8 -*-
"""
一次性迁移脚本：应用 Ming 硬逻辑扫描报告（2026-08-07 核验）的编辑决策。
执行后落盘 data/hardlogic.json，再运行 prepare_data.py 重新生成看板。

编辑决策清单：
1. 新增 4 张正式卡片：江波龙301308 / 中国巨石600176 / 华海清科688120 / 长川科技300604
   （纳思达、无人机反制链 经甄别不满足三重逻辑，排除）
   注：Ming 候选#1 长鑫科技(688825)已在板内(id 61)，不重复添加，其催化已由现有 reinforcements 覆盖。
2. 评分上调：佰维存储7.5→8.5、光力科技8.0→8.5、德龙激光7.3→8.0、宏和科技7.0→8.0、雅克科技6.5→7.0
3. 评分下调：鼎泰高科8.5→8.0、东方钽业9.0→8.5（riskNote 追加逻辑弱化说明）
4. conceptReinforcements 追加新催化（国瓷/洁美/深南/佰维/光力/德龙/宏和），
   超3条时删除最旧并将重要事件归纳进 coreLogic
5. 分类内按评分降序重排、刷新 id、更新 stats、meta.updated=2026-08-07
6. conceptAdded 存疑项（深南/donews、铜冠铜箔、中船特气、中钨高新、复旦微电/安路科技、锡业股份）：
   Ming 未给出可确认的原文日期，需人工核验原文，本次不做猜测性修改。
"""

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "hardlogic.json"
TODAY = "2026-08-07"

with open(DATA, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]
by_code = {s["code"]: s for s in stocks}

# ===================== 1. 评分调整 =====================
score_changes = {
    "688525": 8.5,   # 佰维存储：三大原厂2027产能售罄+HBF标准
    "300480": 8.5,   # 光力科技：日本8/1管制直接受益
    "688170": 8.0,   # 德龙激光：日本8/1管制直接受益
    "603256": 8.0,   # 宏和科技：8月提价预期上修+H1预增280-364%
    "002409": 7.0,   # 雅克科技：8/5电子特气涨停潮
    "301377": 8.0,   # 鼎泰高科：8月无新增催化+垄断叙事弱化
    "000962": 8.5,   # 东方钽业：氧化钽价格回落6%+8/22采矿禁令到期
}
for code, new_score in score_changes.items():
    s = by_code[code]
    old = s["score"]
    s["score"] = new_score
    print(f"评分 {code} {s['name']}: {old} -> {new_score}")

# ===================== 2. riskNote 追加 =====================
risk_appends = {
    "301377": " ⚠️ 8/7复查：8月无新增催化（最近事件7/23）；垄断叙事边际弱化（董秘6/15承认金洲等竞争者存在）、港股破发、实控人套现28亿，评分降至8.0",
    "000962": " ⚠️ 8/7复查：氧化钽7月下旬4700→4400元/kg回落6%（价格弹性收敛）；刚果(金)南基伍省采矿禁令8/22到期、供给恢复为边际风险点，评分降至8.5",
    "603256": " ⚠️ 8/7复查：新浪8/4深度确认Q1均价9.78元/米(+116.85%)、H1净利预增280-364%、8月提价预期上修至+1.5~2.0元/米，评分上调至8.0；但7月以来股价持续下跌、PE曾达535倍，估值与筹码风险需持续跟踪",
}
for code, append in risk_appends.items():
    s = by_code[code]
    s["riskNote"] = s["riskNote"] + append
    print(f"riskNote 追加: {code} {s['name']}")

# ===================== 3. conceptReinforcements 追加与裁剪 =====================
def add_reinforcement(code, event):
    s = by_code[code]
    s.setdefault("conceptReinforcements", [])
    s["conceptReinforcements"].append(event)
    # 按日期降序排序，保留最近3条
    s["conceptReinforcements"].sort(key=lambda e: e["date"], reverse=True)
    dropped = s["conceptReinforcements"][3:]
    s["conceptReinforcements"] = s["conceptReinforcements"][:3]
    if dropped:
        print(f"  {code} {s['name']}: 裁剪 {len(dropped)} 条 -> {[e['date'] for e in dropped]}")
    else:
        print(f"  {code} {s['name']}: reinforcements 共 {len(s['conceptReinforcements'])} 条")
    return dropped

# 国瓷材料 300285
core_logic_guoci = "收购澳洲SDI（8.16亿）锁定锆资源；锆英砂年内+17%、氧氯化锆+36%。"
by_code["300285"]["coreLogic"] = by_code["300285"]["coreLogic"].rstrip("。") + "。" + core_logic_guoci
add_reinforcement("300285", {
    "date": "2026-08-06",
    "desc": "8/5半年报落地：H1营收25.13亿(+16.64%)、归母净利3.63亿(+9.36%)、Q2环比+54.98%；8/6同花顺《涨价40%的底气》：氧化锆粉体7/27涨价10-40%已生效、高端MLCC缺口2026H2 15-20%→2027年30%、高盛口径AI服务器MLCC年复合增速约80%、国瓷从'跟随涨价'到'自主定价'",
    "source": "https://www.10jqka.com.cn/"
})

# 洁美科技 002859
core_logic_jiemei = "TrendForce预警2H26高端特规MLCC面临结构性短缺、村田BB Ratio 1.30创新高（超2018年缺货峰值1.25），全行业MLCC扩产拉动离型膜需求爆发。"
by_code["002859"]["coreLogic"] = by_code["002859"]["coreLogic"].rstrip("。") + "。" + core_logic_jiemei
add_reinforcement("002859", {
    "date": "2026-08-06",
    "desc": "同花顺8/6：离型膜销量同比+100%、供不应求延续至明年上半年、公司主动聚焦中高端",
    "source": "https://www.10jqka.com.cn/"
})

# 深南电路 002916
core_logic_shennan = "H1业绩预告中值13.5亿(+55/59%)。"
by_code["002916"]["coreLogic"] = by_code["002916"]["coreLogic"].rstrip("。") + "。" + core_logic_shennan
add_reinforcement("002916", {
    "date": "2026-08-07",
    "desc": "8月核验确认：ABF载板缺口21-30%、价格一年涨38%；味之素ABF膜垄断95%+扩产至2032年；新浪8月口径ABF Q3涨价30%起步、高端AI品类最高50%；48.82亿募资落地无锡项目",
    "source": "https://finance.sina.com.cn/"
})

# 佰维存储 688525（原0条）
add_reinforcement("688525", {
    "date": "2026-08-05",
    "desc": "8/5三大DRAM原厂2027年产能售罄（三星/SK海力士/美光仅能满足客户60-70%需求）+存储芯片全线涨停潮；8/5 SK海力士/闪迪发布HBF行业标准，2027年内存短缺逻辑显著强化，评分上调至8.5",
    "source": "https://finance.sina.com.cn/stock/zqgd/2026-08-05/doc-inimfwqf3591567.shtml"
})

# 光力科技 300480（原0条）
add_reinforcement("300480", {
    "date": "2026-08-05",
    "desc": "日本8/1第三轮管制落地：首次纳入激光隐切/划片设备（20大类后道设备、逐案审批驳回率70-80%实质准断供）；出海网8/5点名光力科技进入量产验证/批量供货，国产替代加速，评分上调至8.5",
    "source": "https://www.chwang.com/news/208484007307"
})

# 德龙激光 688170（原0条）
add_reinforcement("688170", {
    "date": "2026-08-05",
    "desc": "日本8/1第三轮管制纳入激光隐切/划片设备；出海网8/5点名德龙激光SDBG激光隐切进入量产验证/批量供货，国产替代加速，评分上调至8.0",
    "source": "https://www.chwang.com/news/208484007307"
})

# 宏和科技 603256（原0条）
add_reinforcement("603256", {
    "date": "2026-08-04",
    "desc": "新浪8/4深度《一米布撬动AI算力狂潮》：Q1均价9.78元/米(+116.85%)、H1净利预增280-364%、8月提价预期由+1.2上修至+1.5~2.0元/米、低介电二代布160元/米年内翻倍，评分上调至8.0",
    "source": "https://finance.sina.cn/stock/jdts/2026-08-04/detail-inimcpit2206855.d.html"
})

# ===================== 4. 新增卡片（4只，经三重逻辑甄别通过） =====================
new_stocks = [
    {
        "category": "制造与存储",
        "subCategory": "存储模组(DRAM/NAND)",
        "code": "301308",
        "name": "江波龙",
        "market": "创业板",
        "coreLogic": "全球领先存储模组厂商（Lexar+江波龙双品牌）。2026H1净利预增62204%-74394%（千万级跃至百亿级）为A股'预增王'；8/5存储芯片全线涨停潮中涨8.59%；董秘8/5正面回应2027年订单。2027年全球内存短缺（三大原厂产能售罄、客户配货仅60-70%）直接传导至模组厂，涨价+缺货双受益。",
        "supplyDemand": "TrendForce口径2026Q1 DRAM合约价+90-95%、NAND+55-60%；2027年短缺最严峻（三大原厂产能分配完毕、客户配货60-70%）。",
        "priceSignal": "2026H1净利预增62204%-74394%；8/5存储涨停潮涨8.59%",
        "catalyst": "2027内存短缺+涨价直接传导模组厂；H1预增王业绩兑现",
        "conceptAdded": "2026-08-05",
        "conceptSource": "2027年内存短缺确认+存储模组涨价直接受益（新浪财经8/5《存储芯片引爆盘面涨停潮》深度，页面正文2026-08-05）",
        "conceptSourceUrl": "https://finance.sina.com.cn/stock/zqgd/2026-08-05/doc-inimfwqf3591567.shtml",
        "riskNote": "股价自高点回撤近50%（8/6报道）；长城证券703元'增持'研报合规存疑被点名；融资余额59.61亿处一年70%分位",
        "tags": ["存储模组", "2027短缺", "涨价传导", "预增王"],
        "score": 4.25,
        "conceptReinforcements": []
    },
    {
        "category": "PCB产业链",
        "subCategory": "电子布(全球产能之王)",
        "code": "600176",
        "name": "中国巨石",
        "market": "主板",
        "coreLogic": "全球玻纤产能之王（电子布产能全球第一）。7628电子布年内六轮提价、8月提价预期由+1.2上修至+1.5~2.0元/米（执行后主流成交10-11元/米）；G75电子纱9000→14525元/吨(+61%)。织布机瓶颈（日本丰田垄断电子级织机）+新产能最早2028年释放，供给约束贯穿2026-2027。H1净利预增65-85%（27.84-31.21亿）。",
        "supplyDemand": "G75电子纱9000→14525元/吨(+61%)；建滔新增1.8亿米/年产能因织布机限制2026年仅释放不到20%。",
        "priceSignal": "7628电子布年内六轮提价；8月提价预期+1.5~2.0元/米；H1净利预增65-85%",
        "catalyst": "8月电子布提价预期上修；织布机产能瓶颈贯穿2026-2027；H1预增落地",
        "conceptAdded": "2026-08-04",
        "conceptSource": "8月电子布提价预期上修至+1.5~2.0元/米+织布机瓶颈供给硬约束（新浪财经8/4《一米布撬动AI算力狂潮》，页面正文2026-08-04）",
        "conceptSourceUrl": "https://finance.sina.cn/stock/jdts/2026-08-04/detail-inimcpit2206855.d.html",
        "riskNote": "7月以来股价持续下跌（市场担忧2027-2028产能集中释放后供需反转）；玻纤指数自高点回撤约51%",
        "tags": ["电子布", "全球产能之王", "织布机瓶颈", "供给硬约束"],
        "score": 4.0,
        "conceptReinforcements": []
    },
    {
        "category": "先进封装",
        "subCategory": "晶圆减薄/研磨设备(国产替代)",
        "code": "688120",
        "name": "华海清科",
        "market": "科创板",
        "coreLogic": "国内CMP设备龙头，CMP+减薄一体机为国产替代核心标的。日本8/1第三轮管制首次纳入超薄晶圆减薄/研磨机（原由DISCO等主导，对华逐案审批、驳回率70-80%实质准断供）；验证周期由2-3年压缩至6-12个月，国产导入加速。",
        "supplyDemand": "日本8/1管制约20大类先进封装后道设备、审批周期3-6个月、AI算力配套设备申请驳回率接近八成；超薄晶圆减薄/研磨机原由DISCO等日企主导。",
        "priceSignal": "验证周期由2-3年压缩至6-12个月",
        "catalyst": "日本8/1第三轮管制纳入晶圆减薄/研磨机；国产CMP+减薄一体机替代加速",
        "conceptAdded": "2026-08-03",
        "conceptSource": "日本8/1第三轮管制纳入超薄晶圆减薄/研磨机→国产CMP+减薄一体机替代加速（闪存市场8/3，页面正文2026-08-03 15:23）",
        "conceptSourceUrl": "https://m.chinaflashmarket.com/news/industry/184139",
        "riskNote": "减薄设备业务占比尚小，主业仍为CMP；验证导入仍存时间差",
        "tags": ["国产替代", "先进封装设备", "日本准断供", "CMP龙一"],
        "score": 4.25,
        "conceptReinforcements": []
    },
    {
        "category": "先进封装",
        "subCategory": "分选检测设备(国产替代)",
        "code": "300604",
        "name": "长川科技",
        "market": "创业板",
        "coreLogic": "国内分选测试设备龙头（测试机+分选机+探针台平台）。日本8/1管制纳入高精度芯片分选/检测设备（原日系主导）；管制后国产导入加速，出海网8/5明确点名长川等进入量产验证/批量供货。",
        "supplyDemand": "日本8/1第三轮管制约20大类先进封装后道设备、驳回率70-80%；高精度分选/检测设备原由日系主导。",
        "priceSignal": "出海网8/5点名进入量产验证/批量供货",
        "catalyst": "日本8/1管制纳入分选检测设备；国产测试设备导入加速",
        "conceptAdded": "2026-08-05",
        "conceptSource": "日本8/1第三轮管制纳入高精度分选/检测设备→长川国产替代加速（出海网8/5，页面正文2026-08-05 11:13）",
        "conceptSourceUrl": "https://www.chwang.com/news/208484007307",
        "riskNote": "分选检测设备国产化进程受客户验证节奏影响；日系同类设备仍具技术优势",
        "tags": ["国产替代", "测试设备", "日本准断供", "分选机龙一"],
        "score": 3.75,
        "conceptReinforcements": []
    },
]

for ns in new_stocks:
    if ns["code"] in by_code:
        print(f"!! 跳过重复标的: {ns['code']} {ns['name']}（已在板内）")
        continue
    stocks.append(ns)
    by_code[ns["code"]] = ns
    print(f"新增卡片: {ns['code']} {ns['name']} score={ns['score']} conceptAdded={ns['conceptAdded']}")

# ===================== 5. 分类内按评分降序重排 + 刷新 id =====================
# 保持原有 category 顺序
cat_order = []
for s in stocks:
    if s["category"] not in cat_order:
        cat_order.append(s["category"])

reordered = []
for cat in cat_order:
    cat_stocks = [s for s in stocks if s["category"] == cat]
    # Python sort 稳定，同分保持原文件相对顺序
    cat_stocks.sort(key=lambda s: -s["score"])
    reordered.extend(cat_stocks)

for i, s in enumerate(reordered, start=1):
    s["id"] = i

data["stocks"] = reordered

# ===================== 6. 更新 stats =====================
from collections import Counter, OrderedDict
cat_counts = Counter(s["category"] for s in reordered)
stats_categories = []
for cat in cat_order:
    stats_categories.append({"name": cat, "count": cat_counts[cat]})
data["stats"]["categories"] = stats_categories

market_counts = Counter(s["market"] for s in reordered)
data["stats"]["totalMarkets"] = {
    "主板": market_counts.get("主板", 0),
    "创业板": market_counts.get("创业板", 0),
    "科创板": market_counts.get("科创板", 0),
}
data["stats"]["totalStocks"] = len(reordered)

# ===================== 7. meta.updated =====================
data["meta"]["updated"] = TODAY

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 已写回 {DATA}")
print(f"   标的总数: {len(reordered)}")
print(f"   meta.updated: {TODAY}")
print(f"   categories: {[(c['name'], c['count']) for c in stats_categories]}")
print(f"   markets: {data['stats']['totalMarkets']}")

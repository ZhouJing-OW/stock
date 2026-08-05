#!/usr/bin/env python3
"""Apply Ming's hard logic scan report (2026-08-05) edits to hardlogic.json.

Edits:
- Downgrade: 铜冠铜箔 9.0->8.0, 宏和科技 8.5->7.0, 多氟多 8.5->7.5 (riskNote appended)
- Add: 德福科技 301511 (score 4.0, PCB产业链)
- New catalysts appended to conceptReinforcements (鼎龙/中微/三环/生益/国瓷/宏和), trimmed to 3
- riskNote updates for 源杰/国瓷/圣泉/石英/佰维/东材 (no score change)
- Re-sort by score desc within category, refresh ids, rebuild stats, meta.updated=2026-08-05
"""

import json

JSON_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"
TODAY = "2026-08-05"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]

IMPORTANT_KEYWORDS = ["涨价", "认证通过", "量产", "停产", "突破", "大单签约", "断供"]


def find_stock(code):
    for s in stocks:
        if s["code"] == code:
            return s
    return None


def trim_reinforcements(s, max_count=3):
    """Keep at most max_count newest; merge important removed events into coreLogic."""
    reifs = s.get("conceptReinforcements", [])
    if len(reifs) <= max_count:
        return
    reifs_sorted = sorted(reifs, key=lambda r: r["date"], reverse=True)
    keep = reifs_sorted[:max_count]
    removed = reifs_sorted[max_count:]
    core = s.get("coreLogic", "")
    merged = []
    for r in removed:
        if any(kw in r["desc"] for kw in IMPORTANT_KEYWORDS):
            first_sentence = r["desc"].split("；")[0]
            if first_sentence not in core:
                merged.append(f'[{r["date"]}] {first_sentence}')
    if merged:
        s["coreLogic"] = core.rstrip("。") + "。" + "；".join(merged) + "。"
    s["conceptReinforcements"] = keep


def add_reinforcement(s, date, desc, source=None):
    reifs = s.get("conceptReinforcements", [])
    for r in reifs:
        if r["date"] == date and r["desc"][:20] == desc[:20]:
            return False
    item = {"date": date, "desc": desc}
    if source:
        item["source"] = source
    reifs.append(item)
    s["conceptReinforcements"] = reifs
    trim_reinforcements(s)
    return True


# ============================================================
# 1. 降分 + riskNote 追加逻辑弱化说明
# ============================================================

s = find_stock("301217")  # 铜冠铜箔
s["score"] = 8.0
s["riskNote"] += (" ⚠️ 8/5复查（华夏时报7/23深度核实）：Q2净利0.99-1.19亿环比-7%~+12%未加速；"
                  "出货主力仍为HVLP2代（5月调研口径）、HVLP3良率仅30-40%（普华研究院7月）；"
                  "6/22-7/22股价跌超50%、滚动PE 481倍；6/16公司回应暂无扩产规划；"
                  "HVLP4加工费出现第四口径12-20万/吨（新浪6/12），四口径并存差异达15倍须人工核验。降分至8.0")
print("降分: 铜冠铜箔 9.0 -> 8.0")

s = find_stock("603256")  # 宏和科技
s["score"] = 7.0
s["riskNote"] += (" ⚠️ 8/5复查：实控人一致行动人7/2-3大宗减持875万股约18亿元（30笔209.91元/股，经济参考报7/13）；"
                  "静态PE超900倍；公司6/18风险提示自认'估值已偏离基本面、存在非理性炒作'；"
                  "6/24石英纤维电子布(Q布)通过认证为新催化（对冲项）。降分至7.0")
print("降分: 宏和科技 8.5 -> 7.0")

s = find_stock("002407")  # 多氟多
s["score"] = 7.5
s["riskNote"] += (" ⚠️ 8/5复查：8/4晚间收深交所监管函（半导体级氢氟酸相关信息披露存在重大遗漏，钛媒体8/4快讯），"
                  "叠加无水氢氟酸价格7/3起拐头下跌，降分至7.5")
print("降分: 多氟多 8.5 -> 7.5")

# ============================================================
# 2. riskNote 追加（维持评分，记录新风险/核验结论）
# ============================================================

s = find_stock("688498")  # 源杰科技 9.8 维持
s["riskNote"] += (" ⚠️ 8/5新增风险点（贝尔财经7/23，需公告复核）：5月分管销售核心高管涉嫌刑事犯罪被拘；"
                  "H1净利含约1亿非经常性损益；最大单一客户占比53.4%、境外收入2025年不足200万元。"
                  "8/4 CPO暴力反弹(+6.96%)→8/5板块大跌4%+，'退潮'言论未证实未解除，评分暂维持9.8")
print("riskNote: 源杰科技 新风险点")

s = find_stock("300285")  # 国瓷材料 9.5 维持
s["riskNote"] += (" ⚠️ 8/5复查：氧化镝价格口径冲突待核验——看板'144.5万/吨历史新高' vs 长江有色8/3'140万/吨持平' "
                  "vs 国金7/26'底部回升趋势显著'")
print("riskNote: 国瓷材料 氧化镝口径冲突")

s = find_stock("605589")  # 圣泉集团 9.0 维持
s["riskNote"] += (" ⚠️ 8/5复查：2000吨新产能投产时间口径冲突（投资者关系'2026年9月' vs 新浪6/10'Q4'），需公司公告核验")
print("riskNote: 圣泉集团 投产时间口径冲突")

s = find_stock("603688")  # 石英股份 7.0 维持
s["riskNote"] += (" ⚠️ 8/5核实完成：光伏坩埚内层砂跌破2.8万/吨（较高点-90%+）；进口半导体坩埚砂16-18万/吨、交期8个月+；"
                  "国产半导体砂12万/吨+；光纤级4.8-5.5万/吨（公司市占超80%）；"
                  "'6N缺口75%/涨价120%'未找到权威信源复核，8/4标注正确")
print("riskNote: 石英股份 核实完成")

s = find_stock("688525")  # 佰维存储 7.5 维持
s["riskNote"] += (" ⚠️ 8/5复查：董事长提议回购2-2.5亿注销；TrendForce警示NAND 2027H2供给宽松价格或修正，"
                  "NAND模组为主的中期风险")
print("riskNote: 佰维存储 回购+周期风险")

s = find_stock("601208")  # 东材科技 7.5 维持
s["riskNote"] += (" ⚠️ 8/5盘面：8/4 MLCC板块反弹中涨停，板块情绪修复（Q1高速树脂+131%已录）")
print("riskNote: 东材科技 8/4涨停盘面")

# ============================================================
# 3. 新增德福科技 (301511) — 载体铜箔+HVLP4 双卡位
#    三重逻辑甄别：供给硬约束(三井垄断90%+、国产产能2027后释放) ✓
#                 海外缺口(三井3月提价12%、HVLP4缺口1500→2500吨) ✓
#                 国产替代(国内唯一Q2小批量试产、绑定中际旭创1.6T链) ✓(试产阶段)
#    score = 逻辑强度4×0.5 + 个股受益强度4×0.5 = 4.0 (量产刚起步扣分)
#    conceptAdded = 最早公开报道日期 2026-06-12 (信源权威性低，已在riskNote标注)
# ============================================================

defu = {
    "category": "PCB产业链",
    "subCategory": "载体铜箔+HVLP4(1.6T光模块mSAP)",
    "code": "301511",
    "name": "德福科技",
    "market": "创业板",
    "coreLogic": "国内唯一载体铜箔(≤3μm可剥离超薄铜箔)Q2小批量试产企业，载体铜箔是1.6T光模块mSAP工艺与高端存储芯片刚需材料，全球仅日本三井金属稳定出货(市占90%+)，2026年3月已提价12%；1.6T光模块2026年100%采用载体铜箔、需求同比翻倍；HVLP4对标国际一线并绑定中际旭创1.6T链；国产载体铜箔产能2027年后才释放，供给硬约束成立。",
    "supplyDemand": "全球载体铜箔供给高度集中于日本三井金属(市占90%+)；国产产能2027年后才释放；HVLP4缺口2026年约1500吨→2027年2500吨(东吴证券口径，与看板铜冠条目同源)；1.6T光模块2026年100%采用载体铜箔。",
    "priceSignal": "三井金属2026年3月载体铜箔提价12%；公司Q2小批量试产(量产刚起步)",
    "catalyst": "1.6T光模块mSAP工艺放量；载体铜箔国产替代窗口打开；绑定中际旭创1.6T链",
    "conceptAdded": "2026-06-12",
    "conceptSource": "载体铜箔(1.6T光模块mSAP刚需)+三井垄断90%+国产唯一试产（新浪财经转自媒体，信源权威性低需官方复核）",
    "riskNote": "量产刚起步（Q2小批量试产），距批量供货与业绩兑现仍有距离；概念最早报道为新浪财经转情感类自媒体（2026-06-12，可信度低），需以公司公告/券商研报复核；载体铜箔技术/良率爬坡存在不确定性；与铜冠铜箔同赛道竞争。评分4.0（量产刚起步扣分）",
    "tags": ["载体铜箔", "1.6T光模块", "国产替代", "供给硬约束", "试产阶段"],
    "score": 4.0,
    "conceptReinforcements": []
}
if find_stock("301511") is None:
    stocks.append(defu)
    print("新增: 德福科技 301511 (score=4.0, PCB产业链)")
else:
    print("跳过: 德福科技已存在")

# ============================================================
# 4. 新催化 → conceptReinforcements 追加（超3条自动修剪+归纳）
# ============================================================

s = find_stock("300054")  # 鼎龙股份: 8/2 光刻胶产线投产
add_reinforcement(s, "2026-08-02",
                  "8/2官宣国内首条全流程自主光刻胶产线投产（潜江二期300吨、合计330吨；纯度99.999%、覆盖90nm-28nm、树脂自主）；40余款产品、8款批量采购；潜江三期抛光垫开工")
print("强化: 鼎龙股份 +8/2光刻胶产线投产")

s = find_stock("688012")  # 中微公司: H1净利预增公告确认
add_reinforcement(s, "2026-08-05",
                  "8/5扫描确认：H1净利预增282-311%（27-29亿）公告落地；其中约19.82亿为公允价值变动/投资收益，主业营收+34.89%，业绩质量需甄别")
print("强化: 中微公司 +H1预增确认")

s = find_stock("300408")  # 三环集团: 二次回购
add_reinforcement(s, "2026-08-04",
                  "二次回购方案（5-10亿，首轮回购8.9亿已完成）；港股8/4 +3.86%")
print("强化: 三环集团 +二次回购")

s = find_stock("600183")  # 生益科技: 8/4 CPO反弹涨停
add_reinforcement(s, "2026-08-04",
                  "8/4 CPO暴力反弹日涨停（21股涨停名单内），板块景气验证；建滔九轮涨价延续CCL涨价逻辑",
                  "https://finance.eastmoney.com/")
print("强化: 生益科技 +8/4涨停")

s = find_stock("300285")  # 国瓷材料: 太阳诱电9/1二涨+村田Q1利润
add_reinforcement(s, "2026-08-05",
                  "太阳诱电9/1第二次涨价落地（财联社7/29）；村田Q1营业利润+59.8%；与非网8/5 MLCC全线调涨30%深度，涨价向粉体上游传导强化")
print("强化: 国瓷材料 +太阳诱电二涨/村田利润")

s = find_stock("603256")  # 宏和科技: 6/24 Q布认证（新催化，对冲减持利空）
add_reinforcement(s, "2026-06-24",
                  "6/24石英纤维电子布(Q布)通过认证，新催化（对冲实控人减持利空）")
print("强化: 宏和科技 +6/24 Q布认证")

# ============================================================
# 5. 重排: category 内按 score 降序, 刷新 id, 更新 stats
# ============================================================

categories_order = [c["name"] for c in data["stats"]["categories"]]

cat_map = {}
for s in stocks:
    cat_map.setdefault(s["category"], []).append(s)

new_stocks = []
for cat in categories_order:
    if cat in cat_map:
        cat_map[cat].sort(key=lambda x: (-x["score"], x["code"]))
        new_stocks.extend(cat_map[cat])
# 兜底: 新出现的 category
for cat, items in cat_map.items():
    if cat not in categories_order:
        items.sort(key=lambda x: (-x["score"], x["code"]))
        new_stocks.extend(items)

for i, s in enumerate(new_stocks, 1):
    s["id"] = i

# stats
stat_cats = []
for cat in categories_order:
    cnt = sum(1 for s in new_stocks if s["category"] == cat)
    if cnt:
        stat_cats.append({"name": cat, "count": cnt})
seen = {c["name"] for c in stat_cats}
for cat, items in cat_map.items():
    if cat not in seen:
        stat_cats.append({"name": cat, "count": len(items)})

stat_markets = {}
for s in new_stocks:
    stat_markets[s["market"]] = stat_markets.get(s["market"], 0) + 1

data["stocks"] = new_stocks
data["stats"] = {
    "categories": stat_cats,
    "totalMarkets": stat_markets,
    "totalStocks": len(new_stocks)
}

# ============================================================
# 6. meta.updated
# ============================================================
data["meta"]["updated"] = TODAY

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print(f"hardlogic.json 更新完成")
print(f"总标的: {len(new_stocks)}")
print(f"meta.updated: {TODAY}")
print(f"分类: " + ", ".join(f'{c["name"]}({c["count"]})' for c in stat_cats))
print(f"板块: {stat_markets}")
# 验证降分与新标的
for code in ("301217", "603256", "002407", "301511"):
    s = find_stock(code)
    print(f"  {s['name']}({code}): score={s['score']}, id={s['id']}")
print("=" * 60)

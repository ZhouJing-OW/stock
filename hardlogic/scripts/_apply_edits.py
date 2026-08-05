# -*- coding: utf-8 -*-
"""
hardlogic.json 编辑决策脚本 (2026-08-03)
基于 Ming 扫描报告执行：评分调整 / 数据修正 / riskNote 补充 / 新候选标的 /
催化事件追加与裁剪(归纳coreLogic) / 分类内降序重排 / id重编号 / stats与meta更新。
"""
import json, io

PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with io.open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]
by_code = {s["code"]: s for s in stocks}

def get(code):
    return by_code[code]

# ---------------------------------------------------------------- 2. 评分调整
get("002436")["score"] = 7.5   # 兴森科技 8.0 -> 7.5
get("605358")["score"] = 8.0   # 立昂微 7.5 -> 8.0

# ---------------------------------------------------------------- 3. riskNote 补充
# 兴森科技
s = get("002436")
s["riskNote"] += " ⚠️ 8/3复查：PE(TTM)350倍+、PB9.7倍（7/29新浪英才），海外客户收入贡献未验证；ABF良率与台系仍有5-10pct差距；中报预增247-316%已计入股价，估值与兑现风险显著，降分至7.5"

# 宏和科技
s = get("603256")
s["riskNote"] += " ⚠️ 8/3复查：6/9公告第二、第三大股东（实控人王文洋家族一致行动人）拟减持不超总股本3%，按当日收盘价可套现超56亿（凤凰财经6/16）；80亿扩产+赴港上市募资，资金链压力需跟踪"

# 云南锗业
s = get("002428")
s["riskNote"] += " ⚠️ 8/3复查：高纯红磷80%份额被日本NCI/RASA垄断，2026年日企收紧配额曾致阶段性断供（新风险点）；长协'锁单不锁价'（市场价±20%浮动）；18个月产能建设期与履约期存在时间错配"

# 东方钽业
s = get("000962")
s["riskNote"] += " ⚠️ 8/3复查：刚果(金)南基伍省采矿禁令5/22起3个月，8/22到期，供给恢复是边际风险点"

# 铜冠铜箔 加工费第三口径
s = get("301217")
s["riskNote"] += " ⚠️ 8/3复查：HVLP4加工费第三口径30万/吨（一牛网6/17），与捷配'2万/吨'、东吴'15-20万/吨'三口径并存、差异达15倍，必须人工核验"

# ---------------------------------------------------------------- 4. 数据修正
# 生益科技：建滔 6轮 -> 九轮
s = get("600183")
assert "建滔年内6轮涨价确认CCL景气。" in s["coreLogic"]
s["coreLogic"] = s["coreLogic"].replace("建滔年内6轮涨价确认CCL景气。", "建滔已连续九轮涨价确认CCL景气（7/8捷配）。")
assert "建滔6轮涨价确认行业景气" in s["catalyst"]
s["catalyst"] = s["catalyst"].replace("建滔6轮涨价确认行业景气", "建滔九轮涨价确认行业景气")

# 深南电路 coreLogic 同步修正建滔轮次
s = get("002916")
assert "建滔第6轮涨价+15%确认PCB全产业链景气。" in s["coreLogic"]
s["coreLogic"] = s["coreLogic"].replace("建滔第6轮涨价+15%确认PCB全产业链景气。", "建滔连续九轮涨价确认PCB全产业链景气。")

# 长鑫科技：市值 3.28万亿 -> 4万亿
s = get("688825")
assert "市值3.28万亿已成A股第一" in s["riskNote"]
s["riskNote"] = s["riskNote"].replace("市值3.28万亿已成A股第一", "市值7/31突破4万亿跻身全球TOP30（原3.28万亿数据已过时）；7/28公告纳入MSCI中国全股票指数(8/10生效)")

# ---------------------------------------------------------------- 5. 新候选标的（通过三重逻辑甄别）
new_stocks = [
    {
        "category": "PCB产业链",
        "subCategory": "T-glass/LowCTE电子布(国产替代)",
        "code": "002080",
        "name": "中材科技",
        "market": "主板",
        "coreLogic": "T-glass/LowCTE电子布国产替代核心标的（泰山玻纤）：日东纺垄断全球90%+ LowCTE电子布，T-glass 2026年缺口率超40%（较2025年14%大幅扩大）；英伟达高管赴日本抢料；已供货英伟达H100、华为昇腾；泰山玻纤已具备近5000吨电子布产能、2026年规划3500万米/年。",
        "supplyDemand": "T-glass缺口>40%；高端织布机交付周期18-24个月；日东纺新产能2027年才投产（山西证券口径）。",
        "priceSignal": "电子布行业年内5轮提价、均价7.4元/米（较2025Q3低点+100%）",
        "catalyst": "T-glass/LowCTE电子布缺口扩大；英伟达/谷歌竞相争购电子布；泰山玻纤国产替代产能释放",
        "conceptAdded": "2026-02-04",
        "conceptSource": "T-glass/LowCTE电子布缺口40%+英伟达/谷歌争购+泰山玻纤国产替代（财联社2026-02-04最早报道）",
        "conceptSourceUrl": "https://www.cls.cn/detail/2280400",
        "riskNote": "公司6/28主动提示电子布相关产品营收占比小，弹性需打折（证券时报）；高端织布机交付周期18-24个月制约扩产节奏",
        "tags": ["国产替代", "供给硬约束", "T-glass", "英伟达链", "电子布"],
        "score": 3.8,
        "conceptReinforcements": [],
        "id": 0
    },
    {
        "category": "PCB产业链",
        "subCategory": "电子布(低介电特种布)",
        "code": "301526",
        "name": "国际复材",
        "market": "创业板",
        "coreLogic": "电子布涨价高弹性标的：年内5轮提价、均价7.4元/米（较2025Q3低点+100%）；低介电特种布市场缺口超50%、行业零库存、订单排期9个月；2025年扭亏为盈（净利2.6-3.5亿）；6/8-12周涨30.76%领跑板块。",
        "supplyDemand": "低介电特种布市场缺口超50%；行业零库存、订单排期9个月（凤凰财经6/16口径）；电子布涨价向高端特种布扩散。",
        "priceSignal": "电子布均价7.4元/米(+100% vs 2025Q3低点)；6/8-12周涨30.76%",
        "catalyst": "电子布年内第五轮涨价落地（证券时报6/15）；低介电特种布缺口扩大；扭亏为盈业绩弹性",
        "conceptAdded": "2026-06-15",
        "conceptSource": "电子布年内第五轮涨价落地+低介电特种布缺口超50%（证券时报2026-06-15）",
        "conceptSourceUrl": "https://www.stcn.com/article/detail/3960532.html",
        "riskNote": "与宏和科技（超薄电子布全球龙一）同赛道存在逻辑重叠；玻纤行业周期属性，若涨价放缓弹性回落",
        "tags": ["涨价传导", "电子布", "供给缺口", "业绩反转"],
        "score": 3.8,
        "conceptReinforcements": [],
        "id": 0
    },
]
for ns in new_stocks:
    stocks.append(ns)
    by_code[ns["code"]] = ns

# ---------------------------------------------------------------- 6/7. 催化事件追加 + 裁剪(保留最近3条, 旧条目重要事件归纳coreLogic)
def add_reinf(code, date, desc, source=None):
    entry = {"date": date, "desc": desc}
    if source:
        entry["source"] = source
    get(code)["conceptReinforcements"].append(entry)

def trim(code):
    s = get(code)
    rs = s["conceptReinforcements"]
    rs.sort(key=lambda r: r["date"], reverse=True)
    if len(rs) > 3:
        dropped = rs[3:]
        s["conceptReinforcements"] = rs[:3]
        return dropped
    return []

# 深南电路：+07-29，裁剪07-24并归纳（鹏鼎百亿扩产）
add_reinf("002916", "2026-07-29",
          "新浪英才ABF紧缺深度：高盛7月口径缺口上调至2028年51%、短缺起点提前至2026Q2；味之素ABF膜Q3涨约30%、交期超6个月；T-glass/LowCTE玻纤布短缺致部分ABF扩产延后6-12个月；中报预告中值13.5亿(+55/59%)")
dropped = trim("002916")
for d in dropped:
    if d["date"] == "2026-07-24":
        s = get("002916")
        s["coreLogic"] += "鹏鼎控股百亿扩产验证PCB全产业链景气。"

# 生益科技：+07-08（九轮涨价确认）
add_reinf("600183", "2026-07-08",
          "捷配：覆铜板暴涨超270%，建滔已连续九轮涨价；生益FR-4年内累计涨幅近40%",
          "https://www.jiepei.com/")
trim("600183")

# 风华高科：+07-30，裁剪07-15并归纳（村田BB值/交期52周）
add_reinf("000636", "2026-07-30",
          "上证报：三星8/1 MLCC涨价30%今日正式生效；MLCC升至AI服务器BOM第三大成本项（摩根士丹利拆解）")
dropped = trim("000636")
for d in dropped:
    if d["date"] == "2026-07-15":
        s = get("000636")
        s["coreLogic"] += "村田MLCC订单积压比(BB值)超2018年历史峰值、高端MLCC交期延长至52周。"

# 洁美科技：+07-30
add_reinf("002859", "2026-07-30",
          "三星8/1 MLCC涨价30%正式生效；高端MLCC交期拉长至4-5个月")
trim("002859")

# 国瓷材料：+07-30（裁剪07-20，其内容已在coreLogic）
add_reinf("300285", "2026-07-30",
          "上证报：三星8/1 MLCC涨价30%正式生效；氧化锆粉体7/27起涨10-40%落地")
trim("300285")

# 三环集团：+07-24
add_reinf("300408", "2026-07-24",
          "FX168：国内三环及风华预计8月跟进涨价、10月预计还有一轮；MLCC三龙头BB Ratio 1.25-1.31创近五年峰值")
trim("300408")

# 铜冠铜箔：+06-17
add_reinf("301217", "2026-06-17",
          "一牛网：HVLP4全球缺口2026年1500吨→2027年2500吨；英伟达直接下场锁产能、CCL配额制",
          "https://m.16rd.com/writings-865271-1.html")
trim("301217")

# 宏和科技：+06-16
add_reinf("603256", "2026-06-16",
          "凤凰财经：宏和电子布年内5轮提价、2026Q1均价9.78元/米(+110%)、特种布毛利率61.31%")
trim("603256")

# 彤程新材：+07-28
add_reinf("603650", "2026-07-28",
          "凤凰网：国产高端光刻胶产业化提速，彤程获头部晶圆厂批量订单、1000吨/年产能国内最大；ArF营收+800%")
trim("603650")

# 立昂微：+06-26
add_reinf("605358", "2026-06-26",
          "36氪：重掺硅片全球仅信越/SUMCO稳定供货、价格被推高10-25%；12英寸重掺订单饱满，中信测算2025-2028年需求年化增速20-30%")
trim("605358")

# 沪硅产业：+07-07
add_reinf("688126", "2026-07-07",
          "腾讯新闻再次确认：信越/SUMCO/环球晶5月二轮提价，12英寸+5-8%、AI专用+18-22%；2026年12英寸月需求1100万片vs供给<1000万片")
trim("688126")

# 复旦微电：+07-30
add_reinf("688385", "2026-07-30",
          "证券时报原文核实：FPGA交期52周、现货XC 220→850元、EP 120→1200元、涨7-10倍；7/16新品+Agent平台")
trim("688385")

# 安路科技：+07-30
add_reinf("688107", "2026-07-30",
          "证券时报受访企业：FPGA交期52周、现货价格涨7-10倍；定增6/23提交注册")
trim("688107")

# 东方钽业：+07-08
add_reinf("000962", "2026-07-08",
          "Mysteel：钽锭现货6400-6500元/kg维持高位；刚果(金)5/29将钽纳入战略矿产清单、权利金税率升至10%")
trim("000962")

# 长鑫科技：07-31条目补充市值/MSCI/华尔街信息
s = get("688825")
for r in s["conceptReinforcements"]:
    if r["date"] == "2026-07-31":
        r["desc"] += "；7/31市值突破4万亿跻身全球TOP30；7/29华尔街建仓报道"
trim("688825")

# ---------------------------------------------------------------- 8. 评分复核（略，维持既有判断）
# ---------------------------------------------------------------- 9. 分类内降序重排 + 刷新id
from collections import OrderedDict
cat_order = []
for s in stocks:
    if s["category"] not in cat_order:
        cat_order.append(s["category"])

new_stocks_list = []
for cat in cat_order:
    group = [s for s in stocks if s["category"] == cat]
    group.sort(key=lambda s: s["score"], reverse=True)  # stable sort
    new_stocks_list.extend(group)

for i, s in enumerate(new_stocks_list, start=1):
    s["id"] = i
data["stocks"] = new_stocks_list

# stats 更新
from collections import Counter
cat_counts = Counter(s["category"] for s in new_stocks_list)
mkt_counts = Counter(s["market"] for s in new_stocks_list)
data["stats"] = {
    "categories": [{"name": c, "count": cat_counts[c]} for c in cat_order],
    "totalMarkets": {k: mkt_counts[k] for k in ["主板", "创业板", "科创板"] if k in mkt_counts},
    "totalStocks": len(new_stocks_list),
}

# ---------------------------------------------------------------- 10. meta.updated
data["meta"]["updated"] = "2026-08-03"

with io.open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("OK  totalStocks =", len(new_stocks_list))
for c in cat_order:
    print(f"  {c}: {cat_counts[c]}")
print("  markets:", dict(mkt_counts))
print("  meta.updated =", data["meta"]["updated"])

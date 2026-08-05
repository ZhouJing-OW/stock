#!/usr/bin/env python3
"""
硬逻辑看板编辑决策脚本
基于 Ming 2026-07-28 扫描报告执行所有编辑决策
"""

import json
import copy
from datetime import datetime, date

JSON_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]
stats = data["stats"]
meta = data["meta"]

# ============================================================
# 0. 修正云南锗业 conceptSourceUrl（原URL指向韩国金融无关文章）
# ============================================================
for s in stocks:
    if s["code"] == "002428":
        s["conceptSourceUrl"] = "https://pdf.dfcfw.com/pdf/H3_AP202606091823395435_1.pdf"
        s["conceptAdded"] = "2026-06-09"
        print(f"[修正] 云南锗业 conceptAdded: 2026-06-20 → 2026-06-09, URL已修正为东吴证券研报")
        break

# ============================================================
# 1. 评分调整
# ============================================================
score_changes = {
    "688825": 7.0,    # 长鑫科技 4.25→7.0: H1净利+2244-2544%暴增+科创板上市+全球第四稀缺性
    "002371": 8.0,    # 北方华创 8.5→8.0: 估值历史高位, 国产化率35%后边际弹性递减
}

for s in stocks:
    if s["code"] in score_changes:
        old_score = s["score"]
        s["score"] = score_changes[s["code"]]
        print(f"[评分] {s['name']}({s['code']}): {old_score} → {s['score']}")

# ============================================================
# 2. Risk Note 更新
# ============================================================
risk_updates = {
    "002371": "高端设备与AMAT/TEL仍有代差；海外客户导入周期长。⚠️ 7/28复查：估值已处历史高位，国产化率从16%→35%后边际弹性递减；SK海力士接触无实质订单转化。建议下调至8.0分。",
    "603688": "光伏业务占比大受行业周期影响。⚠️ 7/28复查：半导体级认证进度始终不确定，光伏业务受行业周期影响大，持续关注。",
    "301377": "股价2年涨47倍，PE极高；钨/钴原材料涨价。⚠️ 建滔7月6日第六次涨价后大股东套现35.62亿。⚠️ 7/28复查：PCB板块7/23利好出尽式跌停，若构成板块见顶信号需降分。日系钻针涨价逻辑仍在，观察7-15天。",
    "000657": "钨价已从3月高点102万元/吨回落至约95.5万元/吨(-6.4%)，H2不确定性增加。⚠️ 7/28复查：若钨粉跌破80万需重新评估评分。商务部7/24新增14家欧盟实体出口管制名单构成新催化对冲。",
    "300666": "高端靶材与日矿金属/霍尼韦尔仍有差距；产能扩张节奏。⚠️ 7/28复查：股价突破775亿元市值创历史新高，估值风险需关注。",
    "688019": "高端抛光液与国际巨头仍有差距；客户导入周期长。⚠️ 7/28复查：国产CMP抛光液国产化率约30%，逻辑维持但近期无新催化。",
}

for s in stocks:
    if s["code"] in risk_updates:
        s["riskNote"] = risk_updates[s["code"]]
        print(f"[风险] {s['name']}({s['code']}): riskNote已更新")

# ============================================================
# 3. 新增 conceptReinforcements（追加后最多保留3条）
# ============================================================

def add_reinforcement(stock, date, desc, source):
    """追加reinforcement，按日期排序保留最近3条；删除前将重要事件归纳到coreLogic"""
    stock.setdefault("conceptReinforcements", [])
    stock["conceptReinforcements"].append({
        "date": date,
        "desc": desc,
        "source": source
    })
    # 去重（同日期+同描述）
    seen = set()
    unique = []
    for r in stock["conceptReinforcements"]:
        key = (r["date"], r["desc"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    stock["conceptReinforcements"] = unique

    # 按日期排序
    stock["conceptReinforcements"].sort(key=lambda x: x["date"], reverse=True)

    # 超过3条：删除最旧的，重要事件归纳到coreLogic
    important_kw = ["涨价", "认证", "量产", "停产", "突破", "大单", "签约", "断供", "缺口", "暴增"]
    while len(stock["conceptReinforcements"]) > 3:
        removed = stock["conceptReinforcements"].pop()  # 最旧的
        # 检查是否重要
        is_important = any(kw in removed["desc"] for kw in important_kw)
        if is_important:
            summary = removed["desc"].split("；")[0].split("，")[0]  # 第一句摘要
            if summary not in stock.get("coreLogic", ""):
                stock["coreLogic"] = stock["coreLogic"].rstrip("。") + "。" + summary + "。"

# 深南电路：7/24 鹏鼎控股百亿扩产验证PCB全产业链景气
for s in stocks:
    if s["code"] == "002916":
        add_reinforcement(s,
            "2026-07-24",
            "鹏鼎控股百亿扩产验证PCB全产业链景气；高盛上调ABF缺口至2028年51%；味之素ABF膜Q3涨价30%确认",
            "https://www.21jingji.com/article/20260724/herald/")
        print(f"[强化] 深南电路: 新增7/24 reinforcement")
        break

# 鼎龙股份：追加断供35天事件
for s in stocks:
    if s["code"] == "300054":
        # 已有7/26的reinforcement，无需重复
        print(f"[强化] 鼎龙股份: 7/26 reinforcement已存在，跳过")
        break

# 中钨高新：7/24 商务部新增14家欧盟实体出口管制
for s in stocks:
    if s["code"] == "000657":
        add_reinforcement(s,
            "2026-07-24",
            "商务部7月24日将德国莱茵金属等14家欧盟实体列入出口管制名单，稀土管制升级为全链条监督；商务部26号公告7月1日起实施",
            "https://www.mofcom.gov.cn/article/zwgk/gkzcfg/202607/20260703541234.shtml")
        print(f"[强化] 中钨高新: 新增7/24 reinforcement")
        break

# ============================================================
# 4. 新增候选标的（通过三重逻辑甄别）
# ============================================================

new_stocks = []

# --- 候选1: 联合化学 (301209.SZ) - 光刻胶上游单体 ---
new_stocks.append({
    "category": "半导体上游",
    "subCategory": "光刻胶上游单体(KrF核心原料)",
    "code": "301209",
    "name": "联合化学",
    "market": "创业板",
    "coreLogic": "控股子公司启辰半导体聚焦苯乙烯类光刻胶单体，一期200吨/年产线6月底试产，纯度99.9%向日韩送样。日本进口光刻胶2026Q1同比暴跌95%，KrF国产化率仅3%。单体是制约光刻胶国产化的真正根源：纯度要求1ppb以下、占光刻胶成本35-45%。光刻胶单体客户验证周期远短于光刻胶成品，变现节奏更快。",
    "supplyDemand": "日本四大光刻胶巨头6月22日对华断供。中国从日本进口光刻胶：2025Q1约2200吨→2026Q1仅111.3吨(-95%)。国内KrF光刻胶国产化率不足3%、ArF不足1%。光刻胶单体纯度要求1ppb以下，全球仅少数企业掌握。",
    "priceSignal": "一期200吨试产；纯度99.9%向日韩送样；若满产预计年产值1-1.2亿元",
    "catalyst": "日本光刻胶断供→上游单体国产替代窗口打开；单体是光刻胶'卡脖子'真正根源",
    "conceptAdded": "2026-07-22",
    "conceptSource": "日本光刻胶断供满月→光刻胶上游单体国产化突破(KrF核心原料)",
    "conceptSourceUrl": "https://wap.stockstar.com/detail/IG2026072200033392",
    "riskNote": "光刻胶单体业务刚启动试产距营收贡献还需验证；纯度99.9%距离1ppb以下半导体级标准仍有差距；目前主业为有机颜料非半导体",
    "tags": ["海外断供", "国产替代", "光刻胶单体", "KrF原料", "去日化"],
    "score": 7.0,
    "conceptReinforcements": []
})

# --- 候选2: 风华高科 (000636.SZ) - MLCC本体制造 ---
new_stocks.append({
    "category": "被动元件",
    "subCategory": "MLCC本体制造(全品类)",
    "code": "000636",
    "name": "风华高科",
    "market": "主板",
    "coreLogic": "国内MLCC全品类龙头。MLCC进入超级涨价周期：国巨7月1日全系列电容涨价30-80%（覆盖50%营收，首次纳入直接客户）；村田年内第三轮涨价10-40%。三星电机两月内斩获7500亿韩元AI服务器MLCC长协。AI服务器单机MLCC用量达普通13倍、价值量约3倍。高端MLCC供不应求，供需缺口预计延续至2028年。Q1毛利率仅20%处于周期底部，涨价弹性巨大。",
    "supplyDemand": "高端MLCC扩产周期18-24个月；核心原材料陶瓷粉体高度集中（村田+三星电机垄断）。国巨AI相关BB值达1.4。高端MLCC供不应求。",
    "priceSignal": "7月1日涨停响应国巨涨价；Q1毛利率不足20%（2018年峰值近50%）弹性空间大",
    "catalyst": "国巨7/1全系列涨30-80%；村田年内第三轮涨价；三星电机7500亿韩元AI长协",
    "conceptAdded": "2026-07-01",
    "conceptSource": "MLCC超级涨价周期：国巨全系列涨30-80%+村田年内第三轮涨价+AI服务器MLCC需求暴增",
    "conceptSourceUrl": "https://finance.sina.com.cn/stock/relnews/cn/2026-07-01/doc-inifhrqu1010394.shtml",
    "riskNote": "MLCC周期性强涨价可持续性待观察；毛利率尚处历史低位但意味着弹性大；与三环集团存在竞争",
    "tags": ["MLCC龙头", "涨价周期", "AI算力", "国产替代", "周期反转"],
    "score": 7.5,
    "conceptReinforcements": []
})

# --- 候选3: 九丰能源 (605090.SH) - 氦气/电子特气 ---
new_stocks.append({
    "category": "电子特气",
    "subCategory": "氦气(半导体黄金气体)",
    "code": "605090",
    "name": "九丰能源",
    "market": "主板",
    "coreLogic": "国内民营自主提氦规模龙头（150万m³/年产能全国第一），100%国产气源，航天+半导体双认证。氦气是半导体制造不可替代的'黄金气体'（光刻/刻蚀/气相沉积核心工序必需）。日本酸素7月起全线氦气涨价30%+；卡塔尔产能损毁+俄罗斯出口管制锁死致全球42-50%产能停摆；国产化率仅25%。Q1高纯氦产销量同比+60%。海南商业航天特气配套项目已投产。",
    "supplyDemand": "卡塔尔产能永久损毁（占全球33-35%）；俄罗斯出口管制延长至2027年底；全球40%+产能停摆。氦气为天然气伴生资源无法独立开采，扩产周期3-5年。国内自给率不足15%，电子级6N高纯氦高度依赖进口。",
    "priceSignal": "Q1高纯氦产销量同比+61%；日本酸素7月全线涨30%+；海南航天特气已投产毛利率47.53%",
    "catalyst": "日本酸素7月全线氦气涨价30%+；商务部对氦气实施临时禁止出口管理；卡塔尔产能不可逆损毁",
    "conceptAdded": "2026-06-22",
    "conceptSource": "日本酸素7月起氦气全线涨价30%+全球供给危机+国产提氦龙头",
    "conceptSourceUrl": "https://wap.eastmoney.com/a/202606223777989034.html",
    "riskNote": "非AI PCB主线赛道；国产提氦在半导体端大规模认证仍需时间；氦气价格受地缘政治影响波动大",
    "tags": ["国产替代", "供给硬约束", "黄金气体", "航天+半导体", "提氦龙头"],
    "score": 7.0,
    "conceptReinforcements": []
})

# 加入新标的
for ns in new_stocks:
    stocks.append(ns)
    print(f"[新增] {ns['name']}({ns['code']}) → {ns['category']}/{ns['subCategory']} score={ns['score']}")

# ============================================================
# 5. 按评分降序在每个 category 内重排，刷新 id
# ============================================================

# 按category分组
from collections import OrderedDict
cats = OrderedDict()
for s in stocks:
    cat = s["category"]
    cats.setdefault(cat, []).append(s)

# 每类按score降序排列
for cat in cats:
    cats[cat].sort(key=lambda x: x["score"], reverse=True)

# 展平+重新编号
new_stocks_list = []
new_id = 1
for cat in cats:
    for s in cats[cat]:
        s["id"] = new_id
        new_stocks_list.append(s)
        new_id += 1

data["stocks"] = new_stocks_list

# ============================================================
# 6. 更新 stats
# ============================================================
from collections import Counter
cat_counts = Counter()
market_counts = Counter()
for s in new_stocks_list:
    cat_counts[s["category"]] += 1
    market_counts[s["market"]] += 1

stats["categories"] = [{"name": k, "count": v} for k, v in cat_counts.items()]
stats["totalMarkets"] = dict(market_counts)
stats["totalStocks"] = len(new_stocks_list)
data["stats"] = stats

# ============================================================
# 7. 更新 meta.updated
# ============================================================
meta["updated"] = "2026-07-28"
data["meta"] = meta

# ============================================================
# 8. 写回 JSON
# ============================================================
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n=== 完成 ===")
print(f"总标的数: {stats['totalStocks']} (曾53→现{stats['totalStocks']})")
print(f"新增: 联合化学、风华高科、九丰能源 (+3)")
print(f"移除: 无")
print(f"评分调整: 长鑫科技 4.25→7.0, 北方华创 8.5→8.0")
print(f"日期修正: 云南锗业 conceptAdded 6/20→6/9")
print(f"新增 reinforcement: 深南电路+1, 中钨高新+1")
print(f"分类统计: {dict(cat_counts)}")
print(f"市场分布: {dict(market_counts)}")

# 打印各类别标的清单
print(f"\n=== 最终标的列表 ===")
for s in new_stocks_list:
    print(f"  #{s['id']:2d} {s['name']:6s} {s['code']} score={s['score']:3.1f} | {s['category']}/{s['subCategory']} | conceptAdded={s['conceptAdded']}")

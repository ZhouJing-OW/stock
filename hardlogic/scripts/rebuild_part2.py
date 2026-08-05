#!/usr/bin/env python3
"""Part 2: Append remaining stocks and finalize hardlogic.json"""
import json
from datetime import date

OUTPUT = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

def mk(cat, sub, code, name, mkt, core, sd, ps, cat2, added, csrc, curl, risk, tags, score, reins=None):
    return {
        "category": cat, "subCategory": sub, "code": code, "name": name, "market": mkt,
        "coreLogic": core, "supplyDemand": sd, "priceSignal": ps, "catalyst": cat2,
        "conceptAdded": added, "conceptSource": csrc, "conceptSourceUrl": curl,
        "riskNote": risk, "tags": tags, "score": score,
        "conceptReinforcements": reins or []
    }

# Read existing stocks from part 1
with open(OUTPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

existing = data["stocks"]
print(f"Existing stocks: {len(existing)}")

# Add remaining stocks
new_stocks = [
    # === 被动元件 (8) ===
    mk("被动元件","MLCC介质粉体","300285","国瓷材料","创业板",
       "全球领先MLCC介质粉体企业，钛酸钡粉体是MLCC核心介质材料。高端120nm以下粉体全球供给60%+由日美企业垄断。MLCC超级周期向上游粉体传导；氧化镝涨至144.5万/吨历史新高。7月20日公告自7月27日起氧化锆粉体涨价10-40%：东曹断供+MLCC粉体涨价+氧化锆涨价三重共振。",
       "高端钛酸钡粉体全球供给高度集中(日本堺化学28%+美国Ferro20%+日本化学14%)。稀土出口管制使日系粉体厂商原料受限。",
       "6月2日涨超14%创历史新高；月内融资净买入11.64亿元",
       "稀土出口管制持续收紧；日系MLCC粉体断供风险；村田7月第三轮涨价10-40%",
       "2026-05-31","稀土管控+日系粉体断供+MLCC涨价",
       "https://caifuhao.eastmoney.com/news/20260531105849115520790",
       "高端120nm以下粉体追赶日美仍需时间；产能扩产节奏",
       ["核心原材料","稀土管制受益","国产替代","上游卡位"],9.5,
       [{"date":"2026-07-20","desc":"国瓷材料公告自7月27日起氧化锆粉体涨价10-40%；东曹断供+MLCC粉体涨价+氧化锆涨价三重共振","source":"https://www.cls.cn/detail/2428607"},
        {"date":"2026-07-17","desc":"村田7月第三轮MLCC涨价10-40%今日正式执行；国盛证券研判涨价至2027年底；TrendForce预警2H26高端MLCC结构性短缺","source":"https://news.qq.com/rain/a/20260701A09T7600"},
        {"date":"2026-07-06","desc":"国盛证券：MLCC涨价持续至2027年底+高容延续至2028-29年；本轮与2018年本质不同是AI算力升级带来的产品结构性迭代与产能错配","source":"https://news.qq.com/rain/a/20260701A09T7600"}]),
    
    mk("被动元件","MLCC全品类龙头","000636","风华高科","主板",
       "国内唯一阻容感全品类覆盖企业，2026年底MLCC月产能突破500亿只。AI服务器单机柜MLCC用量超40万颗，价值量从H3000美元升至VR200的22000美元。年内完成三轮调价，全系产品涨10-30%。Q1车规订单同比+183%。村田7月第三轮涨价10-40%已执行。",
       "MLCC或迎'史上最长缺货潮'延续至2027-2028年。氧化镝紧缺进一步收紧高端MLCC供给。渠道库存仅1-1.5个月历史低位。",
       "年内三轮涨价全系+10-30%；Q1车规订单+183%；年内股价累涨252%",
       "村田7月第三轮涨价10-40%；太阳诱电5月涨价20%；三星6月跟涨",
       "2026-03-03","MLCC涨价潮+AI服务器需求",
       "https://pdf.dfcfw.com/pdf/H3_AP202603031820210581_1.pdf",
       "公司澄清'未通过英伟达全系列认证'；日韩厂商主导高端市场",
       ["涨价传导","AI算力","全品类","国产替代"],9.5,
       [{"date":"2026-07-17","desc":"村田7月第三轮MLCC涨价10-40%今日正式执行；国巨全系列电容涨价同步进行；国盛证券研判MLCC涨价至2027年底","source":"https://news.qq.com/rain/a/20260701A09T7600"},
        {"date":"2026-07-06","desc":"国盛证券：MLCC涨价持续至2027年底+高容延续至2028-29年","source":"https://news.qq.com/rain/a/20260701A09T7600"},
        {"date":"2026-07-03","desc":"OFweek深度分析确认氧化镝对日出口归零18个月+氧化钇归零6个月；日系MLCC全链条原料从理论断供变为物理层面系统性紧缺","source":"https://ee.ofweek.com/2026-07/ART-8420-2816-30693192.html"}]),
    
    mk("被动元件","钽铌材料(钽粉/钽丝/钽靶)","000962","东方钽业","主板",
       "全球钽铌材料龙头，电容级钽粉国内市占率超50%/全球20-25%。AI服务器钽电容用量是传统服务器10倍以上。钽靶材切入中芯国际先进制程供应链。钽精矿257.5美元/磅年内涨222%维持高位；刚果(金)鲁巴亚矿区矿难持续影响全球15%钽供应。",
       "全球钽矿高度集中于刚果(金)/卢旺达。刚果(金)鲁巴亚矿区接连矿难，全球约15%钽供应中断。钽供给年增速<10%，AI需求增速>20%。",
       "钽锭2600→6700元/kg(+158%)；钽精矿80→257.5美元/磅(+222%)",
       "刚果(金)矿难持续影响供应；AI服务器钽电容用量暴增；公司切入中芯国际供应链",
       "2026-04-21","钽价暴涨确认：钽锭+190%、钽精矿+158%",
       "https://caifuhao.eastmoney.com/news/20260421164701348191390",
       "矿端供给有恢复风险；钽矿价格波动大",
       ["海外垄断","供给硬约束","AI算力","刚果矿难","涨价158%"],9.0,
       [{"date":"2026-07-06","desc":"钽精矿257.5美元/磅年内涨222%维持第15天高位；刚果(金)鲁巴亚矿区矿难持续影响全球15%钽供应","source":"https://news.qq.com/rain/a/20260701A09T7600"}]),
    
    mk("被动元件","电感(TLVR)","002138","顺络电子","主板",
       "自研TLVR大电流电感通过英伟达、AMD认证，切入全球AI服务器供应链。车载电感业务占比超50%。日系电感7月第二轮涨价已全面落地：村田/太阳诱电再涨25-35%，TLVR涨70%+。稀土出口管制使日系电感原材料持续吃紧。",
       "AI服务器VPD供电架构普及，TLVR电感需求爆发。单颗价值量翻倍，预计2028年市场空间200-300亿元。",
       "AI服务器专用电感年初至今翻倍，部分型号涨超110%",
       "英伟达/AMD认证通过；村田/太阳诱电电感涨价；VPD供电架构推广",
       "2026-03-06","电感涨价+英伟达认证",
       "https://finance.sina.com.cn/stock/aigc/jgdy/2026-03-06/doc-inhpzkwr9250265.shtml",
       "认证通过到批量供货有时间差；电感竞争格局相对分散",
       ["AI供电","英伟达链条","涨价传导","国产替代"],9.0,
       [{"date":"2026-07-15","desc":"日系电感7月第二轮涨价已全面落地：村田/太阳诱电电感再涨25-35%高端料号涨超70%；TLVR电感涨70%+；稀土出口管制使日系电感厂商原材料持续吃紧","source":"https://m.36kr.com/p/3845611027728640"},
        {"date":"2026-07-01","desc":"日系电感7月第二轮提价正式执行！村田/太阳诱电电感年初至今涨15-35%部分型号涨超110%","source":"https://m.36kr.com/p/3845611027728640"}]),
    
    mk("被动元件","MLCC高端突破","300408","三环集团","创业板",
       "MLCC产品客户认可度持续提升，Q1归母净利润7.91亿元同比+48.48%。光通信等行业需求增长叠加MLCC高端化。预计Q3落地新一轮涨价。MLCC介质粉体+成品双布局。",
       "MLCC行业供需紧张，村田稼动率超90%，行业BB Ratio逐月递增。高容MLCC结构性短缺加剧。",
       "Q1净利润+48.48%；预计Q3涨价落地",
       "村田/三星/太阳诱电全线涨价；AI服务器MLCC需求爆发",
       "2026-04-24","MLCC涨价+业绩高增",
       "http://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/lastest/rptid/830399616481/index.phtml",
       "日韩厂商高端产能转向AI/车规后，国内厂商能否抢占中高端份额需观察",
       ["涨价传导","AI算力","高端突破","业绩兑现"],8.5,
       [{"date":"2026-07-06","desc":"TrendForce预警AI高端MLCC激励日韩大厂BB Ratio创新高，2H26高端特规MLCC面临结构性短缺","source":"https://www.trendforce.cn/presscenter/news/20260706-13137.html"}]),
    
    mk("被动元件","MLCC离型膜(核心耗材)","002859","洁美科技","主板",
       "全球纸质载带市占率约70%，MLCC离型膜国内唯一实现BOPET基膜→涂布全链条自主供应企业。离型膜已批量供货村田/三星/国巨/风华/三环五大核心客户，涨价40%+确认。",
       "全球MLCC离型膜由日本帝人/琳得科/藤森工业垄断。AI服务器MLCC用量暴增→MLCC全行业扩产→离型膜作为流延成型不可替代耗材需求倍增。",
       "4-5月起向客户发布涨价通知部分产品涨幅超40%；离型膜满产满销月出货超2700万㎡",
       "MLCC全行业涨价扩产；村田BB Ratio 1.30创历史新高；离型膜涨价40%+确认",
       "2026-07-11","MLCC离型膜涨价40%+国内唯一全链条供应商+全球纸质载带龙头+五大MLCC原厂全覆盖",
       "https://www.toutiao.com/article/7641930685753704966/",
       "MLCC行业周期性波动若AI投入放缓将影响需求",
       ["隐形冠军","涨价40%","MLCC耗材","国产替代","五大原厂覆盖"],8.0,
       [{"date":"2026-07-06","desc":"TrendForce预警2H26高端特规MLCC面临结构性短缺；村田BB Ratio 1.30创新高超2018年缺货峰值1.25；全行业MLCC扩产拉动离型膜需求爆发","source":"https://www.trendforce.cn/presscenter/news/20260706-13137.html"}]),
    
    mk("被动元件","MLCC镍粉","605376","博迁新材","主板",
       "全球80nm镍粉领先企业，约50%产能供给三星电机（AI服务器MLCC全球份额超45%）。镍粉是MLCC内电极不可替代材料。120nm及以下高端镍粉持续受益产品升级。Q1营收+64%，净利+49.6%。",
       "高端MLCC介质层减薄至0.5μm以下，镍粉粒径需同步缩小至150nm以下。三星电机AI服务器MLCC全球份额超45%。",
       "Q1营收+64%，净利+49.6%；2025年净利+150.6%",
       "AI服务器MLCC用量暴增；三星电机产能全开；村田/三星/太阳诱电全线涨价",
       "2026-06-23","MLCC镍粉：AI服务器MLCC用量暴增+高端镍粉量价齐升+三星电机核心供应商",
       "https://www.hibor.com.cn/repinfodetail_5161989.html",
       "客户集中度高（三星电机占比大）；纳米镍粉技术迭代风险",
       ["核心原材料","AI算力","三星电机链","技术壁垒"],8.0),
    
    mk("被动元件","钽电容","300726","宏达电子","创业板",
       "钽电容国产龙头。松下2月起钽电容涨价15-30%，国巨旗下基美6月起涨价5-65%。钽电容在军工/AI服务器/车规等领域不可替代性强。全品类被动元件涨价潮中钽电容弹性最大。",
       "钽电容涨价覆盖全品类。AI服务器供电模组对高可靠性钽电容需求大增。",
       "松下涨价15-30%；基美涨价5-65%",
       "钽电容全品类涨价；AI服务器供电需求；军工/车规国产化",
       "2026-03-03","钽电容涨价+被动元件景气",
       "https://www.cls.cn/detail/2301217",
       "钽矿供给依赖海外，上游钽锭价格年内暴涨+158%叠加刚果(金)矿难，原料成本压力加剧可能压缩毛利率",
       ["涨价传导","军工","AI算力","高弹性"],7.0,
       [{"date":"2026-07-09","desc":"钽精矿维持257.5美元/磅高位第18天(年内涨222%)；刚果(金)鲁巴亚矿区矿难持续影响全球15%钽供应；基美/松下/国巨全品类钽电容涨价延续","source":"https://qhweb.eastmoney.com/news/202606153771874648.html"}]),
]

# Append and process
all_stocks = existing + new_stocks
print(f"Total after append: {len(all_stocks)}")

# Sort by category order then score desc
cat_order = [
    "PCB产业链","电子特气","被动元件","光互连",
    "半导体上游","半导体设备零部件","先进封装",
    "制造与存储","功率半导体","医疗材料","小金属(AI金属)"
]

cats = {}
for s in all_stocks:
    c = s.get("category","其他")
    cats.setdefault(c,[]).append(s)

sorted_stocks = []
for cat in cat_order:
    if cat in cats:
        cats[cat].sort(key=lambda x: x.get("score",0), reverse=True)
        sorted_stocks.extend(cats[cat])
for cat, items in cats.items():
    if cat not in cat_order:
        items.sort(key=lambda x: x.get("score",0), reverse=True)
        sorted_stocks.extend(items)

# Re-ID
for i, s in enumerate(sorted_stocks, 1):
    s["id"] = i

# Stats
cat_counts = {}
mkt_counts = {}
for s in sorted_stocks:
    cat_counts[s["category"]] = cat_counts.get(s["category"],0) + 1
    mkt_counts[s["market"]] = mkt_counts.get(s["market"],0) + 1

data["stocks"] = sorted_stocks
data["meta"]["updated"] = date.today().isoformat()
data["stats"] = {
    "categories": [{"name":k,"count":v} for k,v in cat_counts.items()],
    "totalMarkets": mkt_counts,
    "totalStocks": len(sorted_stocks)
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"DONE: {len(sorted_stocks)} stocks")
print(f"Cats: {cat_counts}")
print(f"Markets: {mkt_counts}")

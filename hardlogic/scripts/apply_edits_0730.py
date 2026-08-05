# 硬逻辑看板 2026-07-30 编辑决策脚本
# 基于 Ming 扫描报告执行所有变更

import json, os, copy

JSON_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data['stocks']
updated = []

# Build lookup by code for quick editing
stock_map = {s['code']: s for s in stocks}

# ═══════════════════════════════════════════════
# 1. 评分调整
# ═══════════════════════════════════════════════

# 源杰科技 9.5→9.8
stock_map['688498']['score'] = 9.8

# 铜冠铜箔 8.5→9.0
stock_map['301217']['score'] = 9.0

# 三环集团 8.5→9.0
stock_map['300408']['score'] = 9.0

# 风华高科 8.0→8.5
stock_map['000636']['score'] = 8.5

# 圣泉集团 8.5→9.0
stock_map['605589']['score'] = 9.0

# 三孚股份 8.5→7.5
stock_map['603938']['score'] = 7.5

# 宏达电子 6.5→5.5
stock_map['300726']['score'] = 5.5

# ═══════════════════════════════════════════════
# 2. CoreLogic / RiskNote 更新
# ═══════════════════════════════════════════════

# 铜冠铜箔: coreLogic 追加设备锁仓
s = stock_map['301217']
if '设备锁定至2029年' not in s['coreLogic']:
    s['coreLogic'] = s['coreLogic'].rstrip('.') + '。HVLP4通过英伟达全流程认证批量供货（内资唯一HVLP1-4全谱系量产企业）；设备锁定至2029年（全球唯一供应商三船制作所年产能仅8-10台）。'
    # Also update supplyDemand
    s['supplyDemand'] = 'AI服务器PCB铜箔用量大幅增长。HVLP铜箔技术壁垒高。国产化率约25%。HVLP供需缺口28-39%预计持续至2028年。设备锁定至2029年。'
    s['catalyst'] = 'AI PCB扩产拉动铜箔需求；HVLP铜箔国产替代加速；HVLP4英伟达认证通过；设备壁垒极强'

# 三环集团: coreLogic 补充港股上市+1000层突破
s = stock_map['300408']
s['coreLogic'] = 'MLCC产品客户认可度持续提升，Q1归母净利润7.91亿元同比+48.48%。MLCC实现1000层+堆叠、1μm介电层突破，订单排至2027年。7月9日港股上市。光通信等行业需求增长叠加MLCC高端化。预计Q3落地新一轮涨价。MLCC介质粉体+成品双布局。'
s['supplyDemand'] = 'MLCC行业供需紧张，村田稼动率超90%，行业BB Ratio逐月递增。高容MLCC结构性短缺加剧。三环全产业链自给提供成本壁垒。'
s['catalyst'] = '村田/三星/太阳诱电全线涨价；AI服务器MLCC需求爆发；港股上市；MLCC 1000层突破'
s['priceSignal'] = 'Q1净利润+48.48%；预计Q3涨价落地；7/9港股上市'
s['tags'] = list(set(s['tags'] + ['港股上市', '全产业链']))

# 风华高科: coreLogic 补充7/29涨价函
s = stock_map['000636']
s['coreLogic'] = s['coreLogic'].rstrip('.') + '。7月29日三星电机宣布自8月1日起MLCC涨价30%（AI服务器需求飙升），太阳诱电自9月1日起涨价。日韩龙头加速消费级转AI高端，消费级中高容MLCC产能受挤压，订单外溢至国产厂商。'
s['catalyst'] = '国巨7/1全系列涨30-80%；村田年内第三轮涨价；三星电机7500亿韩元AI长协；7/29三星宣布8/1涨30%；订单排至2026Q3'

# 圣泉集团: coreLogic 补充涨价执行细节
s = stock_map['605589']
if '全系涨价15-20%' not in s['coreLogic']:
    s['coreLogic'] = '国内电子级PPO/PPE树脂绝对龙头，国内市占率约70%，M6-M9全系列通过英伟达/华为/英特尔认证。全球高端树脂供应链持续偏紧（SABIC沙特朱拜勒工厂3月底停产至今）。现有1500吨/年满产零库存，在建2000吨Q4投产。7月13日起全系涨价15-20%正式执行。SABIC单体价从65→100万元/吨(+54%)。SABIC朱拜勒工厂停产进入第120+天仍无复产迹象。'

# 中船特气（新）— 在电子特气分类新增

# 源杰科技: coreLogic 补充H1业绩
s = stock_map['688498']
s['coreLogic'] = '全球第二大硅光激光器芯片供应商，市占23.6%。EML供需缺口>30%（Lumentum官方确认），订单排至2027年。100G EML通过英伟达认证，200G EML验证中。CW光源70mW大规模供货、100mW批量交付。H1营收9-9.5亿(+339~364%)净利6-6.5亿(+1197~1305%)超市场预期。353家机构调研全市场第一。'
s['priceSignal'] = 'H1营收+339~364%，H1净利+1197~1305%；订单排至2027年；毛利率77.8%'

# 三孚股份: riskNote 追加逻辑弱化说明
s = stock_map['603938']
s['riskNote'] = '光纤需求有周期性；电子级产品验证周期长。⚠️ 7/30复查：逻辑链条过长，碳化硅涨价的关联性间接，非硬供给约束核心标的。建议下调评分。'

# 宏达电子: riskNote 追加说明
s = stock_map['300726']
s['riskNote'] = '钽矿供给依赖海外，上游钽锭价格年内暴涨+158%叠加刚果(金)矿难，原料成本压力加剧可能压缩毛利率。⚠️ 7/29复查：钽精矿维持257.5美元/磅高位。⚠️ 7/30复查：钽电容不在本轮AI供给约束主线上，催化缺失，下调评分。'

# 鼎龙股份: riskNote 追加催化偏淡说明
s = stock_map['300054']
s['riskNote'] = s['riskNote'].rstrip('.') + '。⚠️ 7/30复查：近期无新增断供事件，短期催化偏淡。但逻辑基础仍在（CMP抛光垫+PSPI双赛道）。'

# ═══════════════════════════════════════════════
# 3. ConceptReinforcements 追加
# ═══════════════════════════════════════════════

def add_reinforcement(stock_code, date, desc, source, trim_to=3):
    """Add a reinforcement event, trim to keep only N most recent."""
    s = stock_map[stock_code]
    s['conceptReinforcements'].append({
        'date': date,
        'desc': desc,
        'source': source
    })
    # Sort by date (newest first), trim
    s['conceptReinforcements'].sort(key=lambda x: x['date'], reverse=True)
    if len(s['conceptReinforcements']) > trim_to:
        # Before deleting, check if oldest items contain important events
        old_items = s['conceptReinforcements'][trim_to:]
        for old in old_items:
            # Check if any important keywords in the removed item
            keywords = ['涨价', '认证', '量产', '停产', '突破', '大单', '断供', '订单']
            if any(k in old['desc'] for k in keywords):
                # Summarize into coreLogic
                if '[旧重整]' not in s['coreLogic']:
                    s['coreLogic'] += f" [旧重整]重要事件({old['date']}): {old['desc'][:80]}..."
        s['conceptReinforcements'] = s['conceptReinforcements'][:trim_to]

# 风华高科: 追加7/29三星涨价30%
add_reinforcement('000636', '2026-07-29',
    '三星电机宣布自8月1日起MLCC涨价30%（AI服务器需求飙升）；太阳诱电自9月1日起涨价；日韩龙头消费级转AI高端→产能挤压→订单外溢国产厂商',
    'https://www.cls.cn/detail/2438573')

# 铜冠铜箔: 追加H1业绩+HVLP4认证
add_reinforcement('301217', '2026-07-30',
    'H1净利2.05-2.25亿(+486~544%)；HVLP4通过英伟达全流程认证批量供货（内资唯一HVLP1-4全谱系量产）；设备锁仓至2029年（全球唯一供应商三船制作所年产能仅8-10台）',
    'https://finance.sina.com.cn/stock/relnews/cn/2026-07-30/doc-inihmvnu3267093.shtml')

# 源杰科技: 追加H1业绩超预期
add_reinforcement('688498', '2026-07-21',
    'H1营收9-9.5亿(+339~364%)净利6-6.5亿(+1197~1305%)超市场预期；Q2单季净利环比+134~162%；353家机构调研全市场第一；与CSP厂商确定合作意向',
    'https://finance.sina.com.cn/stock/relnews/cn/2026-07-21/doc-inihmvnu3267093.shtml')

# 三环集团: 追加港股上市+MLCC突破
add_reinforcement('300408', '2026-07-09',
    '7月9日港股上市；MLCC实现1000层+堆叠、1μm介电层突破，订单排至2027年；2026年底产能扩至1200亿颗；Q1营收+46%净利+48%',
    'https://finance.eastmoney.com/a/202607093778654321.html')

# ═══════════════════════════════════════════════
# 4. 新标的：中船特气 (688146) — 六氟化钨
# ═══════════════════════════════════════════════

new_stock = {
    "category": "电子特气",
    "subCategory": "六氟化钨(全球龙一)",
    "code": "688146",
    "name": "中船特气",
    "market": "科创板",
    "coreLogic": "全球最大六氟化钨（WF₆）生产企业（2000吨/年产能），WF₆为半导体CVD钨膜沉积唯一商用前驱体气体。日本关东电化、中央硝子因原料断供将2026H2产能停摆，全球供给缺口骤升。公司已从年度调价转月度调价，价格同比大幅上调。上游钨粉2026年3月冲高至230万元/吨。Q1营收7.01亿（+36%）净利润1.01亿（+17%）。",
    "supplyDemand": "全球六氟化钨总年产仅8000-9000吨，供给高度集中。日本关东电化/中央硝子产能停摆加剧缺口。公司1000吨新增产能预计2027Q1-Q2落地。2026年全球钨供需缺口1.85万吨（占需求17.6%）。",
    "priceSignal": "Q1营收+36%净利润+17%；WF₆6N级桶装报价2000-2500元/kg折合220-300万元/吨；从年度调价转月度调价",
    "catalyst": "日本关东电化/中央硝子2026H2产能停摆；六氟化钨全球供给缺口形成；国内唯一大规模量产企业；月度涨价机制",
    "conceptAdded": "2026-06-01",
    "conceptSource": "六氟化钨供给硬缺口+日本产能停摆+全球最大产能+月度涨价机制",
    "conceptSourceUrl": "https://www.cls.cn/detail/2387512",
    "riskNote": "股价年内涨超190%涨幅已大，5月28日公司公告称尚未签署任何新的大额实质性订单协议。需关注7月底中报业绩是否包含六氟化钨涨价兑现。",
    "tags": [
        "全球龙一",
        "供给硬约束",
        "涨价周期",
        "半导体特气",
        "日本断供"
    ],
    "score": 8.5,
    "conceptReinforcements": [],
    "id": 999  # will be reassigned
}

stocks.append(new_stock)

# ═══════════════════════════════════════════════
# 5. 分类内按评分降序重排 + 刷新id + 更新stats
# ═══════════════════════════════════════════════

# Group by category
from collections import OrderedDict
cat_order = []
cat_stocks = {}
for s in stocks:
    cat = s['category']
    if cat not in cat_stocks:
        cat_stocks[cat] = []
        cat_order.append(cat)
    cat_stocks[cat].append(s)

# Sort each category by score descending, then renumber
new_stocks = []
new_id = 1
new_cats = []
for cat in cat_order:
    group = sorted(cat_stocks[cat], key=lambda x: (-x['score'], x['name']))
    for s in group:
        s['id'] = new_id
        new_id += 1
        new_stocks.append(s)
    new_cats.append({"name": cat, "count": len(group)})

# Update stats
market_counts = {'主板': 0, '创业板': 0, '科创板': 0}
for s in new_stocks:
    m = s['market']
    if m in market_counts:
        market_counts[m] += 1

data['stocks'] = new_stocks
data['stats'] = {
    "categories": new_cats,
    "totalMarkets": market_counts,
    "totalStocks": len(new_stocks)
}

# Update meta
data['meta']['updated'] = '2026-07-30'

# ═══════════════════════════════════════════════
# 6. 写回
# ═══════════════════════════════════════════════

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 更新完成：共 {len(new_stocks)} 只标的，{len(new_cats)} 个分类")
print(f"   meta.updated = {data['meta']['updated']}")

# 输出变更摘要
print("\n📋 评分调整：")
changes = {
    '688498': ('9.5', '9.8', 'H1业绩暴增+12倍'),
    '301217': ('8.5', '9.0', '设备锁仓至2029+HVLP4英伟达认证'),
    '300408': ('8.5', '9.0', 'MLCC 1000层突破+港股上市'),
    '000636': ('8.0', '8.5', '7/29三星涨价30%利好'),
    '605589': ('8.5', '9.0', '涨价15-20%执行+SABIC停产确认'),
    '603938': ('8.5', '7.5', '逻辑链条过长'),
    '300726': ('6.5', '5.5', '不在AI供给约束主线上'),
}
for code, (old, new, reason) in changes.items():
    name = stock_map[code]['name']
    print(f"   {name}({code}): {old}→{new} ({reason})")

print(f"\n📋 新增标的：中船特气(688146) 8.5分")
print(f"📋 新增Reinforcement事件：风华高科/铜冠铜箔/源杰科技/三环集团")

#!/usr/bin/env python3
"""Apply Ming's hardlogic scan report edits to hardlogic.json."""

import json, sys
from datetime import datetime, date

DATA_PATH = r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json'
TODAY = '2026-07-31'

def load():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_stock(stocks, code):
    for s in stocks:
        if s['code'] == code:
            return s
    return None

def trim_reinforcements(s, keep=3):
    """保留最近keep条，删除前将重要事件归纳到coreLogic"""
    reinf = s.get('conceptReinforcements', [])
    if len(reinf) <= keep:
        return
    reinf.sort(key=lambda x: x['date'], reverse=True)
    removed = reinf[keep:]
    for r in removed:
        desc = r['desc']
        important_keywords = ['涨价', '认证通过', '量产', '停产', '突破', '大单签约',
                              '业绩', '净利预增', '净利润']
        if any(kw in desc for kw in important_keywords):
            first_sentence = desc.split('；')[0]
            s['coreLogic'] = s['coreLogic'].rstrip('。') + '。' + first_sentence + '。'
    s['conceptReinforcements'] = reinf[:keep]

def main():
    data = load()
    stocks = data['stocks']

    # ===== 1. 降分 =====
    downgrades = {
        '603938': ('三孚股份', '逻辑链条过长（光纤四氯化硅→AI光互连→碳化硅涨价关联性间接），reinforcements空白已超过30天，非硬供给约束核心标的。'),
        '603290': ('斯达半导', '功率半导体涨价属于全行业产能周期而非不可替代供给硬约束，reinforcements仅7/1一条且已过30天，逻辑弱化明显。'),
        '300373': ('扬杰科技', '同上，功率涨价属产能周期非物理瓶颈，若AI需求放缓海外大厂可快速回调产能，逻辑弱化。'),
    }
    for code, (name, note) in downgrades.items():
        s = find_stock(stocks, code)
        if s:
            s['score'] = 7.0
            s['riskNote'] += f' ⚠️ 7/31复查：{note}'
            print(f'  ✓ 降分: {name}({code}) 7.5→7.0')

    # ===== 2. 新增中船特气 =====
    new_stock = {
        'category': '电子特气',
        'subCategory': '六氟化钨(全球龙一)',
        'code': '688146',
        'name': '中船特气',
        'market': '科创板',
        'coreLogic': '全球六氟化钨产能第一（2230吨/年），超越日本关东电化。日本关东电化+中央硝子7月1日起永久停产（合计占全球约25%产能），原料为中国钨出口管制断供无复产可能。已进入台积电/三星/SK海力士/美光供应链，三星/SK海力士紧急启动认证目标8月批量进口。HBM/3D NAND对六氟化钨需求暴增，三星2026年需求920-1000吨、海力士约700吨、台积电约900-1000吨。新增1000吨产能预计2027年建成。六氟化钨价格已暴涨约200%。',
        'supplyDemand': '日本关东电化+中央硝子7月1日起永久停产减少约2000吨/年全球供给（占25%）。中船特气产能2230吨全球第一。六氟化钨是3D NAND/HBM刻蚀不可替代材料，认证壁垒极高（2年+），日企停产后全球供给缺口无解。',
        'priceSignal': '六氟化钨价格已暴涨约200%；中船特气订单排至2027年',
        'catalyst': '日本两厂7月1日永久停产+中国钨出口管制原料断供双重物理约束；三星/SK海力士/台积电紧急认证加速国产替代',
        'conceptAdded': '2026-06-09',
        'conceptSource': '日本六氟化钨供应商因原料断供宣布7月1日起永久停产→中船特气全球龙一直接受益',
        'conceptSourceUrl': 'https://finance.sina.com.cn/money/bond/2026-06-09/doc-iniaueff2060878.shtml',
        'riskNote': '股价年内已涨超700%，PE极高需注意拥挤度与回撤风险',
        'tags': ['全球龙一', '海外停产', '供给硬约束', '国产替代', 'HBM'],
        'score': 9.5,
        'conceptReinforcements': [
            {
                'date': '2026-07-01',
                'desc': '日本关东电化+中央硝子7月1日起永久停产正式生效！六氟化钨价格已暴涨约200%；三星/SK海力士启动中船特气紧急认证',
                'source': 'https://caifuhao.eastmoney.com/news/20260615040624377389170'
            }
        ]
    }
    stocks.append(new_stock)
    print(f'  ✓ 新增: 中船特气 688146 (score=9.5)')

    # ===== 3. 新催化追加 =====
    # 深南电路 002916
    s = find_stock(stocks, '002916')
    if s:
        s['conceptReinforcements'].append({
            'date': '2026-07-30',
            'desc': '三星电子表示芯片短缺2027年进一步加剧延续至2028年；ABF载板缺口预测持续上调；高盛维持ABF缺口扩大至2028年51%判断',
            'source': 'https://www.cls.cn/detail/2440123'
        })
        trim_reinforcements(s, 3)
        print(f'  ✓ 深南电路: +7/30催化, trimmed→{len(s["conceptReinforcements"])}条')

    # 风华高科 000636
    s = find_stock(stocks, '000636')
    if s:
        s['conceptReinforcements'].append({
            'date': '2026-07-10',
            'desc': 'H1归母净利2.7-3.0亿(+61.84-79.82%)；Q2净利1.81-2.11亿环比+104-138%；MLCC量价齐升叠加降本增效成效显著',
            'source': 'https://finance.sina.com.cn/roll/2026-07-10/doc-inihinfz5180428.shtml'
        })
        trim_reinforcements(s, 3)
        print(f'  ✓ 风华高科: +7/10催化, trimmed→{len(s["conceptReinforcements"])}条')

    # 中钨高新 000657
    s = find_stock(stocks, '000657')
    if s:
        s['conceptReinforcements'].append({
            'date': '2026-07-30',
            'desc': '中金公司7/30研报明确：钨业龙头有望迎来量价齐升；7月钨价下跌企稳后再次出现涨价迹象；出口管制持续收紧强化供给约束',
            'source': 'https://www.stcn.com/article/detail/4024430'
        })
        s['conceptReinforcements'].sort(key=lambda x: x['date'], reverse=True)
        if len(s['conceptReinforcements']) > 3:
            trim_reinforcements(s, 3)
        print(f'  ✓ 中钨高新: +7/30催化 (共{len(s["conceptReinforcements"])}条)')

    # 鼎泰高科 301377: 更新7/09条目
    s = find_stock(stocks, '301377')
    if s:
        for r in s['conceptReinforcements']:
            if r['date'] == '2026-07-09':
                r['desc'] = '7月9日港股上市募资48亿港元（引入高瓴/易方达/霸菱等16家基石）；英伟达Kyber NVL144延期验证高端PCB瓶颈+日系钨棒全面停产双重催化'
        print(f'  ✓ 鼎泰高科: 更新7/09条目追加港股IPO')

    # ===== 4. 按分类 score 降序重排 + 重编号 =====
    categories_order = [
        'PCB产业链', '电子特气', '被动元件', '光互连', '半导体上游',
        '半导体设备零部件', '先进封装', '制造与存储', '功率半导体',
        '医疗材料', '小金属(AI金属)'
    ]
    cat_map = {}
    for s in stocks:
        cat = s['category']
        if cat not in cat_map:
            cat_map[cat] = []
        cat_map[cat].append(s)

    new_stocks = []
    for cat in categories_order:
        if cat in cat_map:
            cat_map[cat].sort(key=lambda x: x['score'], reverse=True)
            new_stocks.extend(cat_map[cat])

    # 处理新出现的 category
    for cat, items in cat_map.items():
        if cat not in categories_order:
            items.sort(key=lambda x: x['score'], reverse=True)
            new_stocks.extend(items)

    for i, s in enumerate(new_stocks, 1):
        s['id'] = i

    data['stocks'] = new_stocks
    print(f'  ✓ 重排+重编号: {len(new_stocks)}只')

    # ===== 5. 更新 stats =====
    stat_cats = {}
    stat_markets = {}
    for s in new_stocks:
        cat = s['category']
        stat_cats[cat] = stat_cats.get(cat, 0) + 1
        mkt = s['market']
        stat_markets[mkt] = stat_markets.get(mkt, 0) + 1

    data['stats'] = {
        'categories': [{'name': k, 'count': v} for k, v in stat_cats.items()],
        'totalMarkets': stat_markets,
        'totalStocks': len(new_stocks)
    }

    # ===== 6. 更新 meta =====
    data['meta']['updated'] = TODAY

    save(data)
    print(f'\n=== 全部完成 ===')
    print(f'标的数: 56 → {len(new_stocks)}')
    print(f'分类: {stat_cats}')
    print(f'板块: {stat_markets}')

    # 打印新排序后的前几支票确认
    print('\n--- 各赛道Top2 ---')
    for cat in categories_order:
        if cat in cat_map:
            items = sorted(cat_map[cat], key=lambda x: x['score'], reverse=True)
            top2 = items[:2]
            print(f'{cat}: ' + ', '.join(f'{s["name"]}({s["score"]})' for s in top2))

if __name__ == '__main__':
    main()

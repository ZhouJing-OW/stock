# -*- coding: utf-8 -*-
import json, sys

path = r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data['stocks']
changes = []

# 1. Remove duplicate 风华高科 (keep id=20, remove id=16)
stocks = [s for s in stocks if not (s.get('code') == '000636' and s.get('id') == 16)]
changes.append('Removed duplicate 风华高科 id=16')

# 2. Fix id:40 duplicate - 石英股份(silica, 603688) and 联合化学(301209)
for s in stocks:
    if s.get('code') == '301209':  # 联合化学
        s['category'] = '半导体上游'
        s['subCategory'] = '光刻胶单体'
        changes.append(f'Fixed 联合化学: added category={s["category"]}')
    if s.get('code') == '603688':  # 石英股份 - keep id=40
        pass  # stays id=40

# 3. Renumber IDs (continuous 1-based)
for i, s in enumerate(stocks, 1):
    if s['id'] != i:
        changes.append(f'{s["name"]}({s["code"]}): id {s["id"]} -> {i}')
        s['id'] = i

# 4. Add reinforcements for MLCC stocks
mlcc_rf = {
    "date": "2026-07-30",
    "desc": "三星电机宣布自8月1日起MLCC价格上调30%，所有出货产品执行新价格；日本太阳诱电通知自9月1日起MLCC涨价。日韩龙头消费级转AI高端→MLCC涨价周期再确认",
    "source": "https://www.cls.cn/detail/2438573"
}

for s in stocks:
    code = s.get('code', '')
    new_rf = None
    
    # 风华高科(000636) - the one we kept
    if code == '000636':
        existing = [r['date'] for r in s.get('conceptReinforcements', [])]
        if '2026-07-30' not in existing:
            new_rf = mlcc_rf
    
    # 国瓷材料(300285)
    elif code == '300285':
        existing = [r['date'] for r in s.get('conceptReinforcements', [])]
        if '2026-07-30' not in existing:
            new_rf = mlcc_rf
    
    # 洁美科技(002859)
    elif code == '002859':
        existing = [r['date'] for r in s.get('conceptReinforcements', [])]
        if '2026-07-30' not in existing:
            new_rf = mlcc_rf
    
    # 中钨高新(000657) - 中金研报
    elif code == '000657':
        existing = [r['date'] for r in s.get('conceptReinforcements', [])]
        if '2026-07-30' not in existing:
            new_rf = {
                "date": "2026-07-30",
                "desc": "中金公司研报：中国钨业龙头有望迎来量价齐升；国内钨价7月下跌企稳后再现涨价迹象，海外溢价率创历史新高",
                "source": "https://www.cls.cn/detail/2438573"
            }
    
    # 扬杰科技(300373) - 熊本地震
    elif code == '300373':
        existing = [r['date'] for r in s.get('conceptReinforcements', [])]
        if '2026-07-30' not in existing:
            new_rf = {
                "date": "2026-07-30",
                "desc": "熊本地震致多家半导体工厂停工检修，涉及的车规芯片/功率半导体短期交货不确定性提升，可能进一步推升功率半导体价格预期",
                "source": "https://www.cls.cn/detail/2438573"
            }
    
    if new_rf:
        s.setdefault('conceptReinforcements', []).append(new_rf)
        changes.append(f'{s["name"]}({code}): added 7/30 reinforcement')

# 5. Trim reinforcements to max 3, promote important events to coreLogic
important_kw = ['涨价', '认证', '量产', '停产', '突破', '大单', '签约', '投产', '断供', '盈利', '净利']
for s in stocks:
    rfs = s.get('conceptReinforcements', [])
    if len(rfs) > 3:
        rfs.sort(key=lambda x: x.get('date', ''))
        oldest = rfs[0]
        is_important = any(kw in oldest.get('desc', '') for kw in important_kw)
        if is_important:
            brief = f"\n【重要事件归纳{oldest['date']}】{oldest['desc'][:120]}"
            if brief not in s.get('coreLogic', ''):
                s['coreLogic'] = s.get('coreLogic', '') + brief
                changes.append(f'{s["name"]}: promoted oldest rf to coreLogic ({oldest["date"]})')
        rfs.pop(0)
        changes.append(f'{s["name"]}: trimmed rf from {len(rfs)+1} to {len(rfs)}')

# 6. Sort by category order then score desc
cat_order = [
    'PCB产业链', '电子特气', '被动元件', '光互连', '半导体上游',
    '半导体设备零部件', '先进封装', '制造与存储', '功率半导体', '医疗材料', '小金属(AI金属)'
]
def sort_key(s):
    try:
        ci = cat_order.index(s.get('category', ''))
    except ValueError:
        ci = 999
    return (ci, -s.get('score', 0))

stocks.sort(key=sort_key)
for i, s in enumerate(stocks, 1):
    s['id'] = i

# 7. Update stats
from collections import Counter
cat_c = Counter(s.get('category', '其他') for s in stocks)
mkt_c = Counter(s.get('market', '其他') for s in stocks)
data['stats'] = {
    'categories': [{'name': k, 'count': v} for k, v in sorted(cat_c.items(), key=lambda x: -x[1])],
    'totalMarkets': dict(mkt_c),
    'totalStocks': len(stocks)
}

data['meta']['updated'] = '2026-07-31'

# Write back
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Updated: {len(stocks)} stocks, {len(data["stats"]["categories"])} categories')
print('Changes:')
for c in changes:
    print(f'  {c}')

import json, sys

path = r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data['stocks']

# Remove duplicates by code (keep first occurrence)
seen = set()
unique = []
for s in stocks:
    code = s['code']
    if code not in seen:
        seen.add(code)
        unique.append(s)
    else:
        print(f"Removed duplicate: {s['name']} ({code}) id={s.get('id')}")

# Re-sort within categories by score desc
from collections import OrderedDict
categories = {}
for s in unique:
    cat = s['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(s)

for cat in categories:
    categories[cat].sort(key=lambda x: x['score'], reverse=True)

cat_order = [
    "PCB产业链", "电子特气", "被动元件", "光互连", "半导体上游",
    "半导体设备零部件", "先进封装", "制造与存储", "功率半导体", "医疗材料", "小金属(AI金属)"
]

new_stocks = []
for cat in cat_order:
    if cat in categories:
        new_stocks.extend(categories[cat])
for cat in categories:
    if cat not in cat_order:
        new_stocks.extend(categories[cat])

for i, s in enumerate(new_stocks):
    s['id'] = i + 1

data['stocks'] = new_stocks

from collections import Counter
cc = Counter(s['category'] for s in new_stocks)
mc = Counter(s['market'] for s in new_stocks)
sc = []
for cat in cat_order:
    if cat in cc:
        sc.append({"name": cat, "count": cc[cat]})

data['stats'] = {"categories": sc, "totalMarkets": dict(mc), "totalStocks": len(new_stocks)}
data['meta']['updated'] = '2026-07-30'

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"OK: {len(new_stocks)} stocks")
for c in sc:
    print(f"  {c['name']}: {c['count']}")

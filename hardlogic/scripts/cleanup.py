import json

with open(r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Renumber all IDs
for i, s in enumerate(data['stocks']):
    s['id'] = i + 1

# Fix stats
from collections import Counter
cat_counts = Counter(s['category'] for s in data['stocks'])
market_counts = Counter(s['market'] for s in data['stocks'])

category_order = [
    "PCB产业链", "电子特气", "被动元件", "光互连", "半导体上游",
    "半导体设备零部件", "先进封装", "制造与存储", "功率半导体", "医疗材料", "小金属(AI金属)"
]

stats_categories = []
for cat in category_order:
    if cat in cat_counts:
        stats_categories.append({"name": cat, "count": cat_counts[cat]})

data['stats'] = {
    "categories": stats_categories,
    "totalMarkets": dict(market_counts),
    "totalStocks": len(data['stocks'])
}

data['meta']['updated'] = '2026-07-30'

with open(r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done. Total: {len(data['stocks'])} stocks")
for c in stats_categories:
    print(f"  {c['name']}: {c['count']}")
print(f"Markets: {dict(market_counts)}")

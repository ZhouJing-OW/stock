"""Re-sort hardlogic.json: sort stocks within each category by score desc, re-id, update stats."""
import json
from datetime import datetime, date

DATA_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group stocks by category preserving original category order
cat_order = []
cat_stocks = {}
for s in data['stocks']:
    c = s['category']
    if c not in cat_stocks:
        cat_stocks[c] = []
        cat_order.append(c)
    cat_stocks[c].append(s)

# Sort within each category by score descending, then by name for ties
for c in cat_order:
    cat_stocks[c].sort(key=lambda s: (-s.get('score', 0), s['name']))

# Flatten and re-assign IDs
new_id = 1
new_stocks = []
for c in cat_order:
    for s in cat_stocks[c]:
        s['id'] = new_id
        new_id += 1
        new_stocks.append(s)

data['stocks'] = new_stocks

# Update stats
data['meta']['updated'] = '2026-07-06'

# Category counts
cat_counts = {}
for s in new_stocks:
    c = s['category']
    cat_counts[c] = cat_counts.get(c, 0) + 1

data['stats']['categories'] = [{'name': c, 'count': cat_counts[c]} for c in cat_order]

# Market counts
market_counts = {}
for s in new_stocks:
    m = s['market']
    market_counts[m] = market_counts.get(m, 0) + 1
data['stats']['totalMarkets'] = market_counts

# Average concept age
today = date.today()
ages = []
recent_14d = 0
for s in new_stocks:
    try:
        added = datetime.strptime(s.get('conceptAdded', ''), '%Y-%m-%d').date()
        age = (today - added).days
        ages.append(age)
        if age <= 14:
            recent_14d += 1
    except:
        pass

if ages:
    data['stats']['avgConceptAgeDays'] = round(sum(ages) / len(ages), 1)
data['stats']['recentConcepts14d'] = recent_14d

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Print summary
print(f"Total stocks: {len(new_stocks)}")
print(f"Categories: {len(cat_order)}")
for c in cat_order:
    names = [s['name'] for s in cat_stocks[c]]
    scores = [f"{s['name']}({s.get('score','?')})" for s in cat_stocks[c]]
    print(f"  {c} ({cat_counts[c]}): {', '.join(scores)}")
print(f"Avg concept age: {data['stats']['avgConceptAgeDays']}d")
print(f"Recent 14d: {recent_14d}")
print("Done!")

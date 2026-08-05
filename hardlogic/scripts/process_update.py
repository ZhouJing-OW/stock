import json
from collections import Counter

# Read
with open(r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# === 1. Fix 圣泉集团 conceptSourceUrl ===
for s in data['stocks']:
    if s['code'] == '605589':
        s['conceptSourceUrl'] = 'https://news.chemnet.com/toutiao/detail-72810.html'
        print(f'Fixed: 圣泉集团 conceptSourceUrl -> 72810')

# === 2. Add reinforcement for 国瓷材料 (氧化锆涨价) ===
for s in data['stocks']:
    if s['code'] == '300285':
        reins = s.setdefault('conceptReinforcements', [])
        reins.append({
            'date': '2026-07-21',
            'desc': '国瓷材料宣布7月27日起上调氧化锆粉体销售价格10%-40%；氧化钇出口管制→海外氧化锆龙头(东曹/第一稀元素化学)原料紧缺→全球高端氧化锆数千吨级缺口；MLCC粉体+氧化锆双受益形成三线共振',
            'source': 'https://www.cls.cn/detail/2431559'
        })
        print(f'Added: 国瓷材料 氧化锆涨价 reinforcement')

# === 3. Trim reinforcements to max 3, fold important events into coreLogic ===
IMPORTANT_KW = ['涨价', '认证通过', '量产', '停产', '突破', '大单', '签约', '断供', '禁售', '出口管制', '预增', '暴增', '翻倍', '翻番', '缺口', '归零']

trimmed_count = 0
folded_count = 0
for s in data['stocks']:
    reins = s.get('conceptReinforcements', [])
    if len(reins) <= 3:
        continue
    # Sort by date desc
    reins.sort(key=lambda x: x['date'], reverse=True)
    kept = reins[:3]
    removed = reins[3:]
    # Fold important events into coreLogic
    events_to_fold = []
    for r in removed:
        if any(kw in r['desc'] for kw in IMPORTANT_KW):
            events_to_fold.append(r['desc'])
    if events_to_fold:
        s['coreLogic'] = s['coreLogic'] + '。' + '。'.join(events_to_fold)
        folded_count += len(events_to_fold)
    s['conceptReinforcements'] = kept
    trimmed_count += 1
    print(f'Trimmed: {s["name"]}({s["code"]}) {len(reins)}->3, folded {len(events_to_fold)} events')

if trimmed_count == 0:
    print('No stocks needed reinforcement trimming')

# === 4. Sort within each category by score desc, renumber IDs ===
# Preserve category order from original
cat_order = []
for s in data['stocks']:
    if s['category'] not in cat_order:
        cat_order.append(s['category'])

new_stocks = []
for cat in cat_order:
    cat_stocks = [s for s in data['stocks'] if s['category'] == cat]
    cat_stocks.sort(key=lambda x: -x.get('score', 0))
    new_stocks.extend(cat_stocks)

for i, s in enumerate(new_stocks, 1):
    s['id'] = i

data['stocks'] = new_stocks

# === 5. Update stats ===
cat_counts = Counter(s['category'] for s in data['stocks'])
market_counts = Counter(s['market'] for s in data['stocks'])
data['stats'] = {
    'categories': [{'name': cat, 'count': cat_counts[cat]} for cat in cat_order],
    'totalMarkets': dict(market_counts),
    'totalStocks': len(data['stocks'])
}

# === 6. Update meta ===
data['meta']['updated'] = '2026-07-21'

# Write back
with open(r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone! {len(data["stocks"])} stocks, updated={data["meta"]["updated"]}')
# Print new ID mapping for key stocks
for s in data['stocks']:
    if s['code'] in ['002916','605589','300285','688498','000636','000962','300054']:
        print(f'  id={s["id"]} {s["name"]}({s["code"]}) score={s["score"]} category={s["category"]}')

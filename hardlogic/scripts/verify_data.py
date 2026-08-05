import json
with open('data/top20_hardlogic.json','r',encoding='utf-8') as f:
    d = json.load(f)
print('Valid JSON. Stocks:', len(d['stocks']))
for s in d['stocks']:
    print(f"  #{s['id']:2d} {s['name']:8s} {s['code']} {s['category']:8s} score={s['score']}")
print()
print('Stats:', json.dumps(d['stats'], ensure_ascii=False, indent=2))
print('Updated:', d['meta']['updated'])

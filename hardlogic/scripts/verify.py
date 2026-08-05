import json
with open(r'E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data['stocks']:
    if s['name'] in ['福晶科技', '洁美科技', '雅克科技']:
        print(f"ID={s['id']} {s['name']}({s['code']}) cat={s['category']} score={s['score']}")
        print(f"  conceptAdded={s.get('conceptAdded')}")
        rf = s.get('conceptReinforcements', [])
        print(f"  reinforcements={len(rf)}条")
        if rf:
            for r in rf:
                print(f"    {r['date']}: {r['desc'][:70]}...")

print(f"\nTotal: {len(data['stocks'])} stocks")
print(f"Updated: {data['meta']['updated']}")

# Check top 3 in each category
cats = {}
for s in data['stocks']:
    c = s['category']
    cats.setdefault(c, []).append(s)
for c, items in cats.items():
    print(f"\n{c} ({len(items)}只):")
    for s in items[:3]:
        print(f"  #{s['id']} {s['name']} score={s['score']}")

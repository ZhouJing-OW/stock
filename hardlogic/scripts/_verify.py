import json
with open(r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for s in data["stocks"][:5]:
    print(f'  #{s["id"]} {s["name"]}({s["code"]}) [{s["category"]}] score={s["score"]}')
print("...")
for s in data["stocks"]:
    if s["code"] == "605589":
        print(f'NEW #{s["id"]} {s["name"]}({s["code"]}) [{s["category"]}/{s["subCategory"]}] score={s["score"]}')
    if s["code"] == "601208":
        print(f'UPD #{s["id"]} {s["name"]}({s["code"]}) score={s["score"]}')
print(f"Total: {len(data['stocks'])} stocks, updated={data['meta']['updated']}")

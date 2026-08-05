import json
data = json.load(open("../data/hardlogic.json", "r", encoding="utf-8"))
codes = [s["code"] for s in data["stocks"]]
with open("top20_codes.txt", "w") as f:
    f.write("\n".join(codes))
print("\n".join(codes))
print(f"\n共 {len(codes)} 只")

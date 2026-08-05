import json

PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with open(PATH, "r", encoding="utf-8") as f:
    raw = f.read()

print(f"File size: {len(raw)} chars")
print(f"First 200 chars: {raw[:200]}")
print(f"Last 200 chars: {raw[-200:]}")

try:
    d = json.loads(raw)
    print(f"Valid JSON. Stocks: {len(d['stocks'])}")
except json.JSONDecodeError as e:
    print(f"INVALID JSON: {e}")
    print(f"Context: {raw[max(0,e.pos-50):e.pos+50]}")

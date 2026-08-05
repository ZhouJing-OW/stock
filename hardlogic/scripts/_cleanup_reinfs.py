import json
from datetime import datetime

path = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned = 0
merged = 0

for s in data["stocks"]:
    reinfs = s.get("conceptReinforcements", [])
    if not reinfs:
        continue

    # 按日期排序
    reinfs.sort(key=lambda r: r["date"])
    total = len(reinfs)

    if total <= 3:
        continue

    # 保留最近3条
    keep = reinfs[-3:]
    drop = reinfs[:-3]

    # 从丢弃的增强中提取关键信息
    key_events = []
    for r in drop:
        desc = r["desc"]
        # 筛出重要的：涨价/认证/产能/突破/停产等关键词
        if any(kw in desc for kw in ["涨价", "认证通过", "量产", "停产", "突破", "创新高", "缺口", "暴增", "锁定产能", "断供", "入选"]):
            key_events.append(desc)

    # 合并到 coreLogic 末尾（去重）
    if key_events:
        existing = s["coreLogic"]
        # 简单去重
        new_points = [p for p in key_events if p[:15] not in existing]
        if new_points:
            append = "。".join(new_points[:3])  # 最多补充3条重要事件
            s["coreLogic"] = existing + "。" + append
            merged += 1

    s["conceptReinforcements"] = keep
    cleaned += total - len(keep)

data["meta"]["updated"] = "2026-07-07"

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 删除 {cleaned} 条冗余增强，{merged} 只标的核心理念已补充")
for s in data["stocks"]:
    n = len(s.get("conceptReinforcements", []))
    if n > 0:
        print(f"  {s['name']}: {n}条增强")

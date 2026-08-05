# -*- coding: utf-8 -*-
"""收尾：统一所有 conceptReinforcements 按日期降序。"""
import json, io

PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"
with io.open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for s in data["stocks"]:
    rs = s.get("conceptReinforcements", [])
    if rs:
        rs.sort(key=lambda r: r["date"], reverse=True)
        s["conceptReinforcements"] = rs

with io.open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("sorted OK")

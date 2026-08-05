# -*- coding: utf-8 -*-
"""Compact inventory dump of hardlogic.json for editing decisions."""
import json, io, sys

PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"
with io.open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print("meta.updated =", data["meta"]["updated"])
print("totalStocks =", data["stats"]["totalStocks"])
print("=" * 100)
for s in data["stocks"]:
    re_dates = [r["date"] for r in s.get("conceptReinforcements", [])]
    print(f"id={s['id']:>2} | {s['category']:<16} | {s['subCategory']:<22} | {s['code']} {s['name']:<6} | score={s['score']:<4} | added={s['conceptAdded']} | reinf={re_dates}")

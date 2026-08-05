# -*- coding: utf-8 -*-
import json
from pathlib import Path
DATA = Path(r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json")
data = json.loads(DATA.read_text(encoding="utf-8"))
stocks = data["stocks"]
print("total:", len(stocks))
codes = [s["code"] for s in stocks]
# 检查重复
from collections import Counter
dup = [c for c, n in Counter(codes).items() if n > 1]
print("dup codes:", dup)
# 检查兆易创新
has_zy = any(s["name"] == "兆易创新" for s in stocks)
print("has 兆易创新:", has_zy)
# 分类统计
cat = {}
for s in stocks:
    cat[s["category"]] = cat.get(s["category"], 0) + 1
print("cats:", cat)
# 列出制造与存储
print("制造与存储:", [s["name"] for s in stocks if s["category"] == "制造与存储"])
# 检查 id 连续性
ids = [s["id"] for s in stocks]
print("id range:", min(ids), max(ids), "unique:", len(set(ids)))
# 检查新增标的
for s in stocks:
    if s["code"] in ("300480", "688170"):
        print("NEW:", s["name"], s["code"], "cat:", s["category"], "score:", s["score"], "id:", s["id"])

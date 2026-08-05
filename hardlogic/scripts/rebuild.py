#!/usr/bin/env python3
"""
重建 hardlogic.json - 从原始数据重建完整文件
使用之前读取到的完整JSON内容
"""
import json

# 读取当前损坏的文件获取meta
current = None
try:
    with open(r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json", "r", encoding="utf-8") as f:
        current = json.load(f)
except:
    pass

# 硬编码重建: 使用write工具直接写入完整的最终JSON
# 由于文件太大，使用此脚本作为最后手段
print("Attempting rebuild from script...")
print("Current meta:", current["meta"] if current else "N/A")
print("Current stocks:", len(current.get("stocks", [])) if current else "N/A")

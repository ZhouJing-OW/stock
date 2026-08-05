import os

wf_path = r"E:\Hanako_WorkSpace\workflows\hardlogic_update.js"
with open(wf_path, "r", encoding="utf-8") as f:
    c = f.read()

# 处理转义双反斜杠版本 (JS 字符串字面量)
c = c.replace(r"E:\\Hanako_WorkSpace\\硬逻辑看板", r"E:\\Hanako_WorkSpace\\研报\\个股研究\\hardlogic")
# 处理单反斜杠版本
c = c.replace(r"E:\Hanako_WorkSpace\硬逻辑看板", r"E:\Hanako_WorkSpace\研报\个股研究\hardlogic")

with open(wf_path, "w", encoding="utf-8") as f:
    f.write(c)

# 验证
with open(wf_path, "r", encoding="utf-8") as f:
    c = f.read()
remaining = c.count("硬逻辑看板")
print(f"workflow updated, remaining 硬逻辑看板 references: {remaining}")

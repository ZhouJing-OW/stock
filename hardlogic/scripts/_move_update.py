import os

# 1. 更新 workflow
wf_path = r"E:\Hanako_WorkSpace\workflows\hardlogic_update.js"
with open(wf_path, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(r"E:\Hanako_WorkSpace\硬逻辑看板", r"E:\Hanako_WorkSpace\研报\个股研究\hardlogic")
with open(wf_path, "w", encoding="utf-8") as f:
    f.write(c)
print("workflow updated")

# 2. 更新 SKILL.md
skill_path = r"E:\Hanako_WorkSpace\研报\个股研究\hardlogic\SKILL.md"
if os.path.exists(skill_path):
    with open(skill_path, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace(r"E:\Hanako_WorkSpace\硬逻辑看板", r"E:\Hanako_WorkSpace\研报\个股研究\hardlogic")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(c)
    print("SKILL.md updated")

# 3. 更新 fetch_news.py 输出路径
fetch_path = r"E:\Hanako_WorkSpace\Tool\china-finance-rss-main\fetch_news.py"
with open(fetch_path, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(r"E:\Hanako_WorkSpace\硬逻辑看板", r"E:\Hanako_WorkSpace\研报\个股研究\hardlogic")
with open(fetch_path, "w", encoding="utf-8") as f:
    f.write(c)
print("fetch_news.py updated")

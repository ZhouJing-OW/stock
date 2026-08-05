import json

path = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

events = {
    "002916": {
        "date": "2026-07-21",
        "desc": "PCB板块午后爆发，深南电路涨超5%；生益电子H1净利预增432-471%；英伟达Rubin放量驱动30层正交背板强制切换M9级CCL"
    },
    "603256": {
        "date": "2026-07-21",
        "desc": "电子布年内五轮涨价，均价较去年低点翻倍；织机缺口2027年扩大至10.6%，高端布产能死锁"
    },
    "688347": {
        "date": "2026-07-21",
        "desc": "科创50涨10.73%，华虹宏力20CM涨停；央企近600亿增持+证监会明确维稳"
    },
    "002371": {
        "date": "2026-07-21",
        "desc": "科创50涨10.73%，北方华创10CM涨停；半导体设备板块全线爆发"
    },
    "301217": {
        "date": "2026-07-21",
        "desc": "铜冠铜箔全品类加工费二次上调，HVLP4涨至20万/吨(+11%)；2026-2027供需缺口1500-2500吨"
    },
    "688008": {
        "date": "2026-07-21",
        "desc": "长鑫科技申购，预计募资579亿；存储芯片国产替代加速，DDR5接口需求预期上修"
    },
}

for s in data["stocks"]:
    code = s["code"]
    if code in events:
        s.setdefault("conceptReinforcements", []).append(events[code])

# 限3条
for s in data["stocks"]:
    r = s.get("conceptReinforcements", [])
    if len(r) > 3:
        r.sort(key=lambda x: x["date"])
        s["conceptReinforcements"] = r[-3:]

data["meta"]["updated"] = "2026-07-21"

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已追加6只标的的增强事件")

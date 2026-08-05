#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""硬逻辑看板 2026-08-02 每日更新：编辑脚本
- 新增：光力科技(300480)、德龙激光(688170)（日本8/1先进封装设备管制受益）
- 追加：中微公司/盛美上海 8/1 日本管制 reinforcement
- 重排 id、更新 stats、meta.updated
"""
import json
from collections import OrderedDict
from pathlib import Path

DATA = Path(r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json")
data = json.loads(DATA.read_text(encoding="utf-8"))
stocks = data["stocks"]

# ---------- 1. 新增标的 ----------
new_gl = {
    "category": "先进封装",
    "subCategory": "晶圆划切设备(国产唯一)",
    "code": "300480",
    "name": "光力科技",
    "market": "创业板",
    "coreLogic": "国内唯一量产高端12英寸全自动划片机厂商（全球仅DISCO/东京精密/光力三家），机械划片机国产市占率第一、8230系列获河南省首台套认定；激光隐切机/研磨机客户端验证中，研磨抛光一体机研发中；整机+空气主轴+金刚石刀片全自研闭环。日本8/1第三轮对华半导体管制首次纳入后道先进封装设备（划片机/研磨机/激光隐切/TSV等20大类物项，对华逐案审批、驳回率超79%实质断供），DISCO垄断国内高端划片机75%+份额直接受限。2026年以来国产半导体业务持续满产。",
    "supplyDemand": "12英寸高端划片机国产化率不足15%，激光隐切几乎0到1突破。DISCO垄断全球70%+减薄机/划片机市场。日本管制生效后国内封测厂/存储厂只能加速导入国产设备。",
    "priceSignal": "2026年以来国产半导体业务持续满产（7/30互动平台）；订单兑现预计Q4至明年上半年逐步体现",
    "catalyst": "日本8/1先进封装设备管制正式生效（5/29新规）；DISCO对华实质断供；划片机+研磨机+激光设备全覆盖最纯正替代标的",
    "conceptAdded": "2026-07-15",
    "conceptSource": "日本8/1管制先进封装设备→光力科技国内唯一高端划片机厂商最纯正替代标的",
    "conceptSourceUrl": "https://www.sanhuba.cn/post/dd-e7-32902.html",
    "riskNote": "划片机市场规模相对有限（全球约60亿人民币）；激光隐切/研磨机尚处验证阶段，订单兑现需Q4起；公司另有物联网安全监控主业拖累估值",
    "tags": ["日本断供", "国产替代", "DISCO替代", "后道设备", "划片机"],
    "score": 8.0,
    "conceptReinforcements": [
        {
            "date": "2026-07-30",
            "desc": "互动平台确认：今年以来国产半导体业务持续满产；公司加快二期产能扩建（2027年一季度完工）",
            "source": "https://finance.jrj.com.cn/2026/07/30152057953889.shtml"
        }
    ]
}

new_dl = {
    "category": "先进封装",
    "subCategory": "激光隐切设备(国产独家)",
    "code": "688170",
    "name": "德龙激光",
    "market": "科创板",
    "coreLogic": "国内唯一实现硅晶圆激光隐切(SDBG)量产替代的厂商，可加工35-85μm超薄晶圆，已获小批量订单。激光隐切替代机械划片是存储芯片超薄化、3D堆叠趋势下的工艺升级方向。DISCO激光隐切/裂片设备被日本8/1管制纳入清单（DISCO垄断国内高端市场75%+份额），国内存储厂/先进封装厂替代需求直接涌向德龙。",
    "supplyDemand": "激光隐切国产化率接近0（0到1突破），DISCO垄断国内高端75%+。日本8/1管制生效后唯一国产量产替代厂商直接受益。",
    "priceSignal": "硅晶圆激光隐切设备已获小批量订单；存储超薄化趋势拉动需求",
    "catalyst": "日本8/1先进封装设备管制生效；DISCO激光隐切对华实质断供；存储芯片超薄化+3D堆叠工艺升级",
    "conceptAdded": "2026-07-15",
    "conceptSource": "日本8/1管制先进封装设备→德龙激光激光隐切国产独家突破",
    "conceptSourceUrl": "https://www.sanhuba.cn/post/dd-e7-32902.html",
    "riskNote": "激光隐切设备收入规模小，业绩弹性有限；处于批量验证导入初期，订单兑现节奏不确定",
    "tags": ["日本断供", "国产替代", "激光隐切", "后道设备", "存储超薄化"],
    "score": 7.3,
    "conceptReinforcements": []
}

stocks.append(new_gl)
stocks.append(new_dl)

# ---------- 2. 追加 reinforcement：中微公司 / 盛美上海 ----------
jp_event_zw = {
    "date": "2026-08-01",
    "desc": "日本8/1第三轮对华半导体管制正式生效，首次纳入后道先进封装设备（TSV硅通孔/混合键合/微凸点电镀等20大类物项，逐案审批驳回率超79%实质断供）；中微深硅刻蚀设备为TSV核心工艺设备，技术壁垒极高已进台积电/中芯供应链",
    "source": "https://www.sanhuba.cn/post/dd-e7-32902.html"
}
jp_event_sm = {
    "date": "2026-08-01",
    "desc": "日本8/1对华管制首次纳入先进封装设备（混合键合/TSV等）；盛美为国内唯一进入混合键合验证阶段企业，先进封装清洗+电镀设备已批量出货头部封测厂，国产替代窗口扩大",
    "source": "https://www.sanhuba.cn/post/dd-e7-32902.html"
}

for s in stocks:
    if s["code"] == "688012" and s["name"] == "中微公司":
        s["conceptReinforcements"].append(jp_event_zw)
    if s["code"] == "688082" and s["name"] == "盛美上海":
        s["conceptReinforcements"].append(jp_event_sm)

# ---------- 3. 按 category 内 score 降序重排，刷新 id ----------
cat_order = ["PCB产业链", "电子特气", "被动元件", "光互连", "半导体上游",
             "芯片设计(FPGA)", "半导体设备零部件", "先进封装",
             "制造与存储", "功率半导体", "医疗材料", "小金属(AI金属)"]

def cat_key(cat):
    return cat_order.index(cat) if cat in cat_order else 99

stocks.sort(key=lambda s: (-cat_key(s["category"]), -s["score"]))
# 按 category 分组后组内再按 score 降序（保持组间顺序稳定）
grouped = OrderedDict()
for s in stocks:
    grouped.setdefault(s["category"], []).append(s)

ordered = []
for cat in cat_order:
    if cat in grouped:
        ordered.extend(sorted(grouped[cat], key=lambda x: -x["score"]))
for cat in grouped:
    if cat not in cat_order:
        ordered.extend(sorted(grouped[cat], key=lambda x: -x["score"]))

for i, s in enumerate(ordered, 1):
    s["id"] = i

data["stocks"] = ordered

# ---------- 4. 更新 stats ----------
cats = []
cat_counts = OrderedDict()
for s in ordered:
    cat_counts[s["category"]] = cat_counts.get(s["category"], 0) + 1
for c, n in cat_counts.items():
    cats.append({"name": c, "count": n})

market_counts = {}
for s in ordered:
    market_counts[s["market"]] = market_counts.get(s["market"], 0) + 1

data["stats"] = {
    "categories": cats,
    "totalMarkets": market_counts,
    "totalStocks": len(ordered)
}

# ---------- 5. meta ----------
data["meta"]["updated"] = "2026-08-02"

DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("OK total:", len(ordered))
for c in cat_counts:
    print(" ", c, cat_counts[c])

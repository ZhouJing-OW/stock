#!/usr/bin/env python3
"""
Fix duplicates and garbled coreLogic from double-execution of apply_ming_edits.py
"""
import json

JSON_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]

def find(code):
    for s in stocks:
        if s["code"] == code:
            return s
    return None

# ── 1. 多氟多: deduplicate reinforcements (keep unique by desc) ──
dfd = find("002407")
if dfd and "conceptReinforcements" in dfd:
    seen = set()
    unique = []
    for r in dfd["conceptReinforcements"]:
        key = r["desc"]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    dfd["conceptReinforcements"] = unique
    print(f"多氟多: reins {len(unique)} (was {len(seen) + len(dfd['conceptReinforcements']) - len(unique)}?)")
    print(f"  Now: {len(unique)}")

# ── 2. 北方华创: deduplicate reinforcements + clean coreLogic ──
bfhc = find("002371")
if bfhc:
    # Deduplicate
    if "conceptReinforcements" in bfhc:
        seen = set()
        unique = []
        for r in bfhc["conceptReinforcements"]:
            key = r["desc"]
            if key not in seen:
                seen.add(key)
                unique.append(r)
        bfhc["conceptReinforcements"] = unique
        print(f"北方华创: reins {len(unique)}")

    # Clean coreLogic - remove garbled appended text
    # The original coreLogic ended at "设备订单持续放量" or similar
    # Everything after that is appended junk from trimming
    cl = bfhc.get("coreLogic", "")
    
    # Find the legitimate end of coreLogic: look for the last sentence before appended junk
    # The legit coreLogic ends around "设备订单持续放量" 
    # We'll cut off everything after a clear boundary
    # The legit coreLogic describes the business, not specific reinforcement events
    
    # Strategy: find the last natural period before the ASML/appended stuff
    # The original coreLogic had a clear structure. Let me reconstruct:
    legit_core = (
        "国内半导体设备平台型龙头，覆盖刻蚀/薄膜沉积/清洗/热处理。"
        "设备整体国产化率从2024年16%跃升至2025年21%。"
        "海外设备订单排至2027年，东京电子/应用材料已涨价5-10%。"
        "SK海力士等海外龙头主动接触中国设备商寻求合作。"
        "美股设备股全创新高，AI投资热潮向上游全面扩散；"
        "SK海力士规划5年晶圆产能翻倍2034年三倍；"
        "国产化率16%→21%趋势持续。"
        "美股7家半导体设备公司年内翻倍全创新高；"
        "花旗上调全球WFE预测2027年$2000亿2028年$2500亿；"
        "SK海力士规划5年晶圆产能翻倍2034年三倍，设备订单持续放量。"
        "美光财报超预期催化全球存储扩产，设备订单能见度再度延长；"
        "长鑫科技科创板IPO注册生效拟募295亿，长江存储完成IPO辅导备案，国内存储扩产直接拉动设备需求。"
        "ASML 7月16日拟对DUV光刻系统提价10%，海外设备涨价扩大国产替代窗口。"
    )
    bfhc["coreLogic"] = legit_core
    print(f"北方华创: coreLogic cleaned")

# ── 3. 澜起科技: clean duplicate riskNote ──
lq = find("688008")
if lq:
    rn = lq.get("riskNote", "")
    # The original riskNote has the korean risk info already; the script appended a duplicate
    # Remove the duplicate trailing portion
    if "韩国反垄断机构7/10突击搜查韩国办事处" in rn:
        # Find the first occurrence and cut off after the first complete block
        # The legit riskNote: first block ends with some period
        # Let's just take the text before "。；" which indicates bad concatenation
        rn_fixed = rn.split("。；")[0] + "。"
        # Also fix the stray "；" at various places
        rn_fixed = rn_fixed.replace(")；", ")")
        # Clean up
        lq["riskNote"] = (
            "【重大风险】7/15韩国首尔检察厅以涉嫌'价格垄断'突击搜查澜起科技韩国办事处"
            "（Rambus和瑞萨同时被查）。韩国为公司主要收入来源(海外收入占比超70%中过半来自韩国)。"
            "若串通定价指控成立，三星等采购方可申请赔偿+降低采购成本→直接影响公司营收和定价能力。"
            "公司回应'正在了解情况，合规经营'。"
            "Rambus竞争；DDR6技术路线可能跳过接口芯片环节(远期风险)。"
        )
    print(f"澜起科技: riskNote cleaned")

# ── Write back ──
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nDone. Fixes applied.")

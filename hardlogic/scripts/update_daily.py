"""
每日更新 hardlogic.json v2: 修复巨化股份重复 + 增强现有条目 + 修剪conceptReinforcements + 重排
"""
import json
from collections import OrderedDict

DATA_PATH = r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"
TODAY = "2026-07-16"

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    stocks = data["stocks"]

    # ── 0. 去除重复的巨化股份条目(保留原始PFA条目,删除液冷散热新条目) ──
    jh_indices = [i for i, s in enumerate(stocks) if s.get("code") == "600160"]
    if len(jh_indices) >= 2:
        # 保留第一个(原始PFA条目 score 8.5), 删除后面的
        for idx in sorted(jh_indices[1:], reverse=True):
            removed = stocks.pop(idx)
            print(f"🗑 删除重复条目: {removed['code']} {removed['name']} (category={removed['category']})")
    
    # ── 0b. 增强现有巨化股份条目: 加入氟化液/液冷角度 ──
    for s in stocks:
        if s.get("code") == "600160":
            # 更新 subCategory 体现双逻辑
            s["subCategory"] = "超纯PFA+电子氟化液(液冷)"
            # 在 coreLogic 末尾追加液冷逻辑
            liquid_logic = "3M 2025年底全面退出PFAS制造→全球70%电子氟化液市场留下百亿缺口，巨芯冷却液5000吨规划(一期1000吨已投产)已合作阿里云/华为等头部云厂商。"
            if "巨芯冷却液" not in s["coreLogic"]:
                s["coreLogic"] = s["coreLogic"].rstrip("。") + "。" + liquid_logic
            # 追加液冷相关catalyst
            if "3M退出" not in s["catalyst"]:
                s["catalyst"] += "；3M退出氟化液→百亿缺口+甘肃项目Q3试车新增5000吨氟化液"
            # 追加液冷相关tag
            if "液冷氟化液" not in s["tags"]:
                if len(s["tags"]) >= 5:
                    s["tags"] = s["tags"][:4]
                s["tags"].append("液冷氟化液")
            # 追加液冷概念增强事件
            cr = s.get("conceptReinforcements", [])
            cr.append({
                "date": "2026-07-16",
                "desc": "3M退出氟化液百亿缺口逻辑纳入看板：巨芯冷却液5000吨规划(一期1000吨投产运行良好)+甘肃项目Q3试车新增5000吨+已合作阿里云/华为；电子氟化液+PFA双逻辑升级",
                "source": "https://www.163.com/dy/article/KSGI6OIN05568W0A.html"
            })
            # 保持最多3条
            if len(cr) > 3:
                cr_sorted = sorted(cr, key=lambda x: x.get("date", ""), reverse=True)
                s["conceptReinforcements"] = cr_sorted[:3]
            else:
                s["conceptReinforcements"] = cr
            print(f"🔧 增强现有条目: {s['code']} {s['name']} → subCategory更新+液冷逻辑追加")
            break

    # ── 1. 修剪 conceptReinforcements：只保留最近3条 ──
    for s in stocks:
        cr = s.get("conceptReinforcements", [])
        if len(cr) > 3:
            cr_sorted = sorted(cr, key=lambda x: x.get("date", "0000-00-00"), reverse=True)
            removed = cr_sorted[3:]
            important_keywords = ["涨价", "认证通过", "量产", "停产", "突破", "断供", "IPO", "缺口"]
            merged_events = []
            for r in removed:
                desc = r.get("desc", "")
                for kw in important_keywords:
                    if kw in desc:
                        merged_events.append(desc)
                        break
            if merged_events:
                for ev in merged_events[:2]:
                    short = ev.split("；")[0].split(";")[0]
                    if short not in s["coreLogic"]:
                        s["coreLogic"] = s["coreLogic"].rstrip("。") + "。" + short + "。"
            s["conceptReinforcements"] = cr_sorted[:3]

    # ── 2. 按category分组，组内按score降序排列，刷新id ──
    category_order = [
        "PCB产业链", "电子特气", "被动元件", "光互连",
        "半导体上游", "半导体设备零部件", "先进封装", "制造与存储",
        "功率半导体", "医疗材料", "小金属(AI金属)"
    ]
    
    groups = {}
    for s in stocks:
        cat = s.get("category", "其他")
        groups.setdefault(cat, []).append(s)
    
    for cat in groups:
        groups[cat].sort(key=lambda x: x.get("score", 0), reverse=True)
    
    new_stocks_list = []
    for cat in category_order:
        if cat in groups:
            new_stocks_list.extend(groups[cat])
    for cat in groups:
        if cat not in category_order:
            new_stocks_list.extend(groups[cat])
    
    for i, s in enumerate(new_stocks_list, 1):
        s["id"] = i
    
    data["stocks"] = new_stocks_list

    # ── 3. 更新 stats ──
    cat_counts = {}
    market_counts = {}
    for s in new_stocks_list:
        cat = s["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        mkt = s.get("market", "主板")
        market_counts[mkt] = market_counts.get(mkt, 0) + 1
    
    data["stats"] = {
        "categories": [{"name": k, "count": v} for k, v in cat_counts.items()],
        "totalMarkets": market_counts,
        "totalStocks": len(new_stocks_list)
    }

    data["meta"]["updated"] = TODAY

    # ── 4. 写回 ──
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 更新完成: {len(new_stocks_list)}只标的, {len(cat_counts)}个分类")
    print(f"📅 meta.updated = {TODAY}")
    print(f"📊 分类统计: {json.dumps(cat_counts, ensure_ascii=False)}")

if __name__ == "__main__":
    main()

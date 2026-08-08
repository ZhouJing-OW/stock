#!/usr/bin/env python3
"""
今日要闻看板生成器
读取 RSS 快讯缓存 (news_feeds.txt)，按价值打分筛选最有价值的新闻，生成 HTML 看板。

价值评分规则（贴合硬逻辑偏好）：
- 供给硬约束：停产/断供/涨价/缺货/扩产受限 → +3
- 供应链武器化：出口管制/稀土/制裁/禁令 → +3
- 国产替代：认证/量产/突破/订单 → +2
- 海外映射：美股/日股/韩股新高/巨头动作 → +2
- AI主线：AI/算力/芯片/半导体/HBM/光模块 → +1
- 业绩兑现：业绩预增/扭亏/订单暴增 → +1
- 政策利好：政策/规划/资金 → +1
- 一般市场信息：指数涨跌/成交额 → -2（降权）

输出: E:\\Hanako_WorkSpace\\盘面观察\\daily_news.html
"""

import re
import os
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent  # 个股研究/hardlogic
NEWS_FILE = PROJECT_DIR / "data" / "news_feeds.txt"
OUTPUT_FILE = Path(r"E:\Hanako_WorkSpace\盘面观察\daily_news.html")

# ===================== 评分规则 =====================
# 三层影响权重：宏观层 > 行业层 > 公司层
# 每条新闻取最高命中层级的得分，同层多信号可叠加
KEYWORDS = {
    # ── 宏观层 (±5)：影响全市场 ──
    "macro_money": ["美联储", "央行", "加息", "降息", "利率", "非农", "CPI", "通胀", "GDP", "国债", "美债"],
    "macro_geo": ["战争", "导弹", "袭击", "军事", "制裁", "冲突", "霍尔木兹", "原油", "石油", "地缘"],
    "macro_trade": ["关税", "贸易战", "出口管制", "两用物项", "禁止出口", "限制出口", "商务部"],
    "macro_policy": ["国务院", "发改委", "工信部", "政治局", "十四五", "十五五", "规划", "万亿", "美联储", "主席表示"],

    # ── 行业层 (±4)：影响整个行业 ──
    "ind_supply": ["停产", "断供", "涨价", "缺货", "供不应求", "短缺", "供应中断", "产能瓶颈", "满载", "扩产受限", "缺口"],
    "ind_resource": ["稀土", "氧化镝", "氧化铽", "氧化钇", "氧化铒", "锗", "镓", "锑", "钨", "钼", "铟", "铪", "锆", "钽"],
    "ind_capex": ["投资", "扩产", "新建", "产能建设", "开工", "项目投产", "资本开支", "IPO", "上市"],
    "ind_std": ["标准", "大会", "峰会", "白皮书", "路线图", "政策发布", "实施意见", "认证体系"],
    "ind_chain": ["订单排至", "抢单", "锁产能", "长协", "长约", "采购协议", "供货"],

    # ── 公司层 (±2)：影响个别公司 ──
    "comp_earn": ["净利润", "业绩预增", "扭亏", "营收增长", "净利增长", "半年报", "季报", "财报"],
    "comp_deal": ["收购", "受让", "中标", "订单", "签约", "合作", "定增", "回购", "增资", "并购"],
    "comp_mv": ["增持", "减持", "股权", "解禁", "质押", "内幕交易"],
    "comp_risk": ["立案", "处罚", "违规", "警示", "罚款", "停产整改", "退市"],

    # ── 主线强化 (+2)：AI/半导体/硬科技 ──
    "main_ai": ["AI", "算力", "芯片", "半导体", "HBM", "光模块", "GPU", "数据中心", "存储", "DRAM", "NAND", "先进封装", "硅片", "光刻", "晶圆"],
    "main_overseas": ["英伟达", "台积电", "三星", "海力士", "美光", "AMD", "英特尔", "新高", "美股", "日股", "韩股"],

    # ── 杂讯 (-2)：一般市场噪音 ──
    "noise": ["指数", "成交额", "收盘", "涨跌", "沪指", "深成指", "创业板指", "涨停分析", "午评", "收评", "汇率报", "点位"],
}

# 层级权重（取最高命中层的基准分）
LAYER_WEIGHT = {
    "macro_money": 5, "macro_geo": 5, "macro_trade": 5, "macro_policy": 5,
    "ind_supply": 4, "ind_resource": 4, "ind_capex": 4, "ind_std": 4, "ind_chain": 4,
    "comp_earn": 2, "comp_deal": 2, "comp_mv": 2, "comp_risk": 1,
    "main_ai": 2, "main_overseas": 2,
    "noise": -2,
}

# 标签中文名
TAG_LABEL = {
    "macro_money": "宏观·货币", "macro_geo": "宏观·地缘", "macro_trade": "宏观·贸易", "macro_policy": "宏观·政策",
    "ind_supply": "行业·供给", "ind_resource": "行业·资源", "ind_capex": "行业·资本开支", "ind_std": "行业·标准", "ind_chain": "行业·供应链",
    "comp_earn": "公司·业绩", "comp_deal": "公司·交易", "comp_mv": "公司·资本", "comp_risk": "公司·风险",
    "main_ai": "主线·AI", "main_overseas": "主线·海外",
    "noise": "杂讯",
}

def classify_and_score(title, desc):
    """返回 (分类, 分数, 标签列表)。分类: 'macro'/'industry'/'company'/'noise'"""
    text = (title or "") + " " + (desc or "")
    tags = []
    for cat, kws in KEYWORDS.items():
        hits = [kw for kw in kws if kw in text]
        if hits:
            tags.append((cat, len(hits)))

    if not tags:
        return "noise", 0, []

    # 杂讯词
    noise_hits = sum(n for c, n in tags if c == "noise")
    non_noise = [t for t in tags if t[0] != "noise"]

    if not non_noise:
        return "noise", -2 * noise_hits, tags

    # 分类：按最高影响层级（macro > industry > company）
    macro_cats = [t for t in non_noise if t[0].startswith("macro_")]
    ind_cats = [t for t in non_noise if t[0].startswith("ind_")]
    comp_cats = [t for t in non_noise if t[0].startswith("comp_")]

    if macro_cats:
        category = "macro"
        base_cats = macro_cats
    elif ind_cats:
        category = "industry"
        base_cats = ind_cats
    elif comp_cats:
        category = "company"
        base_cats = comp_cats
    else:
        # 只有 main_ 主线词或杂讯词：归入公司类，基准用主线权重
        category = "company"
        main_cats = [t for t in non_noise if t[0].startswith("main_")]
        base_cats = main_cats if main_cats else [("comp_earn", 1)]

    # 分类内重要性：基准分取本类最高层级的权重
    base = max(LAYER_WEIGHT[c] for c, _ in base_cats)

    # 同类信号叠加（上限 +3）
    layer_bonus = 0
    for cat, n in base_cats:
        if LAYER_WEIGHT[cat] == base:
            layer_bonus += min(n, 2)
    layer_bonus = min(layer_bonus, 3)

    # 主线加分：AI/海外信号各 +1（上限 +2）
    main_bonus = 0
    if any(c == "main_ai" for c, _ in non_noise):
        main_bonus += 1
    if any(c == "main_overseas" for c, _ in non_noise):
        main_bonus += 1

    # 杂讯抵扣
    noise_penalty = min(noise_hits, base - 1) if base > 1 else noise_hits

    score = base + layer_bonus + main_bonus - noise_penalty
    return category, score, tags

# ===================== 解析 RSS 快讯 =====================
def parse_feeds(content):
    """解析 news_feeds.txt，返回 [(信源, 标题, 摘要)]"""
    items = []
    current_source = None
    for raw_line in content.split("\n"):
        line = raw_line.strip()
        if line.startswith("==="):
            m = re.match(r"=== (.+?) ===", line)
            current_source = m.group(1) if m else None
            continue
        # 摘要行：缩进>=4空格 且 不以“数字.”开头（避免和序号标题混淆）
        if (raw_line.startswith("    ") and not re.match(r"^\s*\d+\.", raw_line)
                and current_source and items):
            items[-1]["desc"] += line + " "
            continue
        m = re.match(r"^\d+\.\s*(.*)$", line)
        if m and current_source:
            items.append({"source": current_source, "title": m.group(1), "desc": ""})
    # 清理摘要里的重复（摘要常包含标题重复）
    for it in items:
        d = it["desc"].strip()
        # 若摘要以标题开头，去掉重复前缀
        if d.startswith(it["title"][:20]):
            d = d[len(it["title"]):].strip()
        it["desc"] = d
    return items

# ===================== 主逻辑 =====================
def main():
    if not NEWS_FILE.exists():
        print(f"✗ 找不到快讯文件: {NEWS_FILE}")
        return

    content = NEWS_FILE.read_text(encoding="utf-8")

    # 检测 RSS 服务是否失败
    if "失败" in content and "财联社电报" in content:
        failed = True
        items = []
    else:
        failed = False
        items = parse_feeds(content)

    # 打分分类
    scored = []
    for it in items:
        category, s, tags = classify_and_score(it["title"], it["desc"])
        scored.append({**it, "score": s, "tags": tags, "category": category})

    # 去重：按标题归一化后去重（不同信源转发的同一条新闻只留一条）
    def norm_title(t):
        # 去掉【】括号内容和各种电/来源尾缀，取核心内容
        t = re.sub(r"[【\[（(].*?[】\]）)]", "", t)
        t = re.sub(r"财联社\d+月\d+日电|同花顺|东方财富|华尔街见闻|\s+", "", t)
        # 去掉常见修饰词，避免"上半年/半年度""美国/中国"这类差异导致重复
        for w in ["上半年", "半年度", "美国", "中国", "年内", "今年", "拟", "将"]:
            t = t.replace(w, "")
        # 数字归一化：把数字替换为 N，避免"增46%"vs"增46.53%"差异
        t = re.sub(r"\d+[.\d]*%?", "N", t)
        return t[:25]  # 取前25字作为指纹

    seen = set()
    deduped = []
    for s in scored:
        fp = norm_title(s["title"])
        if fp and fp not in seen:
            seen.add(fp)
            deduped.append(s)

    # 按分类分组，每类内部按分数降序
    groups = {"macro": [], "industry": [], "company": []}
    for s in deduped:
        if s["category"] == "macro":
            groups["macro"].append(s)
        elif s["category"] == "industry":
            groups["industry"].append(s)
        elif s["category"] == "company":
            groups["company"].append(s)

    # 每类内部排序 + 筛选（分数 >= 3），每类最多15条
    CATEGORY_META = {
        "macro": ("宏观要闻", "央行/利率/地缘/贸易/政策 · 影响全市场", 5),
        "industry": ("行业要闻", "供给/资源/资本开支/标准 · 影响整个产业链", 4),
        "company": ("公司要闻", "业绩/交易/资本 · 个股层面", 3),
    }
    top_groups = {}
    for cat, items_list in groups.items():
        items_list.sort(key=lambda x: -x["score"])
        threshold = CATEGORY_META[cat][2]
        top_groups[cat] = [x for x in items_list if x["score"] >= threshold][:15]

    total_top = sum(len(v) for v in top_groups.values())

    # ===================== 生成 HTML =====================
    today = datetime.now().strftime("%Y-%m-%d")

    if failed or total_top == 0:
        body_html = f"""
        <div style="background:var(--card);border:1px solid var(--line);border-radius:10px;padding:40px;text-align:center;color:var(--ink-2)">
          <h2 style="margin-bottom:12px;color:var(--danger)">暂无可用新闻</h2>
          <p>RSS 快讯服务未启动或没有新增新闻。</p>
          <p style="margin-top:8px;font-size:.85rem">请运行 <code>启动RSS服务.bat</code> 后重试。</p>
        </div>"""
    else:
        # 三板块渲染：宏观 / 行业 / 公司
        sections = []
        for cat_key in ["macro", "industry", "company"]:
            cat_list = top_groups.get(cat_key, [])
            title, subtitle, _ = CATEGORY_META[cat_key]
            if not cat_list:
                continue
            cards = []
            for i, n in enumerate(cat_list, 1):
                tag_html = "".join(
                    f'<span class="tag tag-{cat}">{TAG_LABEL.get(cat, cat)}</span>'
                    for cat, _ in n["tags"] if cat != "noise"
                )
                desc = n["desc"][:180] + ("…" if len(n["desc"]) > 180 else "") if n["desc"] else ""
                rank_badge = '<span class="rank-hot">🔥 高价值</span>' if n["score"] >= 6 else ""
                cards.append(f"""
            <div class="news-card">
              <div class="news-head">
                <span class="news-rank">#{i:02d}</span>
                <span class="news-source">{n['source']}</span>
                <span class="news-score">+{n['score']}</span>
                {rank_badge}
              </div>
              <h3 class="news-title">{n['title']}</h3>
              {f'<p class="news-desc">{desc}</p>' if desc else ''}
              <div class="news-tags">{tag_html}</div>
            </div>""")
            sections.append(f"""
        <div class="cat-section cat-{cat_key}">
          <h2 class="cat-head">{title}<span class="cat-sub">{subtitle}</span><span class="cat-count">{len(cat_list)}条</span></h2>
          <div class="news-list">{''.join(cards)}</div>
        </div>""")
        total_top = sum(len(v) for v in top_groups.values())
        body_html = f"""
        <p class="stat-line">共解析 <strong>{len(items)}</strong> 条快讯，筛选出 <strong>{total_top}</strong> 条重点（宏观 {len(top_groups['macro'])} / 行业 {len(top_groups['industry'])} / 公司 {len(top_groups['company'])}）</p>
        {''.join(sections)}"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>今日要闻 · {today}</title>
<style>
  :root{{
    --paper:#F8F4ED;--card:#FCFAF5;--accent:#537D96;--accent-hover:#456A80;
    --accent-tint:rgba(83,125,150,.08);--ink:#3B3D3F;--ink-2:#6B6F73;--ink-3:#8E9196;
    --line:rgba(122,96,88,.18);--success:#7BAE7F;--danger:#8B3A3A;--coral:#EC8F8D;
    --serif:'EB Garamond','Noto Serif SC','Source Han Serif SC','Songti SC','STSong','SimSun',serif;
    --ui:system-ui,-apple-system,'PingFang SC',sans-serif;
    --mono:'JetBrains Mono',ui-monospace,monospace;
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:16px;line-height:1.7;padding:48px 24px 80px;}}
  .page{{max-width:1080px;margin:0 auto;}}
  .hero{{padding-bottom:24px;border-bottom:1px solid var(--line);margin-bottom:28px;}}
  .hero .date{{font-family:var(--mono);font-size:.85rem;letter-spacing:.06em;color:var(--ink-3);margin-bottom:8px;}}
  .hero h1{{font-size:2rem;font-weight:500;color:var(--ink);}}
  .hero h1 .accent{{color:var(--accent);}}
  .stat-line{{font-size:.9rem;color:var(--ink-2);margin-bottom:24px;}}
  .news-list{{display:flex;flex-direction:column;gap:16px;}}
  .news-card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:20px 24px;transition:box-shadow .2s,transform .2s;}}
  .news-card:hover{{box-shadow:0 4px 16px rgba(0,0,0,.05);transform:translateY(-1px);}}
  .news-head{{display:flex;align-items:center;gap:10px;margin-bottom:8px;}}
  .news-rank{{font-family:var(--mono);font-size:.8rem;color:var(--ink-3);}}
  .news-source{{font-family:var(--ui);font-size:.72rem;color:var(--accent);background:var(--accent-tint);padding:2px 8px;border-radius:4px;}}
  .news-score{{font-family:var(--mono);font-size:.78rem;color:var(--success);margin-left:auto;}}
  .rank-hot{{font-family:var(--ui);font-size:.68rem;color:#fff;background:var(--coral);padding:2px 8px;border-radius:10px;}}
  .news-title{{font-size:1.05rem;font-weight:500;color:var(--ink);line-height:1.5;}}
  .news-desc{{margin-top:6px;font-size:.88rem;color:var(--ink-2);line-height:1.6;}}
  .news-tags{{margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;}}
  .tag{{font-family:var(--ui);font-size:.68rem;padding:1px 8px;border-radius:4px;color:var(--ink-2);background:rgba(0,0,0,.03);}}
  .tag-supply{{color:var(--danger);background:rgba(139,58,58,.08);}}
  .tag-weapon{{color:var(--danger);background:rgba(139,58,58,.08);}}
  .tag-substitute{{color:var(--success);background:rgba(123,174,127,.1);}}
  .tag-overseas{{color:var(--accent);background:var(--accent-tint);}}
  .tag-ai{{color:var(--accent);background:var(--accent-tint);}}
  .tag-earnings{{color:#B38B5B;background:rgba(179,139,91,.1);}}
  .tag-policy{{color:#B38B5B;background:rgba(179,139,91,.1);}}
  /* 宏观层：深红 */
  .tag-macro_money,.tag-macro_geo,.tag-macro_trade,.tag-macro_policy{{color:#8B3A3A;background:rgba(139,58,58,.1);}}
  /* 行业层：暖棕 */
  .tag-ind_supply,.tag-ind_resource,.tag-ind_capex,.tag-ind_std,.tag-ind_chain{{color:#B3541E;background:rgba(179,84,30,.1);}}
  /* 公司层：橄榄绿 */
  .tag-comp_earn,.tag-comp_deal,.tag-comp_mv{{color:#6B7D3A;background:rgba(107,125,58,.1);}}
  .tag-comp_risk{{color:var(--ink-3);background:rgba(0,0,0,.04);}}
  /* 主线：青灰蓝 */
  .tag-main_ai,.tag-main_overseas{{color:var(--accent);background:var(--accent-tint);}}
  /* 分类板块 */
  .cat-section{{margin-bottom:32px;}}
  .cat-head{{display:flex;align-items:baseline;gap:10px;font-size:1.25rem;font-weight:500;color:var(--ink);border-left:3px solid var(--accent);padding-left:12px;margin-bottom:14px;}}
  .cat-sub{{font-size:.72rem;color:var(--ink-3);font-family:var(--ui);font-weight:400;}}
  .cat-count{{font-family:var(--mono);font-size:.72rem;color:var(--ink-3);margin-left:auto;}}
  .cat-macro .cat-head{{border-color:#8B3A3A;}}
  .cat-industry .cat-head{{border-color:#B3541E;}}
  .cat-company .cat-head{{border-color:#6B7D3A;}}
  .footer{{text-align:center;padding-top:36px;margin-top:48px;border-top:1px solid var(--line);font-size:.8rem;color:var(--ink-3);}}
</style>
</head>
<body>
<div class="page">
  <div class="hero">
    <div class="date">{today}</div>
    <h1>今日要闻 · <span class="accent">硬逻辑筛选</span></h1>
  </div>
  {body_html}
  <div class="footer">由 RSS 快讯自动提取 · 评分规则：供给约束/出口管制+3 · 国产替代/海外映射+2 · AI/业绩/政策+1 · 杂讯-2</div>
</div>
</body>
</html>"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"✅ 今日要闻看板已生成: {OUTPUT_FILE}")
    print(f"   解析 {len(items)} 条，筛选 {len(top)} 条高价值")

if __name__ == "__main__":
    main()

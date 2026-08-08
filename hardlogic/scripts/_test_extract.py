# 模拟测试 extract_news.py 的解析和评分逻辑
import sys
sys.path.insert(0, r"E:\Hanako_WorkSpace\研报\个股研究\hardlogic\scripts")
import extract_news as en

# 模拟快讯内容
sample = """=== 财联社电报 ===
  1. 【日本两家六氟化钨产线7月1日永久停产】全球供给缺口扩大，中船特气产能满载
     日本关东电化与中央硝子因钨原料断供宣布永久停产，占全球产能25%
  2. 【英伟达Rubin平台PCB层数翻倍】高端铜箔需求爆发
  3. 【沪指收跌1.64% 成交额1.5万亿】
  4. 【商务部：对日稀土出口管制持续收紧】氧化钇海外价格飙涨
  5. 【某公司半导体硅片认证通过】国产替代加速

=== 东方财富快讯 ===
  1. 【美光科技股价创新高】HBM需求超预期，存储巨头扩产
  2. 【央行开展逆回购操作】市场流动性充裕
"""

items = en.parse_feeds(sample)
print(f"解析出 {len(items)} 条")
for it in items:
    s, tags = en.score_news(it["title"], it["desc"])
    print(f"  [{s:+d}] {it['title'][:40]} | {tags}")

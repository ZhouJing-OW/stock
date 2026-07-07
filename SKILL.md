# 12维基本面深度分析 — 执行规范

> 本规范用于指导自动化系统产出对标手工质量的分析报告。
> 质量标准参考：`data/002916.json`（深南电路）为合格范例。
> 数据结构定义：`templates/schema.json`。

---

## 一、核心原则

1. **每一个字段必须有真实数据支撑**。不允许 null、空字符串 ""、空数组 []、0 值占位。
2. **每一条结论必须有搜索来源**。分析不是填空，是基于事实的判断。
3. **财务数据至少覆盖最近 2 个完整财年 + 最新季报**。
4. **护城河 5 维评分必须有分数 + 一句具体的依据**（不能全是 3 分）。
5. **综合研判必须给出明确的评级、仓位、建仓策略、止损条件**。

---

## 一.五、数据库升级模式（Upgrade）

当任务 action 为 `"update"` 时，表示该股票已有分析数据，仅需增量升级而非完全重建。目标：**最小化 token 消耗，仅更新变化的部分**。

### 升级流程

#### 第 1 步：加载现有数据
读取 `data/{code}.json`，作为升级基线。记录现有数据的 `analysis_date` 和 `fiscal_period`。

#### 第 2 步：财报数据升级（必须）
搜索最新季报/年报数据，对比现有 `financials.periods` 数组：
- 如果最新财报期不在现有 periods 中 → 追加新列，更新全部 10 个 metrics 数组
- 如果最新财报期已存在 → 核查数字是否有修正，有修正才改
- 更新 `meta.fiscal_period` 为最新财报期
- 更新 `overview` 中的 `pe_ttm`、`pb`、`total_market_cap_yi`（市值和估值是实时变化的）

#### 第 3 步：基金数据升级（必须）
搜索最新基金持仓数据，更新 `fund_attention` 全部字段。基金持仓每季度变化，必须全量刷新。

#### 第 4 步：事实核查（按需）
对以下维度执行快速搜索验证，**仅在发现实质性变化时才修改**：
- 护城河 (moat)：是否有新的竞争格局变化？核心技术突破或丢失？
- 成长驱动力 (growth)：是否有新的催化剂或风险事件？
- 竞争格局 (competition)：是否有新的竞争对手或市场份额变化？
- 管理层 (governance)：是否有高管变动、股权变更、违规事件？
- 风险 (risks)：是否有新的重大风险出现？

**核查原则**：如果搜索结果与现有分析一致，不修改原文。只在发现明确的新事实时才更新。

#### 第 5 步：综合研判升级（必须）
基于以上升级内容，重新评估 `verdict`：
- 评级是否需要调整？（财报超预期/低于预期 → 可能影响评级）
- 仓位建议是否需要调整？
- 建仓策略和止损条件是否需要更新？
- 如有实质性变化，更新 `core_thesis` 和 `long_reasons`/`short_reasons`
- 如无实质性变化，在 `core_thesis` 末尾追加一句 "[财报期 XXX 更新：无重大变化]"

#### 第 6 步：更新元数据
- `meta.analysis_date` → 当前日期
- `meta.last_updated` → 当前时间戳
- `meta.confidence` → 根据需要调整

### 升级 vs 新建的判断标准
- 任务 action 为 `"new"` 或文件不存在 → 完全新建（走第二章流程）
- 任务 action 为 `"update"` 且文件存在 → 增量升级（走本章流程）

---

## 二、执行流程（每个股票独立执行）

### 第 1 步：信息收集（必须并行搜索，一次搜完）

对目标股票执行以下 4 组关键词搜索，覆盖全部 12 个维度：

**组 A：财务与业务**
- `{股票代码} {股票简称} 2025年报 2026一季报 营收 净利润 毛利率 业务构成 ROE`
- `{股票代码} {股票简称} 估值 PE PB ROE 财务指标 近三年`
- 必须提取：近 2-3 年营收、净利润、毛利率、净利率、ROE、资产负债率、经营现金流、研发费用率

**组 B：行业与竞争**
- `{股票代码} {股票简称} 行业地位 竞争格局 市场份额`
- `{股票代码} {股票简称} 对比 {主要竞争对手简称}`
- 必须提取：2-4 家主要竞争对手的名称、代码、市值、技术差距、差异化

**组 C：基金与治理**
- `{股票代码} {股票简称} 基金持仓 2026 机构持股 重仓`
- 必须提取：持有基金家数、基金持股总量、占流通股比、明星基金经理持仓、近期调研次数

**组 D：催化与风险**
- `{股票代码} {股票简称} 催化剂 利好 业绩展望 2026`
- 必须提取：近期关键事件、业绩展望、行业政策、风险因素

### 第 2 步：逐维度分析（按 schema.json 结构填写，禁止跳步）

对 `templates/schema.json` 中的每个字段，按照以下规范填写：

#### Meta
- `analysis_date`: 当前日期 YYYY-MM-DD
- `fiscal_period`: 最新财报期（2026Q1 / 2025Q4）
- `confidence`: 1-5 整数（4=数据充分且结论明确，3=部分数据估算，2=数据稀疏）
- `concept_tags`: 5-9 个精准标签，基于搜索到的实际业务

#### 1. 公司速览 (overview)
- `one_liner`: 一句精准定位，含核心产品/业务和主要受益逻辑
- `revenue_segments`: 必须有 2-4 个业务板块，每个含营收占比、毛利率、同比增速（来自年报）
- `total_market_cap_yi` / `float_market_cap_yi`: 当前市值（亿元），从搜索中获取
- `pe_ttm` / `pb`: 基于最新年报净利润和当前市值计算

#### 2. 产业链定位 (supply_chain)
- `position`: 描述公司在产业链中的位置
- `upstream` / `downstream`: 列出具体公司名称，不是泛泛的"原材料供应商"
- `upstream_bargaining` / `downstream_bargaining`: 必须填 level（强/中/弱）+ reason（具体理由）
- `supply_constraints`: 如果确实不存在供给硬约束，`has_hard_constraint` 填 false，其他字段填 "无明显供给约束"

#### 3. 护城河深度 (moat) - 重点！
- 五个维度（tech_barrier / scale_effect / customer_stickiness / brand_patent_license / cost_advantage）都必须填写真实分数(1-5)，不能全填 3
- 每个 score 必须配 detail，说明为什么是这个分数。detail 必须是基于搜索的具体事实，不是泛泛评价
- `trend_3_5yr`: 拓宽/维持/收窄
- `core_risk`: 护城河面临的核心威胁

#### 4. 财务体检 (financials) - 重点！
- `periods`: 数组，标注列名，例如 ["2023", "2024", "2025", "2026Q1"]。年度用4位数字，季度加Q标记（如2026Q1）
- ⚠️ 年度数据(2023/2024/2025)和季度数据(2026Q1)必须保持原始值，不要将季度数据年化（×4）。两者的时间尺度不同，viewer 会自动识别年度期间来计算趋势
- `metrics`: 10 个指标，每个是一个数组，必须至少有 3 个非空数值
  - revenue_yi（营收/亿）, net_profit_yi（归母净利/亿）
  - gross_margin_pct, net_margin_pct, roe_pct, debt_ratio_pct
  - ocf_to_profit（经营现金流/净利润）, rd_ratio_pct
  - ar_turnover_days（应收周转天数）, inventory_turnover_days（存货周转天数）
- `highlights`: 2-4 条财务亮点，具体写数字
- `risk_points`: 2-3 条财务风险点

#### 5. 成长驱动力 (growth)
- `short_term_6m` / `mid_term_18m` / `long_term_5y`: 每个至少 3 条
- `tam_yi`: 可寻址市场规模（亿元）
- `penetration_pct`: 当前市占率

#### 6. 竞争格局 (competition)
- `rivals`: 至少 3 个对手，每个填满 name/code/market_cap/tech_gap/share_comparison/differentiation
- `porter_five`: 五个维度填高/中/低

#### 7. 管理层与治理 (governance)
- 全部字段根据搜索结果填写
- `integrity_record`: 基于搜索结果，如有负面写具体事项，没有写"无重大负面记录"

#### 8. 基金关注度 (fund_attention)
- 从组 C 搜索结果中提取具体数字，不能全填 null
- `holding_funds_count` / `total_holding_shares_wan` / `holding_pct_of_float`: 必填
- `star_manager_holdings`: 列出 1-3 个具体基金名称和持股数
- `trend`: 上升/稳定/下降
- `score`: 1-10

#### 9. 估值锚点 (valuation)
- `current`: 填 PE/PB/PS 当前值和行业对比
- `scenarios`: 乐观/基准/悲观三个情景，每个填 assumptions + target_market_cap_yi + target_price + upside/downside_pct
- 目标价基于 PE 估值法：净利润预测 × 合理 PE

#### 10. 风险矩阵 (risks)
- 至少 4 个风险项
- 每个填 risk（具体事项）/ probability（高/中/低）/ impact（高/中/低）/ mitigation（应对思路）

#### 11. 催化剂日历 (catalysts)
- 至少 3 个催化剂
- 每个填 time_window / event / expected_impact / certainty（高/中/低）

#### 12. 综合研判 (verdict) - 重点！
- `core_thesis`: 一句总结核心投资逻辑
- `long_reasons`: 必须 3 条具体做多理由（不是模板套话，每条基于搜索到的事实）
- `short_reasons`: 必须 3 条具体做空/回避理由
- `rating`: 必须从「强烈看好 / 看好 / 中性看好 / 中性 / 谨慎 / 回避 / 强烈回避」中选一个
- `suggested_position_pct`: 0-20 的数字
- `holding_period`: 短线/波段/中线/长线
- `entry_strategy`: 具体的建仓价位和条件
- `stop_loss_conditions`: 具体的止损条件
- `key_tracking_metrics`: 3-5 个具体跟踪指标

---

## 三、保存与验证

### 保存
将完整 JSON 写入 `data/{code}.json`。写入后立即运行验证：

```bash
python E:\Hanako_WorkSpace\研报\个股研究\bridge\validate_json.py E:\Hanako_WorkSpace\研报\个股研究\data\{code}.json
```

### 验证不通过时的修复步骤
1. 如果提示"发现 ASCII 引号混入中文文本"：将中文文本中的 ASCII 直引号 `"` 替换为中文弯引号 `""`
2. 如果提示"JSON 语法错误"：定位到错误行列，修复语法
3. 如果提示"缺少维度"：补充缺失的顶级字段

### 通过验证后
将任务文件从 `tasks/processing/` 移动到 `tasks/completed/`。

---

## 四、常见错误（绝对禁止）

| 错误 | 原因 | 正确做法 |
|------|------|----------|
| JSON 引号语法错误 | 中文文本中用了 ASCII 直引号 `""` | 中文引号用弯引号 `""` |
| moat scores 全空 / 全 3 分 | 没有做竞争分析 | 逐维度给出分数+事实依据 |
| financials metrics 数组全 null | 没有提取财务数据 | 从年报/季报/财经网站提取真实数字 |
| verdict rating 为 null / 空 | 没有形成判断 | 基于多空逻辑对比给出明确评级 |
| one_liner 只有公司名 | 没有提炼核心投资逻辑 | 一句话说明做什么+受益什么 |
| rival 信息空泛 | 没有搜索竞争对手 | 列出具体对手名称+股票代码+差异化 |
| fund_attention 全 null | 没有搜索基金数据 | 搜索具体数字，至少有家数和持股占比 |
| 中文内容全是陈述、没有观点 | 只复制年报内容 | 每个维度给出分析性判断 |

---

## 五、质量基准

分析完成后，自检以下 6 个关键信号。任何一条不通过，分析不合格：

1. ✅ 护城河 5 个维度分数各不相同，且都有具体依据句
2. ✅ 财务指标至少覆盖 3 个年度/季度，且不是全 0
3. ✅ 综合研判有明确的 3+3 多空理由 + 具体评级 + 仓位建议 + 建仓策略 + 止损条件
4. ✅ 竞争对手列表至少有 3 家，每家都有差异化描述
5. ✅ 基金关注度至少有持股家数+持股占比两个数字
6. ✅ JSON 验证脚本返回 `[OK]`

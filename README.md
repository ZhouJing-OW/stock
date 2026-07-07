# stock-research — 通达信基本面分析自动化系统 v2.0

> 在通达信中按 `Ctrl+Shift+A`，自动触发 Hanako 对当前股票进行 12 维基本面深度分析。
> 分析结果以 JSON 存储，通过统一 HTML 页面查看。

## 架构

```
┌─────────────────┐    Win Message       ┌──────────────────┐
│   通达信 (TDX)   │ ◄─ 33780/33819 ──► │  AHK 热键脚本     │
│  TdxW_MainFrame │                     │  Ctrl+Shift+A/O  │
└─────────────────┘                     └────────┬─────────┘
                                                  │
                                    写入 JSON 任务  │
                                                  ▼
                                       ┌──────────────────┐
                                       │  tasks/pending/   │
                                       │  {code}_{ts}.json │
                                       └────────┬─────────┘
                                                  │
                                    Python Bridge 监控   │
                                                  ▼
                                       ┌──────────────────┐
                                       │  Hanako 分析引擎  │
                                       │  12维深度基本面   │
                                       └────────┬─────────┘
                                                  │
                                    输出结构化 JSON   │
                                                  ▼
                                       ┌──────────────────┐
                                       │  data/{code}.json │
                                       └────────┬─────────┘
                                                  │
                            HTTP Server (port 8899)    │
                                                  ▼
                                       ┌──────────────────┐
                                       │   viewer.html     │
                                       │   统一 HTML 查看器 │
                                       └──────────────────┘
```

## 目录结构

```
stock-research/
├── ahk/
│   └── tdx_research_hotkey.ahk    # AHK 热键脚本 (v2.0)
├── bridge/
│   ├── task_watcher.py            # Python 桥接 + HTTP 服务器
│   └── config.yaml                # 配置文件
├── templates/
│   ├── schema.json                # JSON 数据结构定义
│   ├── viewer.html                # 统一 HTML 查看器
│   └── fundamental_analysis.md    # 维度参考文档
├── data/
│   └── {code}.json                # 每只股票一个 JSON 文件
├── tasks/
│   ├── pending/                   # AHK 写入的任务
│   ├── processing/                # Hanako 处理中
│   └── completed/                 # 已完成归档
└── README.md
```

## 快速开始

### 1. 安装依赖

- [AutoHotkey v2.0+](https://www.autohotkey.com/download/)
- Python 3.9+ (仅桥接服务需要)
- `pip install pyyaml` (可选，手动解析已内置降级方案)

### 2. 启动桥接服务

```bash
cd stock-research/bridge
python task_watcher.py
```

服务启动后：
- **HTTP 服务器**: `http://localhost:8899`
- **查看器**: `http://localhost:8899/viewer.html?code=002384`
- **任务监控**: 自动轮询 `tasks/pending/`

高级选项：
```bash
python task_watcher.py --port 8888          # 自定义端口
python task_watcher.py --no-server          # 仅监控任务，不启动 HTTP
python task_watcher.py --no-watch           # 仅 HTTP 服务器
```

### 3. 启动 AHK 脚本

双击 `ahk/tdx_research_hotkey.ahk` 或放入 Windows 启动目录。

### 4. 使用

| 热键 | 功能 |
|------|------|
| `Ctrl+Shift+A` | 获取通达信当前股票代码 → 已有分析则打开查看器 / 无分析则创建任务 |
| `Ctrl+Shift+O` | 仅打开已有分析的查看器，不触发新分析 |
| `Win+Shift+A` | 手动输入任意6位股票代码 |

## 12 维分析框架

| # | 维度 | 核心问题 |
|---|------|----------|
| 1 | 公司速览 | 做什么的、营收结构、多大规模 |
| 2 | 产业链定位 | 产业链位置、议价能力、供给硬约束 |
| 3 | 护城河深度 | 五维评分 + 可持续性判断 |
| 4 | 财务体检 | 近3年核心指标趋势 |
| 5 | 成长驱动力 | 短/中/长期催化剂 + TAM |
| 6 | 竞争格局 | 对手对比 + 波特五力 |
| 7 | 管理层与治理 | 团队、激励、诚信、股东结构 |
| 8 | **基金关注度** | 持仓家数、占比、变动、明星基金经理、调研频率 |
| 9 | 估值锚点 | PE/PB分位数 + 三情景推演 |
| 10 | 风险矩阵 | 概率×影响 + 应对思路 |
| 11 | 催化剂日历 | 时间线事件 + 确定性 |
| 12 | 综合研判 | 多空逻辑 + 评级 + 仓位 + 止损 + 跟踪指标 |

## 文件格式

所有分析数据以标准 JSON 存储，单只股票一个文件。完整结构定义见 `templates/schema.json`。

```json
{
  "meta": { "code": "002384", "name": "东山精密", ... },
  "overview": { ... },
  "supply_chain": { ... },
  "moat": { ... },
  "financials": { ... },
  "growth": { ... },
  "competition": { ... },
  "governance": { ... },
  "fund_attention": { ... },
  "valuation": { ... },
  "risks": [ ... ],
  "catalysts": [ ... ],
  "verdict": { ... }
}
```

## 过时检测

AHK 检查 JSON 中 `meta.analysis_date` 距今天数，超过 `stale_days`（默认90天）弹窗询问是否触发更新。

#!/usr/bin/env pwsh
# 根据 Ming 的硬逻辑扫描报告，对 hardlogic.json 执行所有编辑决策。
$ErrorActionPreference = "Stop"

$dataPath = "E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json"
$todayStr = "2026-07-26"

$json = Get-Content $dataPath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 100
$stocks = [System.Collections.ArrayList]@($json.stocks)

# ==================== 1. 昊华科技：降分 + 修正 conceptAdded ====================
foreach ($s in $stocks) {
    if ($s.code -eq "600378") {
        $s.score = 5.0
        $s.conceptAdded = "2026-06-11"
        $oldRisk = $s.riskNote
        $s.riskNote = "⚠️ 六氟化钨营收占比仅0.13%（2025年约2169万元），概念被过度炒作业绩弹性极有限。真正六氟化钨核心受益标的应为中船特气（全球龙一）。" + $oldRisk
        Write-Host "✅ 昊华科技: score→5.0, conceptAdded→2026-06-11"
        break
    }
}

# ==================== 新增标的 ====================
function New-Stock($category, $subCategory, $code, $name, $market, $coreLogic, $supplyDemand, $priceSignal, $catalyst, $conceptAdded, $conceptSource, $conceptSourceUrl, $riskNote, $tags, $score, $reinforcements) {
    return [PSCustomObject]@{
        category = $category
        subCategory = $subCategory
        code = $code
        name = $name
        market = $market
        coreLogic = $coreLogic
        supplyDemand = $supplyDemand
        priceSignal = $priceSignal
        catalyst = $catalyst
        conceptAdded = $conceptAdded
        conceptSource = $conceptSource
        conceptSourceUrl = $conceptSourceUrl
        riskNote = $riskNote
        tags = $tags
        score = $score
        conceptReinforcements = $reinforcements
    }
}

# 中船特气
$new1 = New-Stock `
    "电子特气" "六氟化钨(WF6)全球龙一" "688146" "中船特气" "科创板" `
    "全球六氟化钨产能第一（2000吨/年，全球约25%）。日本关东电化+中央硝子合计2200吨产能2026年7月1日起永久停产，全球约25%高端产能永久退出、2028年前无新增高端供给。6N级六氟化钨价格从年初约50万/吨飙至220-300万/吨，7N级长协价330-360万/吨。Q2单季度营收12.03亿（+129%）、归母净利2.47亿（+171%），三季度起执行自主定价机制。在建1000吨预计2027年投产。下游存储/HBM需求暴增拉动六氟化钨用量指数级增长。三重逻辑完美匹配：供给硬约束（日本永久停产非临时）+海外缺口（2028年前无新增高端产能）+国产替代（全球龙一地位加速替代）。" `
    "日本退出产能约2200吨/年，占全球高端25%。全球缺口约2000吨/年，2028年前无新增高端产能。钼代钨替代路线短期替代比例<0.4%。6N级报价220-300万元/吨较4月初涨超190%，7N级长协价330-360万元/吨。中船特气现有2000吨满产，在建1000吨2027年投产。" `
    "6N级220-300万/吨（较4月初+190%）；7N级330-360万/吨；Q2营收12.03亿（+129%）净利2.47亿（+171%）" `
    "日本两大巨头7月1日永久停产（非临时检修）；三季度起自主定价机制；在建1000吨2027年投产；存储/HBM扩产拉动需求暴增" `
    "2026-06-18" "六氟化钨全球龙一+日本永久停产25%高端产能退出+Q2业绩暴增确认" `
    "https://36kr.com/p/3858510497780736" `
    "股价从42.92元（4月）飙至389.99元（6月峰值）现245.67元（7/24），累计涨幅472%；静态市盈率447倍估值极高；钼代钨替代路线正在验证但短期替代比例<0.4%；经营现金流-2.41亿（备货+涨价导致）" `
    @("全球龙一","供给硬约束","海外永久停产","国产替代","业绩暴增") 9.5 `
    @(@{date="2026-07-01"; desc="日本关东电化+中央硝子7月1日永久停产正式生效，全球25%六氟化钨高端产能永久退出；Q2营收12.03亿（+129%）净利2.47亿（+171%）业绩确认"; source="https://36kr.com/p/3858510497780736"})

$stocks.Add($new1) | Out-Null
Write-Host "✅ 新增: 中船特气 (688146) score=9.5"

# 东方锆业
$new2 = New-Stock `
    "被动元件" "氧化锆全产业链" "002167" "东方锆业" "主板" `
    "国内锆全产业链龙头。日本东曹因氧化钇断供（中国稀土出口管制）全面停产，东曹占全球高端氧化锆约18%份额、齿科专用细分高达40-45%。氧化钇海外价格一年暴涨15倍（8→500-600美元/kg）。东方锆业高端YSZ粉体产能3000吨/年，已通过宁德时代验证，与清陶能源、卫蓝新能源签订三年长协。6月18日第二次涨价：氧氯化锆+1500元/吨、二氧化锆+4500元/吨。东曹停产造成全球约6000吨/年刚性供应缺口。三重共振：供给硬约束（东曹永久停产）+海外缺口（齿科/MLCC粉体断供）+国产替代（全产业链唯一替代者）。" `
    "东曹停产造成全球约6000吨/年刚性供应缺口。氧化钇海外价从8美元/kg暴涨至500-600美元/kg（+15倍），海外厂商缺乏适配国产粉体能力。东方锆业高端YSZ粉体3000吨/年，已通过宁德/清陶/卫蓝验证。" `
    "6月18日第二次涨价：氧氯化锆+1500元/吨、二氧化锆+4500元/吨；7月23日随国瓷涨价公告20CM涨停" `
    "东曹因氧化钇断供全面停产；固态电池长协锁定（清陶/卫蓝）；氧化锆全产业链涨价传导" `
    "2026-07-20" "东曹断供→氧化锆全产业链涨价+固态电池长协锁定需求+国瓷涨价公告共振" `
    "https://www.yicai.com/news/103283685.html" `
    "氧化锆业务有周期属性；固态电池量产进度不确定；东曹若复产将释放紧缺溢价" `
    @("海外断供","供给硬约束","固态电池","全产业链","涨价确认") 8.0 `
    @(@{date="2026-07-23"; desc="随国瓷氧化锆涨价公告20CM涨停；东曹断供已满6周氧化钇海外价差超160倍确认不可逆；固态电池长协锁定中长期需求"; source="https://www.yicai.com/news/103283685.html"})

$stocks.Add($new2) | Out-Null
Write-Host "✅ 新增: 东方锆业 (002167) score=8.0"

# 福晶科技
$new3 = New-Stock `
    "光互连" "法拉第旋光片(光隔离器)" "002222" "福晶科技" "主板" `
    "国内唯一实现TGG/TSAG磁光晶体→法拉第旋光片全流程量产上市公司。日本Granopt因稀土出口管制大幅减产（2026年1月起逐步减产，5月外售产品基本枯竭），Coherent停止外售，全球法拉第旋光片80%以上供给收缩。高端11×11mm方片价格从120→175美元/片（+46%），交付周期拉长至6-9个月。2026年全球需求约2500万片，缺口预估超40%。公司计划2026年月产能从2000-5000片提升至10000片。供给硬约束（日本减产+美国停售）+海外缺口（全球可外售供给骤降80%+）+国产替代（国内唯一量产）三重逻辑成立，但目前法拉第旋光片业务营收占比<1%，处于产能爬坡期。" `
    "Coherent不再对外销售，Granopt减产→全球可外售供给骤降80%+。高端11×11mm方片价格+46%，交付周期拉长至6-9个月。2026年全球需求约2500万片，缺口预估超40%。福晶科技国内唯一全流程量产，计划月产能扩至10000片。" `
    "11×11mm方片120→175美元/片（+46%）；交付周期6-9个月" `
    "日本Granopt减产+美国Coherent停售→全球80%+供给退出；公司产能爬坡2026年目标10000片/月" `
    "2026-03-27" "法拉第旋光片国产替代：日本减产+美国停售→全球80%供给收缩+福晶科技国内唯一量产" `
    "https://www.cls.cn/detail/2326916" `
    "法拉第旋光片业务营收占比<1%，目前仍处概念阶段；产能爬坡节奏可能不及预期（2026年目标10000片/月）；业绩兑现时间表不确定" `
    @("海外断供","国产替代","唯一量产","光通信") 6.5 `
    @(@{date="2026-05-01"; desc="日本Granopt 5月外售产品基本枯竭确认；Coherent正式停止外售；全球法拉第旋光片80%+供给退出"; source="https://www.cls.cn/detail/2326916"})

$stocks.Add($new3) | Out-Null
Write-Host "✅ 新增: 福晶科技 (002222) score=6.5"

# 斯达半导
$new4 = New-Stock `
    "功率半导体" "IGBT/SiC功率器件" "603290" "斯达半导" "主板" `
    "国内IGBT/SiC模块龙头。7月1日起近20家国内外功率半导体企业同步第二轮涨价，斯达半导IGBT/SiC涨价15%起。AI服务器电源芯片单机价值量是传统服务器3-5倍，8英寸晶圆稼动率超110%、扩产需2-3年。海外英飞凌/TI/ST同步第二轮涨价，中信证券研判涨价趋势延续至2027年。全球前五大功率半导体企业资本开支连续两年下降，新增供给2028年前无法释放。AI数据中心800V HVDC供电架构推广拉动SiC/IGBT需求结构性爆发。" `
    "8英寸晶圆稼动率超110%，扩产需2-3年。全球前五大功率半导体企业资本开支连续两年下降。AI服务器电源芯片订单已排至2027年上半年。海外英飞凌/TI/ST同步第二轮涨价确认全行业供需紧张。" `
    "7月1日起IGBT/SiC涨价15%起；近20家企业同步第二轮涨价；海外英飞凌/TI/ST同步跟涨" `
    "AI数据中心800V HVDC供电架构推广；8英寸产能硬约束；全球功率半导体企业资本开支收缩" `
    "2026-07-02" "功率半导体第二轮涨价：近20家企业7月1日起集中涨价+AI服务器电源芯片需求爆发+8英寸产能硬约束" `
    "https://www.stcn.com/article/detail/3993611.html" `
    "功率半导体涨价属于全行业产能周期而非不可替代供给硬约束；若AI需求放缓海外大厂可回调产能；竞争格局相对分散；SiC业务仍处投入期" `
    @("功率涨价","AI供电","8英寸硬约束","国产替代","SiC") 7.5 `
    @(@{date="2026-07-01"; desc="近20家功率半导体企业7月1日起第二轮集中涨价正式执行；斯达半导IGBT/SiC涨价15%起；英飞凌/TI/ST海外同步涨价；中信证券研判涨价至2027年"; source="https://www.stcn.com/article/detail/3993611.html"})

$stocks.Add($new4) | Out-Null
Write-Host "✅ 新增: 斯达半导 (603290) score=7.5"

Write-Host ("`n📊 标的总数: " + $stocks.Count)

# ==================== 按 category 内 score 降序排序 ====================
$grouped = $stocks | Group-Object -Property category | Sort-Object { -$_.Count }

$sortedStocks = @()
foreach ($g in $grouped) {
    $sorted = $g.Group | Sort-Object { -$_.score }
    $sortedStocks += $sorted
}

# 重新编号
for ($i = 0; $i -lt $sortedStocks.Count; $i++) {
    $sortedStocks[$i].id = $i + 1
}

$json.stocks = $sortedStocks

# ==================== 更新 stats ====================
$catCounts = @{}
$mktCounts = @{}
foreach ($s in $sortedStocks) {
    $catCounts[$s.category] = ($catCounts[$s.category] -or 0) + 1
    $mktCounts[$s.market] = ($mktCounts[$s.market] -or 0) + 1
}

$json.stats.categories = @($grouped | ForEach-Object {
    [PSCustomObject]@{ name = $_.Name; count = $_.Count }
})
$json.stats.totalMarkets = [PSCustomObject]$mktCounts
$json.stats.totalStocks = $sortedStocks.Count

# ==================== 更新 meta ====================
$json.meta.updated = $todayStr

# ==================== 写回 ====================
$json | ConvertTo-Json -Depth 100 | Set-Content $dataPath -Encoding UTF8

Write-Host "`n✅ JSON 已写回: $dataPath"
Write-Host "   更新日期: $todayStr"
Write-Host "   标的总数: $($sortedStocks.Count)"

# 打印排序后前20
Write-Host "`n📋 排序后前20只标的:"
for ($i = 0; $i -lt [Math]::Min(20, $sortedStocks.Count); $i++) {
    $s = $sortedStocks[$i]
    Write-Host ("   #{0:D2} {1} {2,-8s} [{3}] score={4}" -f $s.id, $s.code, $s.name, $s.category, $s.score)
}

const fs = require('fs');
const path = require('path');

const DATA_PATH = 'E:/Hanako_WorkSpace/硬逻辑看板/data/hardlogic.json';
const TODAY = '2026-07-31';

let data = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
let stocks = data.stocks;

// Helper: find by code
function find(code) { return stocks.find(s => s.code === code); }

// Helper: trim reinforcements, fold important events into coreLogic
function trimReinf(s, keep = 3) {
  const reinf = s.conceptReinforcements || [];
  if (reinf.length <= keep) return;
  reinf.sort((a, b) => b.date.localeCompare(a.date));
  const removed = reinf.slice(keep);
  const important = ['涨价', '认证通过', '量产', '停产', '突破', '大单签约', '业绩', '净利预增', '净利润'];
  for (const r of removed) {
    if (important.some(kw => r.desc.includes(kw))) {
      const firstSentence = r.desc.split('；')[0];
      s.coreLogic = s.coreLogic.replace(/。$/, '') + '。' + firstSentence + '。';
    }
  }
  s.conceptReinforcements = reinf.slice(0, keep);
}

console.log('=== Applying Ming Report Edits ===');

// 1. Remove duplicate 风华高科 (older id=16 entry from 2026-03-03)
const dupIdx = stocks.findIndex(s => s.code === '000636' && s.conceptAdded === '2026-03-03');
if (dupIdx >= 0) {
  stocks.splice(dupIdx, 1);
  console.log('✓ Removed duplicate 风华高科 (old id 16, conceptAdded 2026-03-03)');
}

// 2. Downgrade scores
const downgrades = [
  { code: '603938', note: '逻辑链条过长（光纤四氯化硅→AI光互连→碳化硅涨价关联性间接），reinforcements空白已超过30天，非硬供给约束核心标的。' },
  { code: '603290', note: '功率半导体涨价属于全行业产能周期而非不可替代供给硬约束，reinforcements仅7/1一条且已过30天，逻辑弱化明显。' },
  { code: '300373', note: '同上，功率涨价属产能周期非物理瓶颈，若AI需求放缓海外大厂可快速回调产能，逻辑弱化。' },
];
for (const d of downgrades) {
  const s = find(d.code);
  if (s) {
    s.score = 7.0;
    s.riskNote += ` ⚠️ 7/31复查：${d.note}`;
    console.log(`✓ Downgraded ${s.name}(${d.code}): 7.5→7.0`);
  }
}

// 3. 中船特气 already exists (id 11, score 9.5). No action needed.
console.log('✓ 中船特气 already in JSON (id 11, score 9.5) — skipping add');

// 4. Add reinforcements
// 深南电路 002916: add 7/30, trim
let s = find('002916');
if (s) {
  s.conceptReinforcements.push({
    date: '2026-07-30',
    desc: '三星电子表示芯片短缺2027年进一步加剧延续至2028年；ABF载板缺口预测持续上调；高盛维持ABF缺口扩大至2028年51%判断',
    source: 'https://www.cls.cn/detail/2440123'
  });
  trimReinf(s, 3);
  console.log(`✓ 深南电路: +7/30 reinforcement, trimmed to ${s.conceptReinforcements.length}`);
}

// 风华高科 000636 (newer entry): add 7/10 H1业绩
s = find('000636');
if (s) {
  s.conceptReinforcements.push({
    date: '2026-07-10',
    desc: 'H1归母净利2.7-3.0亿(+61.84-79.82%)；Q2净利1.81-2.11亿环比+104-138%；MLCC量价齐升叠加降本增效成效显著',
    source: 'https://finance.sina.com.cn/roll/2026-07-10/doc-inihinfz5180428.shtml'
  });
  trimReinf(s, 3);
  console.log(`✓ 风华高科: +7/10 H1业绩, trimmed to ${s.conceptReinforcements.length}`);
}

// 中钨高新 000657: add 7/30 中金研报
s = find('000657');
if (s) {
  s.conceptReinforcements.push({
    date: '2026-07-30',
    desc: '中金公司7/30研报明确：钨业龙头有望迎来量价齐升；7月钨价下跌企稳后再次出现涨价迹象；出口管制持续收紧强化供给约束',
    source: 'https://www.stcn.com/article/detail/4024430'
  });
  s.conceptReinforcements.sort((a, b) => b.date.localeCompare(a.date));
  if (s.conceptReinforcements.length > 3) trimReinf(s, 3);
  console.log(`✓ 中钨高新: +7/30 reinforcement (${s.conceptReinforcements.length} total)`);
}

// 鼎泰高科 301377: update 7/09 entry
s = find('301377');
if (s) {
  for (const r of s.conceptReinforcements) {
    if (r.date === '2026-07-09') {
      r.desc = '7月9日港股上市募资48亿港元（引入高瓴/易方达/霸菱等16家基石）；英伟达Kyber NVL144延期验证高端PCB瓶颈+日系钨棒全面停产双重催化';
    }
  }
  console.log('✓ 鼎泰高科: updated 7/09 reinforcement');
}

// 5. Re-sort within categories by score desc
const catOrder = [
  'PCB产业链', '电子特气', '被动元件', '光互连', '半导体上游',
  '半导体设备零部件', '先进封装', '制造与存储', '功率半导体',
  '医疗材料', '小金属(AI金属)'
];
const catMap = {};
for (const s of stocks) {
  if (!catMap[s.category]) catMap[s.category] = [];
  catMap[s.category].push(s);
}
const newStocks = [];
for (const cat of catOrder) {
  if (catMap[cat]) {
    catMap[cat].sort((a, b) => b.score - a.score);
    newStocks.push(...catMap[cat]);
  }
}
// Any categories not in catOrder
for (const cat of Object.keys(catMap)) {
  if (!catOrder.includes(cat)) {
    catMap[cat].sort((a, b) => b.score - a.score);
    newStocks.push(...catMap[cat]);
  }
}

// 6. Renumber
newStocks.forEach((s, i) => { s.id = i + 1; });
data.stocks = newStocks;

// 7. Update stats
const statCats = {};
const statMkts = {};
for (const s of newStocks) {
  statCats[s.category] = (statCats[s.category] || 0) + 1;
  statMkts[s.market] = (statMkts[s.market] || 0) + 1;
}
data.stats = {
  categories: Object.entries(statCats).map(([name, count]) => ({ name, count })),
  totalMarkets: statMkts,
  totalStocks: newStocks.length
};

// 8. Update meta
data.meta.updated = TODAY;

// Write back
fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2), 'utf8');

console.log(`\n=== Done ===`);
console.log(`Total stocks: ${newStocks.length}`);
console.log(`Categories: ${JSON.stringify(statCats)}`);

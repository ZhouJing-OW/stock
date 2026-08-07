/* 公共顶部导航栏组件
 * 用法: <script src="nav.js" data-root=""></script>
 * data-root: 当前页面到项目根目录的相对路径（根目录=""，子目录="../"）
 * 自动高亮当前页（根据 data-current 或 URL 匹配）
 */
(function () {
  const PAGES = [
    { id: 'index',     label: '个股研究',   href: 'index.html' },
    { id: 'tmt',       label: 'TMT产业链',  href: 'tmt_network/tmt_network_full.html' },
    { id: 'hardlogic', label: '硬逻辑',     href: 'hardlogic/hardlogic.html' },
    { id: 'fund',      label: '基金重仓',   href: 'fund_top100.html' },
    { id: 'materials', label: '稀缺材料',   href: 'ai_materials_scarcity.html' },
    { id: 'radar',     label: '资金',     href: 'https://onechart.top/', external: true, sep: true },
    { id: 'macro',     label: '宏观',     href: 'https://onechart.top/macro/', external: true }
  ];

  // 解析当前脚本的 data-root（页面到根目录的相对路径）
  const script = document.currentScript;
  const root = (script && script.getAttribute('data-root')) || '';
  const current = (script && script.getAttribute('data-current')) || detectCurrent();
  const theme = (script && script.getAttribute('data-theme')) || 'light';
  const navBg = (script && script.getAttribute('data-nav-bg')) || '';

  function detectCurrent() {
    const path = location.pathname.split('/').pop() || 'index.html';
    if (path.startsWith('tmt_network')) return 'tmt';
    if (path.startsWith('hardlogic')) return 'hardlogic';
    if (path.startsWith('fund_top100')) return 'fund';
    if (path.startsWith('ai_materials')) return 'materials';
    if (path === 'index.html' || path === '') return 'index';
    return '';
  }

  // 注入样式
  const darkCss = `
    .topnav { position:fixed; top:0; left:0; right:0; z-index:1000; display:flex; align-items:center; flex-wrap:wrap; gap:0 2px; padding:0 48px; min-height:24px; width:100%; box-sizing:border-box; background:${navBg || 'rgba(13,17,23,.65)'}; backdrop-filter:blur(6px); border-bottom:1px solid rgba(48,54,61,.5); font-family:system-ui,-apple-system,"PingFang SC",sans-serif; -webkit-text-size-adjust:none; text-size-adjust:none; transition:opacity .3s ease; }
    .topnav .nav-tab { display:inline-flex; align-items:center; height:20px; padding:0 5px; font-size:12px; font-weight:500; color:#8b949e; text-decoration:none; border-bottom:2px solid transparent; white-space:nowrap; transition:color .15s,border-color .15s; }
    .topnav .nav-sep { width:1px; height:12px; background:rgba(48,54,61,.6); margin:0 3px; }
    .topnav .nav-tab:hover { color:#c9d1d9; }
    .topnav .nav-tab.active { color:#58a6ff; border-bottom-color:#58a6ff; font-weight:700; }
    .topnav.cruise-hidden { opacity:0!important; pointer-events:none!important; }
    @media (max-width:800px) { .topnav { padding:0 8px; } .topnav .nav-tab { padding:0 6px; } }
  `;
  const lightCss = `
    .topnav { position:sticky; top:0; left:0; right:0; z-index:100; display:flex; align-items:center; flex-wrap:wrap; gap:0 2px; padding:0 48px; min-height:24px; width:100%; box-sizing:border-box; background:var(--card,#fff); border-bottom:1px solid var(--border,rgba(0,0,0,.1)); font-family:system-ui,-apple-system,"PingFang SC",sans-serif; -webkit-text-size-adjust:none; text-size-adjust:none; }
    .topnav .nav-tab { display:inline-flex; align-items:center; height:20px; padding:0 5px; font-size:12px; font-weight:500; color:var(--text-muted,#8e9196); text-decoration:none; border-bottom:2px solid transparent; white-space:nowrap; transition:color .15s,border-color .15s; }
    .topnav .nav-sep { width:1px; height:12px; background:var(--border,rgba(0,0,0,.15)); margin:0 3px; }
    .topnav .nav-tab:hover { color:var(--text,#1c1917); }
    .topnav .nav-tab.active { color:var(--accent,#2563eb); border-bottom-color:var(--accent,#2563eb); font-weight:700; }
    @media (max-width:800px) { .topnav { padding:0 8px; } .topnav .nav-tab { padding:0 6px; } }
  `;
  const style = document.createElement('style');
  style.textContent = theme === 'dark' ? darkCss : lightCss;
  document.head.appendChild(style);

  // 生成导航栏
  const nav = document.createElement('nav');
  nav.className = 'topnav';
  nav.id = 'topnav';
  PAGES.forEach(p => {
    if (p.sep) {
      const s = document.createElement('span');
      s.className = 'nav-sep';
      nav.appendChild(s);
    }
    const a = document.createElement('a');
    a.className = 'nav-tab' + (p.id === current ? ' active' : '');
    a.href = p.external ? p.href : root + p.href;
    a.textContent = p.label;
    if (p.external) a.target = '_blank';
    nav.appendChild(a);
  });
  document.body.insertBefore(nav, document.body.firstChild);
})();

// Render Open Graph share images (1200x630) and app icons with Playwright.
// Usage: node tools/og.js   (needs playwright; reads the built pages' titles from src/*.part)
const fs = require('fs'), path = require('path');
let pw; try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
const ROOT = path.resolve(__dirname, '..');
function meta(f) { const m = fs.readFileSync(f, 'utf8').match(/<!--\s*(\{[\s\S]*?\})\s*-->/); return JSON.parse(m[1]); }
const items = [
  { slug: 'home', kicker: 'Fractional CTO · AI Architect · US & UAE', h1: 'From the ontology to the infrastructure it runs on.' },
  { slug: 'insights', kicker: 'Insights', h1: 'Notes on AI, ontology, healthcare data and technical leadership.' },
  { slug: 'case-studies', kicker: 'Case studies', h1: 'The problem, the architecture, the flow and the decisions.' },
];
for (const dir of ['src/pages', 'src/insights', 'src/case-studies']) {
  const d = path.join(ROOT, dir); if (!fs.existsSync(d)) continue;
  for (const f of fs.readdirSync(d).filter(f => f.endsWith('.part'))) {
    const m = meta(path.join(d, f)); items.push({ slug: f.replace('.part', ''), kicker: m.kicker, h1: m.h1 });
  }
}
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const tpl = it => `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}body{width:1200px;height:630px;background:#111214;color:#f0ede6;font-family:Newsreader,Georgia,serif;position:relative;overflow:hidden}
.k{position:absolute;left:80px;top:84px;font:500 20px "IBM Plex Mono",monospace;letter-spacing:.16em;text-transform:uppercase;color:#e08a63;display:flex;gap:16px;align-items:center}
.k:before{content:"";width:44px;height:2px;background:#e08a63}
h1{position:absolute;left:80px;right:300px;top:150px;font-weight:450;font-size:${it.h1.length > 60 ? 62 : 74}px;line-height:1.04;letter-spacing:-.02em}
.f{position:absolute;left:80px;right:80px;bottom:64px;display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba(240,237,230,.18);padding-top:26px;font:22px "IBM Plex Mono",monospace;color:#b4b1aa}
.f b{font:500 30px Newsreader,serif;color:#f0ede6}.f b span{color:#e08a63}
svg{position:absolute;right:-40px;top:40px;opacity:.9}</style></head><body>
<svg width="420" height="420" viewBox="0 0 420 420">${(() => { let s = '', pts = []; let seed = it.slug.length * 7 + 3; const r = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  for (let i = 0; i < 18; i++) pts.push([40 + r() * 340, 40 + r() * 340, r() < .3]);
  pts.forEach((a, i) => pts.forEach((b, j) => { if (j > i) { const d = Math.hypot(a[0] - b[0], a[1] - b[1]); if (d < 120) s += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${a[2] || b[2] ? '#e08a63' : '#f0ede6'}" stroke-opacity="${(1 - d / 120) * .45}"/>`; } }));
  pts.forEach(a => s += `<circle cx="${a[0]}" cy="${a[1]}" r="${a[2] ? 5 : 2.6}" fill="${a[2] ? '#e08a63' : '#f0ede6'}" fill-opacity="${a[2] ? 1 : .6}"/>`); return s; })()}</svg>
<div class="k">${esc(it.kicker)}</div><h1>${esc(it.h1)}</h1>
<div class="f"><b>Sumanta<span>.</span></b><span>asksumanta.com</span></div></body></html>`;
(async () => {
  const b = await pw.chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  for (const it of items) { await p.setContent(tpl(it), { waitUntil: 'networkidle' }).catch(() => {}); await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(ROOT, 'assets/og', it.slug + '.png') }); }
  const svg = fs.readFileSync(path.join(ROOT, 'favicon.svg'), 'utf8');
  for (const [n, f] of [[180, 'apple-touch-icon.png'], [512, 'icon-512.png']]) {
    const q = await b.newPage({ viewport: { width: n, height: n } });
    await q.setContent(`<body style="margin:0">${svg.replace('<svg ', `<svg width="${n}" height="${n}" `)}</body>`);
    await q.screenshot({ path: path.join(ROOT, 'assets', f) }); await q.close(); }
  console.log('rendered', items.length, 'og images'); await b.close();
})();

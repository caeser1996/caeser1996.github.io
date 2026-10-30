#!/usr/bin/env python3
"""Build landing pages and insights articles from src/*.part fragments.

Each .part file starts with an HTML comment holding a JSON object (title,
description, h1, kicker, lede, keywords, faq, related, and for articles
date/readtime), followed by the body HTML.

Outputs:
  /<slug>/index.html             for src/pages/<slug>.part
  /insights/<slug>/index.html    for src/insights/<slug>.part
  /insights/index.html, sitemap.xml, llms.txt
  and refreshes the marked blocks in index.html (insights list, footer).

Run: python3 tools/build.py
"""
import datetime
import html
import json
import math
import pathlib
import re
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://asksumanta.com"
EMAIL = "sumantamukhopadhyaywork@gmail.com"
CAL = "https://calendar.app.google/fpARv4QHsYCLMo3a8"
NAME = "Sumanta Mukhopadhyay"
TODAY = datetime.date.today().isoformat()
CASES = []  # filled in main(); used by the footer

AREAS_SERVED = ["United States", "Canada", "United Kingdom", "European Union", "United Arab Emirates", "Saudi Arabia", "Qatar", "India", "Singapore", "Australia", "Worldwide"]

SERVICE_LABELS = {
    "fractional-cto": "Fractional CTO",
    "ai-architect": "AI & LLM architecture",
    "ontology-knowledge-graph": "Ontology & knowledge graphs",
    "healthcare-data-architecture": "Healthcare data architecture",
    "technical-due-diligence": "Technical due diligence",
    "uae": "Fractional CTO in the UAE",
}


def load(path):
    raw = path.read_text()
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", raw, re.S)
    if not m:
        raise SystemExit(f"{path}: missing JSON meta comment")
    meta = json.loads(m.group(1))
    meta["body"] = raw[m.end():].strip()
    meta["slug"] = path.stem
    return meta


def e(x):
    return html.escape(x, quote=True)


def words(body):
    return len(re.sub(r"<[^>]+>", " ", body).split())


HEAD_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..600'
    '&family=Schibsted+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />'
)

GTAG = """<!-- Google tag (gtag.js) with Consent Mode v2 -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'granted'});
  gtag('consent', 'default', {analytics_storage: 'denied', region: ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IS','IE','IT','LV','LI','LT','LU','MT','NL','NO','PL','PT','RO','SK','SI','ES','SE','GB','CH'], wait_for_update: 500});
  try { var c = localStorage.getItem('consent'); if (c === 'granted' || c === 'denied') gtag('consent', 'update', {analytics_storage: c}); } catch (e) {}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-8TKBV1S98Q"></script>
<script>
  gtag('js', new Date());

  gtag('config', 'G-8TKBV1S98Q', {content_group: (function(p){return p==='/'?'Home':p.indexOf('/insights/')===0?'Insights':p.indexOf('/case-studies/')===0?'Case studies':'Services';})(location.pathname)});
</script>"""

THEME_INIT = """<script>
  document.documentElement.classList.add('js');
  var t='light';try{t=localStorage.getItem('theme')||'light';}catch(e){}
  document.documentElement.setAttribute('data-theme',t);
  try{if(!sessionStorage.getItem('booted')&&!/bot|crawl|spider|slurp|lighthouse|headless/i.test(navigator.userAgent)&&!matchMedia('(prefers-reduced-motion: reduce)').matches){document.documentElement.classList.add('boot');sessionStorage.setItem('booted','1');}}catch(e){}
</script>"""

SOUND = '<button type="button" class="snd" aria-pressed="false" aria-label="Turn ambient sound on" title="Ambient sound"><span class="eq"><i></i><i></i><i></i><i></i></span></button>'

MOON = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
        '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')


NAV_POSTS = []  # filled in main(); latest insights for the menu
REGIONS = []  # filled in main(); regional landing pages


def label(slug, meta=None):
    if slug in SERVICE_LABELS:
        return SERVICE_LABELS[slug]
    for r in REGIONS:
        if r["slug"] == slug:
            return f"Fractional CTO in {r['country'] if r['country'] != 'European Union' else 'Europe'}"
    return (meta or {}).get("h1", slug)
SERVICE_BLURBS = {
    "fractional-cto": "Part-time technology leadership for startups and scale-ups",
    "ai-architect": "RAG, agents and private LLMs that make it to production",
    "ontology-knowledge-graph": "Shared meaning for your data, analytics and AI",
    "healthcare-data-architecture": "FHIR, OMOP and HIPAA-aligned data platforms",
    "technical-due-diligence": "Independent technology assessment for investors",
    "uae": "Technology leadership on the ground in the UAE",
}
CHEV = '<svg class="chev" width="10" height="10" viewBox="0 0 10 10" aria-hidden="true"><path d="M2 3.5l3 3 3-3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
SEARCH_BTN = ('<button type="button" class="kbtn" data-search aria-label="Search the site" title="Search (Ctrl K)">'
              '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
              '<kbd>⌘K</kbd></button>')


def nav_item(i, a):
    return f'<a class="nd-i" href="{a[0]}"><b>{e(a[1])}</b>' + (f'<span>{e(a[2])}</span>' if len(a) > 2 and a[2] else "") + "</a>"


def nav_drop(key, label, items, side):
    return (f'<div class="nd"><button type="button" class="nd-b" aria-expanded="false" aria-controls="nd-{key}">{label}{CHEV}</button>'
            f'<div class="nd-p" id="nd-{key}"><div class="nd-grid">{"".join(nav_item(i, a) for i, a in enumerate(items))}</div>'
            f'<div class="nd-side">{side}</div></div></div>')


def nav():
    svc = [(f"/{k}/", v, SERVICE_BLURBS.get(k, "")) for k, v in SERVICE_LABELS.items() if k != "uae"]
    svc.append(("/regions/", "Fractional CTO worldwide", "US, UK, Europe, Middle East, India, Singapore and Australia"))
    work = [("/case-studies/", "All case studies", f"{len(CASES)} anonymised engagements with architecture and flow diagrams"),
            ("/case-studies/#use-cases", "Use cases", "Problems I'm brought in to solve, by sector"),
            ("/case-studies/#snapshots", "Engagement snapshots", "Six common problems, the approach and the stack")]
    work += [(f"/case-studies/{c['slug']}/", c.get("short") or c["h1"], c.get("sector", "")) for c in CASES[:3]]
    ins = [("/insights/", "All insights", f"{len(NAV_POSTS)} articles on AI, data, cloud and leadership"),
           ("/insights/#topic-news", "Daily tech news", "A CTO's take on the day's releases, deals and rules"),
           ("/subscribe/", "Subscribe via RSS", "Get every new post in Feedly, Inoreader or any reader")]
    ins += [(f"/insights/{q['slug']}/", q["h1"], "") for q in NAV_POSTS[:5]]
    about = [("/about/", "About", "Background, credentials and open-source work"),
             ("/expertise/", "Expertise", "Practice areas, reference architecture and industries"),
             ("/how-i-work/", "How I work", "Playbook, principles and engagement models"),
             ("/how-i-work/#faq", "FAQ", "Common questions about working together"),
             ("/#contact", "Contact", "Book a call or send a message")]
    side_svc = ('<small>Not sure where to start?</small><p>Answer four questions and get a first diagnosis of your challenge.</p>'
                '<a class="lnk" href="/#assess">Analyse your challenge →</a>')
    side_work = ('<small>Confidential by default</small><p>Every case study is an anonymised composite, cited to public sources.</p>'
                 '<a class="lnk" href="/case-studies/">Browse all →</a>')
    side_ins = ('<small>New every week</small><p>Explainers, playbooks and analysis of new standards and regulation.</p>'
                '<a class="lnk" href="/insights/">Read the latest →</a>')
    side_about = ('<small>Take a break</small><p>Defend production from incoming incidents in Orbital Ops, a free sci-fi browser game.</p>'
                  '<a class="lnk" href="/play/">Play now →</a>')
    return f"""<div class="progress" id="progress"></div>
<nav class="topnav">
  <div class="nav-in">
    <a href="/" class="brand">Sumanta<span>.</span></a>
    <div class="nav-links" id="navLinks">
      {nav_drop("services", "Services", svc, side_svc)}
      {nav_drop("work", "Work", work, side_work)}
      {nav_drop("insights", "Insights", ins, side_ins)}
      {nav_drop("about", "About", about, side_about)}
      <a class="nd-l" href="/play/">Play <em>new</em></a>
    </div>
    <div class="nav-r">
      {SEARCH_BTN}
      {SOUND}
      <button class="theme" id="themeBtn" aria-label="Toggle colour theme">{MOON}</button>
      <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="navLinks"><span></span><span></span></button>
      <a href="{CAL}" target="_blank" rel="noopener" class="btn sm mag">Book a call</a>
    </div>
  </div>
</nav>"""


def modal():
    return f"""<dialog id="contactModal" class="cm" aria-labelledby="cmTitle" data-lenis-prevent>
  <form method="dialog" class="cm-x"><button aria-label="Close">×</button></form>
  <div class="kicker">Start a conversation</div>
  <h3 id="cmTitle">How would you like to reach me?</h3>
  <div class="cm-opts">
    <a class="cm-o pri" href="{CAL}" target="_blank" rel="noopener"><b>Book a 30-min call</b><span>Fastest. Pick any open slot on my calendar.</span><i>→</i></a>
    <a class="cm-o" id="cmGmail" href="#" target="_blank" rel="noopener"><b>Write in Gmail</b><span>Opens a pre-filled draft in your browser.</span><i>→</i></a>
    <a class="cm-o" id="cmMailto" href="mailto:{EMAIL}"><b>Use my email app</b><span>Outlook, Apple Mail or your default client.</span><i>→</i></a>
    <button type="button" class="cm-o" id="cmCopy"><b>Copy email address</b><span>{EMAIL}</span><i>⧉</i></button>
  </div>
  <p class="cm-foot">I reply personally within two business days. Time zones from the Americas and Europe to the Middle East and Asia-Pacific.</p>
</dialog>
<div class="toast" id="toast" role="status" aria-live="polite"></div>"""


def footer(pages, posts):
    svc = "".join(f'<li><a href="/{p["slug"]}/">{e(SERVICE_LABELS.get(p["slug"], p["h1"]))}</a></li>' for p in pages if p["slug"] != "uae")
    ins = "".join(f'<li><a href="/insights/{p["slug"]}/">{e(p["h1"])}</a></li>' for p in posts[:5])
    cs = "".join(f'<li><a href="/case-studies/{c["slug"]}/">{e(c.get("short") or c["h1"])}</a></li>' for c in CASES[:4])
    return f"""<footer class="site-foot">
  <div class="wrap">
    <div class="fcols">
      <div class="fc fbrand">
        <a href="/" class="brand">Sumanta<span>.</span></a>
        <p>Fractional CTO, principal engineer and AI architect. Ontology, AI, data platforms and cloud infrastructure across healthcare, fintech, SaaS, e-commerce and AI startups.</p>
        <p class="floc">Global, remote-first · based in India, the US &amp; UAE · <a href="/regions/">where I work</a></p>
      </div>
      <div class="fc"><h4>Services</h4><ul>{svc}<li><a href="/regions/">Fractional CTO worldwide →</a></li></ul></div>
      <div class="fc"><h4>Case studies</h4><ul>{cs}<li><a href="/case-studies/#snapshots">Engagement snapshots</a></li><li><a href="/case-studies/">All case studies →</a></li></ul></div>
      <div class="fc"><h4>Insights</h4><ul>{ins}<li><a href="/insights/">All articles →</a></li></ul></div>
      <div class="fc"><h4>Connect</h4><ul>
        <li><a href="{CAL}" target="_blank" rel="noopener">Book a 30-min call</a></li>
        <li><a href="mailto:{EMAIL}?subject=Engagement%20enquiry" data-contact="Engagement enquiry">Send a message</a></li>
        <li><a href="/#assess">Analyse your challenge</a></li>
        <li><a href="/how-i-work/">How I work</a></li>
        <li><a href="/expertise/">Expertise</a></li>
        <li><a href="/about/">About</a></li>
        <li><a href="/play/">Play Orbital Ops</a></li>
        <li><a href="https://github.com/caeser1996" target="_blank" rel="noopener">GitHub</a></li>
      </ul></div>
    </div>
    <div class="fbot"><span>© <span id="yr">{TODAY[:4]}</span> {NAME}</span><span class="sp"></span><a href="/privacy/">Privacy &amp; cookies</a><button type="button" class="cookie-link" data-cookie-settings>Cookie settings</button><a href="/subscribe/">RSS</a><a href="/sitemap.xml">Sitemap</a></div>
  </div>
</footer>"""


SCRIPTS = """<script src="/assets/site.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js" defer></script>"""


def head(title, desc, keywords, url, og_image, og_type, ld):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GTAG}
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}" />
<meta name="keywords" content="{e(', '.join(keywords))}" />
<meta name="author" content="{NAME}" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<link rel="canonical" href="{url}" />
<meta name="theme-color" content="#fafafa" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
<link rel="alternate" type="application/rss+xml" title="Sumanta Mukhopadhyay: insights and case studies" href="/feed.xml" />
<link rel="alternate" type="application/rss+xml" title="Sumanta Mukhopadhyay: daily tech news" href="/insights/news.xml" />
<meta property="og:site_name" content="{NAME}" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(desc)}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:url" content="{url}" />
<meta property="og:image" content="{og_image}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{e(title)}" />
<meta name="twitter:description" content="{e(desc)}" />
<meta name="twitter:image" content="{og_image}" />
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{HEAD_FONTS}
<link rel="stylesheet" href="/assets/site.css" />
{THEME_INIT}
</head>"""


def faq_html(faq):
    if not faq:
        return ""
    items = "".join(f'<details class="rise"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faq)
    return f"""<section class="sub-sec" id="faq">
      <div class="kicker">FAQ</div>
      <h2>Common questions</h2>
      <div class="faq">{items}</div>
    </section>"""


def related_html(paths, pages_by_slug, posts, tags=()):
    cards = []
    if tags:  # most shared tags first, newest wins ties (posts are already newest first)
        tags = set(tags)
        posts = sorted(posts, key=lambda q: -len(tags & set(q.get("tags", []))))
    for path in paths:
        slug = path.strip("/")
        if slug in pages_by_slug:
            p = pages_by_slug[slug]
            cards.append((f"/{slug}/", "Service", SERVICE_LABELS.get(slug, p["h1"]), p["lede"]))
    for p in posts[:3]:
        cards.append((f"/insights/{p['slug']}/", "Insight", p["h1"], p["lede"]))
    cards = cards[:4]
    if not cards:
        return ""
    inner = "".join(
        f'<a class="rcard rise" href="{u}"><small>{k}</small><b>{e(t)}</b><span>{e(d)}</span><i>→</i></a>'
        for u, k, t, d in cards)
    return f"""<section class="sub-sec">
      <div class="kicker">Keep reading</div>
      <h2>Related</h2>
      <div class="rgrid">{inner}</div>
    </section>"""


AUTHOR_BOX = f"""<aside class="author-box" aria-label="About the author">
        <div class="ab-av" aria-hidden="true">SM</div>
        <div><small>About the author</small><b>{NAME}</b>
        <p>Fractional CTO, principal engineer and AI architect based in India, the United States and the UAE. Works across ontology and knowledge graphs, production AI, healthcare data platforms and cloud infrastructure.</p>
        <div class="ab-l"><a href="/about/">More about me</a><a href="/how-i-work/">How I work</a><a href="https://github.com/caeser1996" target="_blank" rel="noopener">GitHub</a><a href="{CAL}" target="_blank" rel="noopener">Book a call</a></div></div>
      </aside>"""


def cta_html(subject):
    return f"""<section class="sub-cta rise">
      <div class="tagline"><i></i>Open to advisory, fractional CTO &amp; select builds</div>
      <h2>Let's talk about what you're building.</h2>
      <p>The fastest route is a free 30-minute call. Prefer to write? Send a message and I'll reply personally within two business days.</p>
      <div class="cta-row">
        <a class="btn mag" href="{CAL}" target="_blank" rel="noopener">Book a 30-min call →</a>
        <a class="btn ghost mag" href="mailto:{EMAIL}" data-contact="{e(subject)}">Send a message</a>
        <a class="lnk" href="/#assess" style="align-self:center">or analyse your challenge first →</a>
      </div>
    </section>"""


def person_ref():
    return {"@type": "Person", "@id": f"{SITE}/#person", "name": NAME, "url": f"{SITE}/"}


def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


FORMAT_LABELS = {"essay": "Essay", "explainer": "Explainer", "checklist": "Checklist", "field-note": "Field note",
                 "comparison": "Comparison", "playbook": "Playbook", "news-analysis": "Analysis", "tech-news": "Tech news",
                 "case-study": "Case study"}
TZ_NAMES = {"+0400": "GST", "-0400": "EDT", "-0500": "EST", "+0000": "UTC"}


def when(meta):
    """(iso, human) publish time for a post; falls back to the date alone."""
    dt = meta.get("datetime")
    if dt:
        d = datetime.datetime.fromisoformat(dt)
        tz = TZ_NAMES.get(d.strftime("%z"), "")
        return dt, d.strftime("%-d %b %Y · %H:%M") + (f" {tz}" if tz else "")
    d = meta.get("date", TODAY)
    return d, datetime.date.fromisoformat(d).strftime("%-d %b %Y")


def sort_key(meta):
    return meta.get("datetime") or (meta.get("date", TODAY) + "T00:00:00")


def _rng(seed):
    x = [sum(ord(c) * (i + 1) for i, c in enumerate(seed)) % 233280 or 7]

    def r():
        x[0] = (x[0] * 9301 + 49297) % 233280
        return x[0] / 233280
    return r


def cover_svg(meta, small=False):
    """Deterministic generative cover art; the motif varies with the post format."""
    r = _rng(meta["slug"])
    fmt = meta.get("format", "essay")
    W, H = 1200, 420
    out = [f'<line x1="{i * 100}" y1="0" x2="{i * 100}" y2="{H}" class="cv-grid"/>' for i in range(1, 12)]
    out += [f'<line x1="0" y1="{i * 84}" x2="{W}" y2="{i * 84}" class="cv-grid"/>' for i in range(1, 5)]
    if fmt in ("checklist", "playbook"):
        for i in range(7):
            y, hl = 50 + i * 48, " hl" if i % 3 == 0 else ""
            out.append(f'<circle cx="560" cy="{y + 11}" r="8" class="cv-dot{hl}"/>')
            out.append(f'<rect x="590" y="{y}" width="{160 + r() * 420:.0f}" height="22" class="cv-bar{hl}"/>')
    elif fmt in ("comparison", "news-analysis"):
        for k in range(3):
            pts = " ".join(f"{540 + i * 56},{H / 2 + (r() - .5) * 260 * (k + 1) / 3:.0f}" for i in range(12))
            out.append(f'<polyline points="{pts}" class="cv-line{" hl" if k == 2 else ""}"/>')
    elif fmt == "field-note":
        cx, cy = 880, 210
        out += [f'<circle cx="{cx}" cy="{cy}" r="{40 + i * 30}" class="cv-ring{" hl" if i == 2 else ""}"/>' for i in range(6)]
        for i in range(12):
            a, rad = r() * 6.283, 40 + int(r() * 6) * 30
            out.append(f'<circle cx="{cx + rad * math.cos(a):.0f}" cy="{cy + rad * math.sin(a):.0f}" '
                       f'r="{6 if i % 3 == 0 else 3}" class="cv-dot{" hl" if i % 3 == 0 else ""}"/>')
    else:
        pts = [(520 + r() * 640, 30 + r() * 360, r() < .25) for _ in range(26)]
        for i, a in enumerate(pts):
            for b in pts[i + 1:]:
                d = math.dist(a[:2], b[:2])
                if d < 150:
                    out.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" '
                               f'class="cv-edge{" hl" if a[2] or b[2] else ""}" opacity="{1 - d / 150:.2f}"/>')
        out += [f'<circle cx="{a[0]:.0f}" cy="{a[1]:.0f}" r="{6 if a[2] else 3}" class="cv-dot{" hl" if a[2] else ""}"/>'
                for a in pts]
    label = FORMAT_LABELS.get(fmt, fmt.title())
    if not small:
        out.append(f'<text x="60" y="90" class="cv-k">{e(label.upper())} · {e(meta["kicker"].upper())}</text>')
        out.append(f'<text x="60" y="350" class="cv-n">{e(("COVERS " + meta["period"].upper()) if meta.get("period") else when(meta)[1])}</text>')
    return f'<svg class="cover-svg" viewBox="0 0 {W} {H}" role="img" aria-label="{e(label)} cover art">{"".join(out)}</svg>'


def add_heading_ids(body):
    toc, used = [], set()

    def sub(m):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        sid = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "s"
        while sid in used:
            sid += "-x"
        used.add(sid)
        toc.append((sid, text))
        return f'<h2 id="{sid}">{m.group(1)}</h2>'
    return re.sub(r"<h2>(.*?)</h2>", sub, body), toc


def refs_html(cites):
    if not cites:
        return ""
    items = "".join(
        f'<li id="ref-{i}"><span class="rn">{i}</span><div><a href="{e(c["url"])}" target="_blank" rel="noopener">'
        f'{e(c["title"])}</a><small>{e(c.get("publisher", ""))}{" · " + e(c["date"]) if c.get("date") else ""}</small></div></li>'
        for i, c in enumerate(cites, 1))
    return f'<section class="refs" id="references"><div class="kicker">References</div><ol>{items}</ol></section>'


def share_html(url, title):
    u, t = quote(url, safe=""), quote(title, safe="")
    return (f'<div class="share"><span>Share</span>'
            f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={u}" target="_blank" rel="noopener">LinkedIn</a>'
            f'<a href="https://x.com/intent/post?url={u}&amp;text={t}" target="_blank" rel="noopener">X</a>'
            f'<a href="https://wa.me/?text={t}%20{u}" target="_blank" rel="noopener">WhatsApp</a>'
            f'<button type="button" class="copy-link" data-url="{e(url)}">Copy link</button></div>')


def post_card(p, tag="h2"):
    iso, human = when(p)
    return (f'<a class="post rise" href="/insights/{p["slug"]}/" data-tags="{e(" ".join(p.get("tags", [])))}">'
            f'<div class="pcover">{cover_svg(p, small=True)}</div>'
            f'<small><b>{e(FORMAT_LABELS.get(p.get("format", "essay"), "Essay"))}</b> · {e(p.get("period") or p["kicker"])}</small>'
            f'<{tag}>{e(p["h1"])}</{tag}><p>{e(p["lede"])}</p>'
            f'<span class="pmeta"><time datetime="{iso}">{e(human)}</time> · {e(p.get("readtime", ""))}</span></a>')


def case_card(c, tag="h2"):
    stack = "".join(f'<span class="tag">{e(t)}</span>' for t in c.get("stack", [])[:5])
    return (f'<a class="post cstudy rise" href="/case-studies/{c["slug"]}/" data-tags="{e(" ".join(c.get("tags", [])))}">'
            f'<div class="pcover">{cover_svg(c, small=True)}</div>'
            f'<small><b>Case study</b> · {e(c["sector"])}</small>'
            f'<{tag}>{e(c["h1"])}</{tag}><p>{e(c["lede"])}</p>'
            f'<span class="cs-stack">{stack}</span><i>Read the case study →</i></a>')


def glance_html(meta):
    cells = "".join(f'<div><small>{k}</small><b>{e(meta[f])}</b></div>'
                    for k, f in (("Sector", "sector"), ("My role", "role"), ("Engagement", "engagement"),
                                 ("Scope", "scope")) if meta.get(f))
    stack = "".join(f'<span class="tag">{e(t)}</span>' for t in meta.get("stack", []))
    outs = "".join(f"<li>{e(o)}</li>" for o in meta.get("outcomes", []))
    return (f'<section class="glance rise" aria-label="At a glance"><div class="kicker">At a glance</div>'
            f'<div class="glance-grid">{cells}</div>'
            + (f'<div class="glance-out"><small>What changed</small><ul>{outs}</ul></div>' if outs else "")
            + (f'<div class="cs-stack">{stack}</div>' if stack else "")
            + '<p class="glance-note">Anonymised composite. Client names, identifying details and confidential figures '
              'are withheld; public facts are cited in the references.</p></section>')


def page(meta, kind, pages, posts, pages_by_slug, cases=()):
    slug = meta["slug"]
    if kind == "service":
        url = f"{SITE}/{slug}/"
        crumb = [("Home", f"{SITE}/"), (label(slug, meta), url)]
        if meta.get("country"):
            crumb.insert(1, ("Worldwide", f"{SITE}/regions/"))
        main_ld = {"@type": "Service", "name": label(slug, meta), "description": meta["description"],
                   "provider": person_ref(), "url": url, "serviceType": "Fractional CTO and AI architecture",
                   "areaServed": meta.get("country") or AREAS_SERVED}
        og_type = "website"
        meta_line = ""
    elif kind == "case":
        url = f"{SITE}/case-studies/{slug}/"
        crumb = [("Home", f"{SITE}/"), ("Case studies", f"{SITE}/case-studies/"), (meta["h1"], url)]
        iso, human = when(meta)
        main_ld = {"@type": "Article", "headline": meta["h1"], "description": meta["description"],
                   "articleSection": "Case study", "about": meta.get("sector", ""),
                   "datePublished": iso, "dateModified": meta.get("updated", iso),
                   "citation": [{"@type": "CreativeWork", "name": c["title"], "url": c["url"]}
                                for c in meta.get("citations", [])],
                   "author": person_ref(), "publisher": person_ref(), "mainEntityOfPage": url,
                   "image": f"{SITE}/assets/og/{slug}.png", "keywords": ", ".join(meta["keywords"]),
                   "wordCount": words(meta["body"])}
        og_type = "article"
        tags = "".join(f'<span class="tagp">#{e(t)}</span>' for t in meta.get("tags", []))
        meta_line = (f'<div class="ameta"><span class="fmt">Case study</span><span>{e(meta["sector"])}</span>'
                     f'<span>{NAME}</span><time datetime="{iso}">{e(human)}</time><span>{e(meta.get("readtime", ""))}</span></div>'
                     f'<div class="atags">{tags}</div>')
    else:
        url = f"{SITE}/insights/{slug}/"
        crumb = [("Home", f"{SITE}/"), ("Insights", f"{SITE}/insights/"), (meta["h1"], url)]
        iso, human = when(meta)
        main_ld = {"@type": "BlogPosting", "headline": meta["h1"], "description": meta["description"],
                   "datePublished": iso, "dateModified": meta.get("updated", iso),
                   "articleSection": meta["kicker"], "genre": FORMAT_LABELS.get(meta.get("format", "essay"), "Essay"),
                   "citation": [{"@type": "CreativeWork", "name": c["title"], "url": c["url"]}
                                for c in meta.get("citations", [])],
                   "author": person_ref(), "publisher": person_ref(), "mainEntityOfPage": url,
                   "image": f"{SITE}/assets/og/{slug}.png", "keywords": ", ".join(meta["keywords"]),
                   "wordCount": words(meta["body"])}
        og_type = "article"
        fmt = FORMAT_LABELS.get(meta.get("format", "essay"), "Essay")
        tags = "".join(f'<span class="tagp">#{e(t)}</span>' for t in meta.get("tags", []))
        period = f'<span class="period">Covers {e(meta["period"])}</span>' if meta.get("period") else ""
        meta_line = (f'<div class="ameta"><span class="fmt">{e(fmt)}</span>{period}<span>{NAME}</span>'
                     f'<time datetime="{iso}">{e(human)}</time><span>{e(meta.get("readtime", ""))}</span>'
                     f'{"<span>" + str(len(meta.get("citations", []))) + " sources</span>" if meta.get("citations") else ""}</div>'
                     f'<div class="atags">{tags}</div>')
    graph = [main_ld, crumbs(crumb)]
    if meta.get("faq"):
        graph.append(faq_ld(meta["faq"]))
    ld = {"@context": "https://schema.org", "@graph": graph}
    og = f"{SITE}/assets/og/{slug}.png"
    bc = " <span>/</span> ".join(
        (f'<a href="{u.replace(SITE, "") or "/"}">{e(n)}</a>' if i < len(crumb) - 1 else f"<em>{e(n)}</em>")
        for i, (n, u) in enumerate(crumb))
    subject = label(slug, meta) if kind == "service" else f"Re: {meta['h1']}"
    if kind in ("post", "case"):
        body, toc = add_heading_ids(meta["body"])
        seq, base = (posts, "insights") if kind == "post" else (list(cases), "case-studies")
        idx = next((i for i, p in enumerate(seq) if p["slug"] == slug), 0)
        nxt = seq[idx - 1] if idx > 0 else None
        prv = seq[idx + 1] if idx + 1 < len(seq) else None
        pn = "".join(
            f'<a class="pn {c}" href="/{base}/{p["slug"]}/"><small>{lab}</small><b>{e(p["h1"])}</b></a>'
            for p, lab, c in ((prv, "← Previous", "prev"), (nxt, "Next →", "next")) if p)
        if kind == "case":
            body = glance_html(meta) + body
        toc_html = "".join(f'<li><a href="#{i}">{e(t)}</a></li>' for i, t in toc)
        body_html = f"""<figure class="cover rise">{cover_svg(meta)}</figure>
  <div class="post-wrap">
    <article class="prose article">
      {body}
      {refs_html(meta.get("citations"))}
      {share_html(url, meta["h1"])}
      {AUTHOR_BOX}
      <div class="pnav">{pn}</div>
    </article>
    <aside class="toc" aria-label="On this page"><div class="kicker">On this page</div><ol>{toc_html}</ol>
      <a class="toc-cta" href="{CAL}" target="_blank" rel="noopener">Book a 30-min call →</a></aside>
  </div>"""
    else:
        body_html = f'<article class="prose">\n    {meta["body"]}\n    {refs_html(meta.get("citations"))}\n  </article>'
    return f"""{head(meta['title'], meta['description'], meta['keywords'], url, og, og_type, ld)}
<body class="sub {'is-post' if kind in ('post', 'case') else 'is-service'}{' is-case' if kind == 'case' else ''}">
{nav()}

<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="crumbs" role="navigation" aria-label="Breadcrumb">{bc}</div>
    <div class="kicker">{e(meta['kicker'])}</div>
    <h1>{e(meta['h1'])}</h1>
    <p class="sub-lede">{e(meta['lede'])}</p>
    {meta_line}
    <div class="cta-row">
      <a class="btn mag" href="{CAL}" target="_blank" rel="noopener">Book a 30-min call →</a>
      <a class="btn ghost mag" href="/#assess">Analyse your challenge</a>
    </div>
  </header>

  {body_html}

  {faq_html(meta.get('faq'))}
  {related_html(meta.get('related', []), pages_by_slug, [p for p in posts if p['slug'] != slug], meta.get('tags', []))}
  {cta_html(subject)}
</main>

{modal()}
{footer(pages, posts)}
{SCRIPTS}
</body>
</html>
"""


def series_html(posts):
    items = sorted((p for p in posts if p.get("series") == "Monthly briefing"), key=lambda p: p["slug"])
    if not items:
        return ""
    cells = "".join(
        f'<a class="tl-i rise" href="/insights/{p["slug"]}/"><span class="tl-dot"></span><small>{e(p["period"])}</small>'
        f'<b>{e(p["h1"].split(":", 1)[-1].strip() if ":" in p["h1"] else p["h1"])}</b></a>' for p in items)
    return (f'<section class="series"><div class="kicker">Monthly briefings</div>'
            f'<h2>Six months of AI, platform and data, in one place.</h2><div class="tl">{cells}</div></section>')


def insights_index(pages, posts):
    url = f"{SITE}/insights/"
    title = "Insights on AI, ontology, healthcare data & CTO leadership"
    desc = ("Practical articles by Sumanta Mukhopadhyay on fractional CTO work, ontologies and knowledge graphs, "
            "production RAG and LLMs, FHIR and OMOP, and private AI.")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "name": "Insights", "url": url, "author": person_ref(),
         "blogPost": [{"@type": "BlogPosting", "headline": p["h1"], "url": f"{SITE}/insights/{p['slug']}/",
                       "datePublished": when(p)[0]} for p in posts]},
        crumbs([("Home", f"{SITE}/"), ("Insights", url)])]}
    cards = "".join(post_card(p) for p in posts)
    tagset = sorted({t for p in posts for t in p.get("tags", [])})
    filt = ('<div class="filters" role="group" aria-label="Filter by topic"><button type="button" class="fchip" aria-pressed="true" data-tag="">All</button>'
            + "".join(f'<button type="button" class="fchip" aria-pressed="false" data-tag="{e(t)}">#{e(t)}</button>' for t in tagset)
            + f'<span class="fcount">{len(posts)} articles</span></div>')
    kw = sorted({k for p in posts for k in p["keywords"]})[:30]
    return f"""{head(title + ' | Sumanta', desc, kw, url, f'{SITE}/assets/og/insights.png', 'website', ld)}
<body class="sub">
{nav()}
<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="crumbs" role="navigation" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <em>Insights</em></div>
    <div class="kicker">Insights</div>
    <h1>Notes from the work: AI, ontology, healthcare data and technical leadership.</h1>
    <p class="sub-lede">Practical writing from real architecture problems. No hype, just what I've seen work, what doesn't, and why.</p>
    <p class="rss-line"><a href="/subscribe/"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5" cy="19" r="2.5"/><path d="M3 10.5v3a7.5 7.5 0 0 1 7.5 7.5h3A10.5 10.5 0 0 0 3 10.5zm0-7v3A14.5 14.5 0 0 1 17.5 21h3A17.5 17.5 0 0 0 3 3.5z"/></svg>Subscribe via RSS</a> · new posts in Feedly, Inoreader or any reader</p>
  </header>
  {series_html(posts)}
  {filt}
  <div class="posts">{cards}</div>
  {cta_html('Re: Insights')}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
</body>
</html>
"""


def home_snapshots():
    """The tabbed engagement snapshots from the home page, reused on /case-studies/."""
    f = ROOT / "src/sections/snapshots.html"
    return f.read_text().strip() if f.exists() else ""


def use_cases():
    f = ROOT / "src/use-cases.json"
    return json.loads(f.read_text()) if f.exists() else []


def use_cases_html(ucs):
    if not ucs:
        return ""
    sectors = sorted({u["sector"] for u in ucs})
    chips = ('<div class="filters uc-filters" role="group" aria-label="Filter use cases by sector">'
             '<button type="button" class="ucchip" aria-pressed="true" data-sector="">All sectors</button>'
             + "".join(f'<button type="button" class="ucchip" aria-pressed="false" data-sector="{e(x)}">{e(x)}</button>'
                       for x in sectors) + f'<span class="fcount">{len(ucs)} use cases</span></div>')
    cards = []
    for i, u in enumerate(ucs, 1):
        flow = "".join(f'<li{" class=hl" if j == len(u["flow"]) - 2 else ""}>{e(st)}</li>'
                       for j, st in enumerate(u["flow"]))
        stack = "".join(f'<span class="tag">{e(t)}</span>' for t in u["stack"])
        cards.append(
            f'<article class="uc rise" id="uc-{e(u["id"])}" data-sector="{e(u["sector"])}">'
            f'<div class="uc-top"><span class="uc-n">{i:02d}</span><span class="uc-s">{e(u["sector"])}</span></div>'
            f'<h3>{e(u["title"])}</h3>'
            f'<p class="uc-p"><b>Problem.</b> {e(u["problem"])}</p>'
            f'<p class="uc-a"><b>Approach.</b> {e(u["approach"])}</p>'
            f'<ol class="uc-flow" aria-label="Flow">{flow}</ol>'
            f'<div class="cs-stack">{stack}</div>'
            + (f'<a class="uc-more" href="/case-studies/{e(u["case"])}/">Read the full case study →</a>'
               if u.get("case") and (ROOT / "src/case-studies" / f'{u["case"]}.part').exists()
               else f'<a class="uc-more" href="{e(u["link"])}">Go deeper →</a>')
            + '</article>')
    return f"""<section class="sub-sec" id="use-cases">
    <div class="kicker">Use cases</div>
    <h2>{len(ucs)} problems across {len({u["sector"] for u in ucs})} sectors, one way of working.</h2>
    <p class="sub-lede" style="margin-bottom:24px">Typical use cases I design and build for: the problem, the approach, the flow and the stack. Pick your sector, then book a call to talk through yours.</p>
    {chips}
    <div class="ucs">{"".join(cards)}</div>
  </section>"""


def cases_index(pages, posts, cases):
    url = f"{SITE}/case-studies/"
    title = "Case studies: ontology, AI, healthcare data and scale"
    desc = ("Anonymised case studies by Sumanta Mukhopadhyay: the problem, the architecture, the flow and the "
            "decisions, across AI, ontology, healthcare data, data platforms and cloud.")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "Case studies", "url": url, "author": person_ref(), "description": desc,
         "hasPart": [{"@type": "Article", "headline": c["h1"], "url": f"{SITE}/case-studies/{c['slug']}/",
                      "datePublished": when(c)[0]} for c in cases]},
        {"@type": "ItemList", "name": "Use cases", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": u["title"], "description": u["problem"],
             "url": f"{url}#uc-{u['id']}"} for i, u in enumerate(use_cases())]},
        crumbs([("Home", f"{SITE}/"), ("Case studies", url)])]}
    cards = "".join(case_card(c) for c in cases)
    tagset = sorted({t for c in cases for t in c.get("tags", [])})
    filt = ('<div class="filters" role="group" aria-label="Filter by topic"><button type="button" class="fchip" aria-pressed="true" data-tag="">All</button>'
            + "".join(f'<button type="button" class="fchip" aria-pressed="false" data-tag="{e(t)}">#{e(t)}</button>' for t in tagset)
            + f'<span class="fcount">{len(cases)} in-depth</span></div>') if len(cases) > 1 else ""
    stack = sorted({t for c in cases for t in c.get("stack", [])})
    kw = sorted({k for c in cases for k in c["keywords"]})[:30]
    snaps = home_snapshots()
    ucs = use_cases()
    snap_sec = f"""<section class="sub-sec" id="snapshots">
    <div class="kicker">Engagement snapshots</div>
    <h2>Five problems I'm regularly brought in to solve.</h2>
    <p class="sub-lede" style="margin-bottom:28px">Short form: the challenge, the approach, the architecture and the result, one tab each.</p>
    {snaps}
    <p class="note">Client names, figures and specifics are withheld under confidentiality. Detailed references available on request.</p>
  </section>""" if snaps else ""
    return f"""{head(title + ' | Sumanta', desc, kw, url, f'{SITE}/assets/og/case-studies.png', 'website', ld)}
<body class="sub is-cases">
{nav()}
<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="crumbs" role="navigation" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <em>Case studies</em></div>
    <div class="kicker">Case studies</div>
    <h1>The problem, the architecture, the flow, and the decisions behind it.</h1>
    <p class="sub-lede">Anonymised, composite case studies from the kinds of engagements I lead across healthcare, fintech, SaaS, e-commerce and AI. No logos and no confidential numbers: just how each system was designed, how the data flows, and why.</p>
    <div class="cs-stats">
      <div><b>{len(cases)}</b><small>in-depth case studies</small></div>
      <div><b>{len(ucs)}</b><small>use cases</small></div>
      <div><b>{len(pages)}</b><small>practice areas</small></div>
      <div><b>{len(stack)}</b><small>technologies in play</small></div>
    </div>
    <div class="cta-row">
      <a class="btn mag" href="{CAL}" target="_blank" rel="noopener">Book a 30-min call →</a>
      <a class="btn ghost mag" href="#use-cases">Browse {len(ucs)} use cases</a>
    </div>
  </header>

  <section class="sub-sec" id="in-depth">
    <div class="kicker">In depth</div>
    <h2>Full case studies, with architecture and flow diagrams.</h2>
    {filt}
    <div class="posts">{cards}</div>
  </section>

  {use_cases_html(ucs)}

  {snap_sec}

  <section class="sub-sec">
    <div class="kicker">How engagements run</div>
    <h2>From first call to hand-off.</h2>
    <figure class="dgm">
      <div class="dgm-phases">
        <div><small>Step 1</small><b>Free 30-minute call</b><ul><li>Your goals and constraints</li><li>Whether I'm the right fit</li></ul></div>
        <div><small>Step 2</small><b>Review</b><ul><li>Architecture and data review</li><li>Risks and quick wins</li><li>Written recommendation</li></ul></div>
        <div><small>Step 3</small><b>Build or lead</b><ul><li>Hands-on build, or</li><li>Fractional CTO leadership</li></ul></div>
        <div><small>Step 4</small><b>Hand-off</b><ul><li>Runbooks and decision records</li><li>Your team owns it</li></ul></div>
      </div>
      <figcaption>Every engagement starts with the problem, not a proposal.</figcaption>
    </figure>
  </section>
  {cta_html('Re: Case studies')}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
<script>
(function(){{var cs=[].slice.call(document.querySelectorAll('.ucchip')),cards=[].slice.call(document.querySelectorAll('.uc'));
  cs.forEach(function(c){{c.addEventListener('click',function(){{var s=c.getAttribute('data-sector');
    cs.forEach(function(x){{x.setAttribute('aria-pressed',x===c);}});
    cards.forEach(function(k){{k.hidden=!!s&&k.getAttribute('data-sector')!==s;}});}});}});
}})();
(function(){{var list=document.getElementById('csTabs');if(!list)return;
  var ts=[].slice.call(list.querySelectorAll('[role=tab]'));
  function sel(i,f){{ts.forEach(function(t,j){{var on=j===i;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!on;}});if(f)ts[i].focus();}}
  ts.forEach(function(t,i){{t.addEventListener('click',function(){{sel(i);}});
    t.addEventListener('keydown',function(e){{var k={{ArrowRight:1,ArrowDown:1,ArrowLeft:-1,ArrowUp:-1}}[e.key];if(k){{e.preventDefault();sel((i+k+ts.length)%ts.length,true);}}}});}});
}})();
</script>
</body>
</html>
"""


def privacy_page(pages, posts):
    url = f"{SITE}/privacy/"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": "Privacy and cookies", "url": url, "dateModified": "2026-10-28"},
        crumbs([("Home", f"{SITE}/"), ("Privacy and cookies", url)])]}
    return f"""{head("Privacy and cookies | Sumanta Mukhopadhyay", "How asksumanta.com uses cookies and Google Analytics, what is collected, and how to change your choice.", [], url, f"{SITE}/assets/og/home.png", "website", ld)}
<body class="sub">
{nav()}
<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="crumbs" role="navigation" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <em>Privacy and cookies</em></div>
    <div class="kicker">Privacy</div>
    <h1>Privacy and cookies</h1>
    <p class="sub-lede">This site is a personal portfolio. It has no accounts and no forms, and it never asks for or stores your name or email. Last updated 28 October 2026.</p>
  </header>
  <article class="prose">
    <h2>What is collected</h2>
    <p>With your consent, the site uses Google Analytics 4 to understand how it is used: pages viewed, how far you scroll, which links and buttons you use (for example booking a call, opening an article or answering the challenge assessor), approximate location at country or city level, device and browser type, and how you arrived. This data is anonymous to me: I cannot see who you are.</p>
    <p>No personal information such as names, email addresses or phone numbers is sent to Google Analytics. Advertising features and ad personalisation are switched off.</p>
    <h2>Cookies and local storage</h2>
    <table class="tbl">
      <thead><tr><th>Name</th><th>Set by</th><th>Purpose</th><th>Duration</th></tr></thead>
      <tbody>
        <tr><td><code>_ga</code></td><td>Google Analytics</td><td>Distinguishes anonymous visitors</td><td>Up to 2 years</td></tr>
        <tr><td><code>_ga_8TKBV1S98Q</code></td><td>Google Analytics</td><td>Keeps session state</td><td>Up to 2 years</td></tr>
        <tr><td><code>consent</code> (local storage)</td><td>This site</td><td>Remembers your cookie choice</td><td>Until you clear it</td></tr>
        <tr><td><code>theme</code> (local storage)</td><td>This site</td><td>Remembers light or dark mode</td><td>Until you clear it</td></tr>
      </tbody>
    </table>
    <p>Analytics cookies are only set after you accept them. If you are in the European Economic Area, the United Kingdom or Switzerland, analytics is off until you choose to allow it. Elsewhere it is on by default and you can switch it off at any time.</p>
    <h2>Your choice</h2>
    <p>You can change your choice whenever you like: <button type="button" class="lnk cookie-link" data-cookie-settings>open cookie settings</button>. Rejecting analytics has no effect on how the site works.</p>
    <h2>Third parties</h2>
    <p>Booking a call takes you to Google Calendar's appointment page, and writing to me opens your own email client or Gmail. Those services have their own privacy policies. Fonts are loaded from Google Fonts and scripts from public CDNs, which may see your IP address when they deliver files.</p>
    <h2>Contact</h2>
    <p>Questions about privacy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </article>
  {cta_html('Privacy question')}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
</body>
</html>
"""


PLAY_FAQ = [
    ("What is Orbital Ops?", "A free browser arcade game on this site. You pilot a ship defending a production system from incidents such as latency spikes, memory leaks, schema drift, traffic floods and prompt injections, with a legacy monolith boss every fifth wave."),
    ("How do I play?", "Move with the mouse, a finger, the arrow keys or WASD. Firing is automatic. Collect power-ups, keep your streak for a higher multiplier and protect your error budget of three hits. Press P to pause."),
    ("Does it work on phones?", "Yes. It runs in any modern browser on desktop, tablet or phone, with touch controls. Nothing is installed and no account is needed; your best score is kept only in your own browser."),
    ("Is the music real?", "The ambient soundtrack is generated live in your browser with the Web Audio API, so there is nothing to download. It stays off until you switch it on with the sound button."),
]

PLAY_GUIDE = [
    ("latency", "Latency spike", "#ffcf5a", "Fast and fragile. In production, you catch these with service level objectives and error budgets.", "/insights/slos-error-budgets-small-teams/", "SLOs and error budgets"),
    ("leak", "Memory leak", "#8ab8ff", "Slow, tough and grows the longer you ignore it. Right-sizing workloads helps.", "/insights/kubernetes-in-place-pod-resize/", "In-place pod resize"),
    ("drift", "Schema drift", "#5ae0ff", "Zigzags unpredictably, like an upstream schema nobody agreed. Contracts stop it.", "/insights/data-contracts-playbook/", "Data contracts"),
    ("ddos", "Traffic flood", "#ff7a59", "Splits into fragments when hit. Gateways and rate limits keep floods manageable.", "/insights/kubernetes-inference-gateway/", "Inference gateways"),
    ("inject", "Prompt injection", "#ff4f8b", "Homes in on you, the way hostile input targets an AI agent's tools.", "/insights/prompt-injection-defence-for-agents/", "Prompt injection defence"),
    ("mono", "Legacy monolith", "#4c8dff", "The boss every fifth wave. Heavily armoured and fires back. Decisions, not heroics, retire it.", "/insights/architecture-decision-records-fractional-cto/", "Architecture decision records"),
]


def play_page(pages, posts):
    url = f"{SITE}/play/"
    title = "Orbital Ops: a free space arcade game about production incidents"
    desc = "Play Orbital Ops, a free sci-fi browser game: defend production from latency spikes, memory leaks and prompt injections. Works on desktop and mobile."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": ["VideoGame", "WebApplication"], "@id": f"{url}#game", "name": "Orbital Ops", "url": url, "description": desc,
         "image": f"{SITE}/assets/og/play.png", "genre": ["Arcade", "Shoot 'em up", "Science fiction"], "gamePlatform": "Web browser",
         "applicationCategory": "GameApplication", "operatingSystem": "Any", "playMode": "SinglePlayer", "inLanguage": "en-GB",
         "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "author": person_ref(), "publisher": person_ref()},
        {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc, "mainEntity": {"@id": f"{url}#game"},
         "isPartOf": {"@type": "WebSite", "url": f"{SITE}/", "name": NAME}, "dateModified": TODAY},
        crumbs([("Home", f"{SITE}/"), ("Play", url)]), faq_ld(PLAY_FAQ)]}
    guide = "".join(f'<div><b><i style="--c:{c}"></i>{e(n)}</b><p>{e(d)}</p><a href="{u}">{e(l)} →</a></div>'
                    for _, n, c, d, u, l in PLAY_GUIDE)
    h = head(title, desc, ["browser game", "free online space game", "sci-fi arcade game", "HTML5 canvas game", "developer game",
                           "SRE game", "incident response game", "play online no download"], url, f"{SITE}/assets/og/play.png", "website", ld)
    return f"""{h}
<body class="sub">
{nav()}
<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="crumbs" role="navigation" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <em>Play</em></div>
    <div class="kicker">Arcade · Orbital Ops</div>
    <h1>Orbital Ops: defend production from incoming incidents</h1>
    <p class="sub-lede">A free sci-fi arcade game that runs in your browser. Shoot down latency spikes, memory leaks and prompt injections, survive the legacy monolith, and protect your error budget. Switch on the ambient soundtrack with the sound button.</p>
  </header>
  <section class="arc" aria-label="Orbital Ops game">
    <div class="arc-hud">
      <span>Score<b id="arcScore">0</b></span><span>Wave<b id="arcWave">0</b></span><span>Streak<b id="arcMult">×1</b></span>
      <span>Error budget<i class="arc-bud" id="arcBudget" role="img" aria-label="Error budget 3 of 3"></i></span>
      <span class="sp"></span><span>Best<b id="arcBest">0</b></span>
      <button type="button" id="arcPause" aria-pressed="false">Pause</button>{SOUND}
    </div>
    <div class="arc-stage" id="arcStage" data-cal="{CAL}">
      <canvas role="img" aria-label="Orbital Ops play area: a ship at the bottom shoots incidents falling from the top"></canvas>
      <div class="arc-screen" id="arcScreen" aria-live="polite"></div>
    </div>
  </section>
  <article class="prose">
    <h2>How to play</h2>
    <p>Move your ship with the mouse, a finger, the arrow keys or WASD. Firing is automatic, so you can focus on dodging. Every eight incidents you clear without letting one escape raises your streak multiplier, up to eight times. Each hit spends one point of your error budget; lose all three and the game ends. Press P to pause at any time.</p>
    <h2>Power-ups</h2>
    <ul>
      <li><strong>Autoscale</strong>: triple shot for a few seconds.</li>
      <li><strong>Observability</strong>: slows incoming incidents so you can see what is happening.</li>
      <li><strong>Circuit breaker</strong>: a shield that absorbs one hit.</li>
      <li><strong>Rollback</strong>: restores one point of error budget.</li>
    </ul>
    <h2>Incident field guide</h2>
    <p>Every enemy is a real class of production problem. When one takes you down, the game links to how to handle it for real.</p>
  </article>
  <div class="arc-guide">{guide}</div>
  {faq_html(PLAY_FAQ)}
  {cta_html('Orbital Ops')}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
<script src="/assets/arcade.js" defer></script>
</body>
</html>
"""


HUB_PAGES = {
    "how-i-work": {
        "name": "How I work", "kicker": "Process",
        "title": "How I work: engagement models and approach | Sumanta Mukhopadhyay",
        "description": "How a fractional CTO and AI architect engagement runs: a playbook for common problems, working principles, engagement models, how to connect, and FAQs.",
        "h1": "How I work: from first conversation to a team that runs it",
        "lede": "The problems I'm usually brought in to solve, how I approach them, the ways we can work together, and what happens after you get in touch.",
        "sections": ["playbook", "approach", "engage", "connect", "faq"]},
    "expertise": {
        "name": "Expertise", "kicker": "Practice",
        "title": "Expertise: AI, ontology, data platforms and cloud | Sumanta Mukhopadhyay",
        "description": "Six practice areas, a reference architecture, systems built for scale, industries served and the nine-layer stack I work across, from ontology to infrastructure.",
        "h1": "Expertise across the whole stack, from the ontology to the infrastructure",
        "lede": "Strategy, applied AI, semantic architecture, data platforms, cloud and product engineering, with the reference architecture and industries behind them.",
        "sections": ["practice", "architecture", "scale", "industries", "capabilities", "languages"]},
    "about": {
        "name": "About", "kicker": "Background",
        "title": "About Sumanta Mukhopadhyay: fractional CTO and AI architect",
        "description": "Background, experience and credentials of Sumanta Mukhopadhyay, fractional CTO, principal engineer and AI architect based in India, the United States and the UAE.",
        "h1": "About Sumanta: principal engineer, fractional CTO and AI architect",
        "lede": "Experience across AI, data and infrastructure, published research, open-source work, and the hardware I'm experimenting on right now.",
        "sections": ["experience", "credentials", "now"]},
}


SECTION_LABELS = {"playbook": "Playbook", "approach": "Principles", "engage": "Engagement models", "connect": "How to connect",
                  "faq": "FAQ", "practice": "Practice areas", "architecture": "Reference architecture", "scale": "At scale",
                  "industries": "Industries", "capabilities": "The stack", "languages": "Languages",
                  "experience": "Experience", "credentials": "Credentials", "now": "Now"}


REGION_ORDER = ["North America", "Europe", "Middle East", "Asia", "Asia-Pacific"]


def regions_page(pages, posts):
    url = f"{SITE}/regions/"
    title = "Fractional CTO & AI Architect Worldwide | Sumanta Mukhopadhyay"
    desc = ("Fractional CTO and AI architect for teams in the US, UK, Europe, UAE, Saudi Arabia, India, Singapore and "
            "Australia: remote-first, with the local rules built in.")

    def nm(r):
        return "Europe (EU)" if r["country"] == "European Union" else r["country"]
    cards = "".join(
        f'<a class="rg rise" href="/{r["slug"]}/"><div class="rg-meta"><span>{e(r["region"])}</span>'
        f'<span class="rg-clock" data-tz="{e(r["tz"])}">--:--</span></div>'
        f'<b>{e(nm(r))}</b><p>{e(r["description"])}</p>'
        f'<div class="rg-chips">{"".join(f"<i>{e(c)}</i>" for c in r.get("chips", []))}</div>'
        f'<span class="rg-go">Explore {e(nm(r))} <em>→</em></span></a>' for r in REGIONS)
    zones = "".join(f'<div class="tz-row"><span class="tz-c">{e(r["city"])}</span><div class="tz-bar" data-tz="{e(r["tz"])}">'
                    f'<i class="tz-on"></i><i class="tz-on tz-w"></i></div></div>' for r in REGIONS)
    ticks = "".join(f'<span style="left:{h / 24 * 100:.4f}%">{h:02d}:00</span>' for h in range(0, 24, 3))
    wm = json.loads((ROOT / "src/world-pins.json").read_text())
    dots = '<div class="wm-dots" aria-hidden="true"></div>'
    pins = "".join(
        f'<a class="wm-pin{" wm-l" if r["tz"] in ("Europe/London", "Asia/Riyadh", "Australia/Sydney") else ""}{" wm-base" if r["tz"] in ("America/New_York", "Asia/Dubai", "Asia/Kolkata") else ""}" href="/{r["slug"]}/" style="left:{wm["pins"][r["tz"]][0]}%;top:{wm["pins"][r["tz"]][1]}%">'
        f'<i></i><span><b>{e(nm(r))}</b><em class="rg-clock" data-tz="{e(r["tz"])}">--:--</em></span></a>'
        for r in REGIONS if r["tz"] in wm["pins"])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": title, "description": desc, "dateModified": TODAY,
         "hasPart": [{"@type": "WebPage", "name": label(r["slug"]), "url": f"{SITE}/{r['slug']}/"} for r in REGIONS]},
        {"@type": "ProfessionalService", "name": f"{NAME}: Fractional CTO & AI Architecture", "url": url,
         "provider": person_ref(), "areaServed": AREAS_SERVED},
        crumbs([("Home", f"{SITE}/"), ("Worldwide", url)])]}
    kw = ["fractional CTO worldwide", "global fractional CTO", "remote fractional CTO", "AI architect worldwide",
          "fractional CTO USA", "fractional CTO UK", "fractional CTO Europe", "fractional CTO India",
          "fractional CTO Dubai", "fractional CTO Singapore", "fractional CTO Australia"]
    return f"""{head(title, desc, kw, url, f"{SITE}/assets/og/regions.png", "website", ld)}
<body class="sub hub">
{nav()}
<main class="wrap">
  <header class="sub-hero rg-hero">
    <div class="rg-hero-t">
      <div class="crumbs" role="navigation" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <em>Worldwide</em></div>
      <div class="kicker">Worldwide · remote-first</div>
      <h1>A fractional CTO and AI architect for teams anywhere</h1>
      <p class="sub-lede">The engineering is the same everywhere. The rules, time zones and buyers are not. I work with founders, enterprises and investors across {len(REGIONS)} markets, with each market's regulation built into the architecture from day one.</p>
      <div class="cta-row"><a class="btn mag" href="{CAL}" target="_blank" rel="noopener">Book a 30-min call →</a><a class="btn ghost mag" href="#markets">Find your region</a></div>
    </div>
  </header>
  <figure class="wm" aria-label="Map of the markets I work in, with local times">
    <div class="wm-in">{dots}{pins}</div>
    <figcaption><span><i class="wm-k wm-kb"></i>Bases: India, United States, UAE <i class="wm-k"></i>Markets with a dedicated page</span><span>Times are live local time · based in India, the US &amp; UAE</span></figcaption>
  </figure>
  <section class="rg-sec" id="markets">
    <div class="sec-head"><div><div class="kicker">Markets</div><h2>Pick your region</h2></div>
    <p>Each page covers who I work with there, the rules that shape the architecture, typical first projects and how time zones work.</p></div>
    <div class="rg-grid">{cards}</div>
  </section>
  <section class="rg-sec rise" aria-labelledby="tzh">
    <div class="sec-head"><div><div class="kicker">Live working hours</div><h2 id="tzh">Where it's office hours right now</h2></div>
    <p>Office hours (9:00 to 18:00) in each city, shown on your own clock. The red line is now. Most markets share several hours a day with each other.</p></div>
    <div class="tz"><div class="tz-axis"><span class="tz-c"></span><div class="tz-ticks">{ticks}</div></div>{zones}<div class="tz-nowrow"><span class="tz-c"></span><div class="tz-track"><i class="tz-now"></i></div></div></div>
  </section>
  {cta_html("Worldwide enquiry")}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
</body>
</html>
"""


def hub_page(slug, pages, posts):
    m = HUB_PAGES[slug]
    url = f"{SITE}/{slug}/"
    body = "\n".join((ROOT / f"src/sections/{k}.html").read_text() for k in m["sections"])
    body = body.replace('href="#assess"', 'href="/#assess"')
    graph = [{"@type": "WebPage", "@id": url, "url": url, "name": m["title"], "description": m["description"],
              "isPartOf": {"@type": "WebSite", "url": f"{SITE}/", "name": NAME}, "dateModified": TODAY,
              "about": person_ref()},
             crumbs([("Home", f"{SITE}/"), (m["name"], url)])]
    if slug == "about":
        graph[0]["@type"] = "AboutPage"
        graph[0]["mainEntity"] = person_ref()
    faq = [(re.sub(r"<[^>]+>", "", q), re.sub(r"<[^>]+>", "", a)) for q, a in
           re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", body, re.S)]
    if faq:
        graph.append(faq_ld([(html.unescape(q), html.unescape(a)) for q, a in faq]))
    ld = {"@context": "https://schema.org", "@graph": graph}
    secnav = "".join(f'<a href="#{k}">{SECTION_LABELS.get(k, k.title())}</a>' for k in m["sections"])
    cur = ' aria-current="page"'
    hubs = "".join(f'<a href="/{k}/"{cur if k == slug else ""}>{e(v["name"])}</a>' for k, v in HUB_PAGES.items())
    return f"""{head(m["title"], m["description"], [], url, f"{SITE}/assets/og/{slug}.png", "website", ld)}
<body class="sub hub">
{nav()}
<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="crumbs" role="navigation" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <em>{e(m["name"])}</em></div>
    <div class="kicker">{e(m["kicker"])}</div>
    <h1>{e(m["h1"])}</h1>
    <p class="sub-lede">{e(m["lede"])}</p>
    <div class="hub-nav" aria-label="More about this practice">{hubs}<a href="/case-studies/">Case studies</a><a href="/play/">Play</a></div>
  </header>
  <div class="subnav" aria-label="On this page"><div class="subnav-in"><span class="subnav-k">On this page</span>{secnav}</div></div>
{body}
  {cta_html(m["name"])}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
<script src="/assets/home.js" defer></script>
</body>
</html>
"""


def not_found(pages, posts):
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Page not found"}
    links = "".join(f'<a class="svc" href="/{p["slug"]}/"><b>{e(SERVICE_LABELS.get(p["slug"], p["h1"]))}</b><i>→</i></a>'
                    for p in pages)
    h = head("Page not found | Sumanta Mukhopadhyay", "This page doesn't exist. Find services, case studies and insights instead.",
             [], f"{SITE}/404.html", f"{SITE}/assets/og/home.png", "website", ld)
    h = h.replace('<meta name="robots" content="index, follow, max-image-preview:large" />', '<meta name="robots" content="noindex" />')
    return f"""{h}
<body class="sub">
{nav()}
<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="kicker">404</div>
    <h1>This node isn't in the graph.</h1>
    <p class="sub-lede">The page you were looking for doesn't exist or has moved. Here's where you probably wanted to go.</p>
    <div class="cta-row"><a class="btn mag" href="/">Back to home →</a><a class="btn ghost mag" href="/insights/">Read the insights</a></div>
    <div class="svcs">{links}</div>
  </header>
  {cta_html('Engagement enquiry')}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
</body>
</html>
"""


def update_home(pages, posts, cases=()):
    p = ROOT / "index.html"
    s = p.read_text()
    cards = "".join(post_card(q, "h3") for q in posts[:4])
    svc = "".join(
        f'<a class="svc rise" href="/{q["slug"]}/"><b>{e(SERVICE_LABELS.get(q["slug"], q["h1"]))}</b><i>→</i></a>'
        for q in pages if q["slug"] != "uae")
    svc += '<a class="svc rise" href="/regions/"><b>Fractional CTO worldwide</b><i>→</i></a>'
    strip = ('<div class="rstrip rise"><span>Working with teams in</span>'
             + "".join(f'<a href="/{r["slug"]}/">{e(r["country"] if r["country"] != "European Union" else "Europe")}</a>' for r in REGIONS)
             + "</div>")
    blocks = {"NAV": nav(), "INSIGHTS": f'<div class="posts">{cards}</div>', "SERVICES": f'<div class="svcs">{svc}</div>{strip}',
              "FOOTER": footer(pages, posts)}
    if cases:
        ccards = "".join(case_card(c, "h3") for c in list(cases)[:4])
        blocks["CASES"] = (f'<div class="cs-more"><div class="kicker">In depth</div>'
                           f'<div class="posts">{ccards}</div>'
                           f'<a class="lnk" href="/case-studies/">All case studies, with architecture and flow diagrams →</a></div>')
    for k, v in blocks.items():
        s, n = re.subn(rf"<!-- {k}:START -->.*?<!-- {k}:END -->", f"<!-- {k}:START -->\n{v}\n<!-- {k}:END -->", s,
                       flags=re.S)
        if n != 1:
            raise SystemExit(f"index.html: marker {k} not found")
    p.write_text(s)


FEEDS = [("/feed.xml", "Everything", "All insights and case studies"),
         ("/insights/feed.xml", "Insights", "Articles on AI, data, cloud and technology leadership"),
         ("/insights/news.xml", "Daily tech news", "A CTO's take on the day's releases, deals and rules"),
         ("/case-studies/feed.xml", "Case studies", "Anonymised engagements with architecture and flow diagrams")]


def rfc822(meta):
    iso = meta.get("datetime") or (meta.get("date", TODAY) + "T09:00:00+04:00")
    return datetime.datetime.fromisoformat(iso).strftime("%a, %d %b %Y %H:%M:%S %z")


def write_feed(path, title, desc, items):
    """RSS 2.0 with full content, absolute links and a browser-friendly stylesheet."""
    url = f"{SITE}{path}"
    def item(m, base):
        link = f"{SITE}/{base}/{m['slug']}/"
        body = re.sub(r'(href|src)="/', rf'\1="{SITE}/', m["body"]).replace("]]>", "]]&gt;")
        cats = "".join(f"<category>{e(t)}</category>" for t in m.get("tags", []))
        return (f"<item><title>{e(m['h1'])}</title><link>{link}</link><guid isPermaLink=\"true\">{link}</guid>"
                f"<pubDate>{rfc822(m)}</pubDate><dc:creator>{NAME}</dc:creator>{cats}"
                f"<description>{e(m['description'])}</description>"
                f"<content:encoded><![CDATA[<p><em>{e(m['lede'])}</em></p>{body}"
                f"<p><a href=\"{link}\">Read on asksumanta.com</a> for diagrams, references and related reading.</p>]]></content:encoded></item>")
    latest = rfc822(items[0][0]) if items else rfc822({})
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/xsl" href="/assets/feed.xsl"?>\n'
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" '
           'xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>'
           f'<title>{e(NAME)}: {e(title)}</title><link>{SITE}/</link><description>{e(desc)}</description>'
           f'<language>en-gb</language><lastBuildDate>{latest}</lastBuildDate>'
           f'<atom:link href="{url}" rel="self" type="application/rss+xml"/>'
           f'<image><url>{SITE}/assets/apple-touch-icon.png</url><title>{e(NAME)}: {e(title)}</title><link>{SITE}/</link></image>'
           + "".join(item(m, b) for m, b in items[:50]) + "</channel></rss>\n")
    out = ROOT / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml)


def subscribe_page(pages, posts):
    url = f"{SITE}/subscribe/"
    title = "Subscribe via RSS | Sumanta Mukhopadhyay"
    desc = "Follow new insights, case studies and the daily tech news in any RSS reader, such as Feedly, Inoreader or NetNewsWire. Free, private, no email needed."
    rows = "".join(
        f'<div class="feed rise"><div><b>{e(t)}</b><span>{e(d)}</span><code>{SITE}{p}</code></div>'
        f'<div class="feed-a"><button type="button" class="btn sm" data-copy="{SITE}{p}">Copy URL</button>'
        f'<a class="btn ghost sm" href="https://feedly.com/i/subscription/feed/{quote(SITE + p, safe="")}" target="_blank" rel="noopener">Feedly</a>'
        f'<a class="btn ghost sm" href="https://www.inoreader.com/?add_feed={quote(SITE + p, safe="")}" target="_blank" rel="noopener">Inoreader</a>'
        f'<a class="btn ghost sm" href="{p}">View</a></div></div>' for p, t, d in FEEDS)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc, "dateModified": TODAY},
        crumbs([("Home", f"{SITE}/"), ("Subscribe", url)])]}
    return f"""{head(title, desc, ["RSS feed", "subscribe", "tech news RSS", "AI news feed", "CTO blog RSS"], url, f"{SITE}/assets/og/insights.png", "website", ld)}
<body class="sub">
{nav()}
<main class="wrap">
  <header class="sub-hero">
    <canvas class="sub-graph" aria-hidden="true"></canvas>
    <div class="crumbs" role="navigation" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <em>Subscribe</em></div>
    <div class="kicker">Subscribe · RSS</div>
    <h1>Get every new post in your feed reader</h1>
    <p class="sub-lede">Free, private and instant: no email address, no tracking, unsubscribe any time. Pick a feed below and add it to the reader you already use.</p>
  </header>
  <section class="feeds">{rows}</section>
  <article class="prose">
    <h2>How to subscribe</h2>
    <ol>
      <li><strong>Choose a reader.</strong> Feedly and Inoreader work in any browser and on phones. NetNewsWire (Mac and iPhone), Reeder and Thunderbird are good apps; Outlook can also read RSS.</li>
      <li><strong>Add the feed.</strong> Use the Feedly or Inoreader button, or press <em>Copy URL</em> and paste it into your reader's "Add feed" or "Follow" box.</li>
      <li><strong>Done.</strong> New insights, case studies and the daily tech news appear automatically as they are published.</li>
    </ol>
    <p>Most readers will also find the feeds if you paste in <code>{SITE}</code> itself. Each feed carries the full text of the latest 50 posts; diagrams and references are best viewed on the site.</p>
  </article>
  {cta_html('Subscribe')}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
</body>
</html>
"""


def stamp_assets():
    """Append a content hash to CSS/JS URLs in every page so browsers never mix new HTML with cached old assets."""
    import hashlib
    names = ["site.css", "site.js", "home.js", "arcade.js"]
    ver = {n: hashlib.sha1((ROOT / "assets" / n).read_bytes()).hexdigest()[:10] for n in names if (ROOT / "assets" / n).exists()}
    pat = re.compile(r'/assets/(' + "|".join(re.escape(n) for n in ver) + r')(\?v=[0-9a-f]+)?"')
    for f in ROOT.rglob("*.html"):
        if any(part.startswith(".") or part in ("node_modules", "src") for part in f.relative_to(ROOT).parts):
            continue
        t = f.read_text()
        n = pat.sub(lambda m: f'/assets/{m.group(1)}?v={ver[m.group(1)]}"', t)
        if n != t:
            f.write_text(n)


def main():
    pages = [load(f) for f in sorted((ROOT / "src/pages").glob("*.part"))]
    order = list(SERVICE_LABELS)
    pages.sort(key=lambda m: order.index(m["slug"]) if m["slug"] in order else 99)
    posts = [load(f) for f in sorted((ROOT / "src/insights").glob("*.part"))]
    posts.sort(key=sort_key, reverse=True)
    regions = [load(f) for f in sorted((ROOT / "src/regions").glob("*.part"))]
    REGIONS[:] = sorted([m for m in pages if m.get("country")] + regions,
                        key=lambda r: (REGION_ORDER.index(r["region"]), r["country"]))
    by_slug = {m["slug"]: m for m in pages + regions}
    cases = [load(f) for f in sorted((ROOT / "src/case-studies").glob("*.part"))]
    cases.sort(key=sort_key, reverse=True)
    CASES[:] = cases
    NAV_POSTS[:] = posts
    for m in cases:
        m.setdefault("format", "case-study")

    for m in pages + regions:
        out = ROOT / m["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page(m, "service", pages, posts, by_slug))
    for m in posts:
        out = ROOT / "insights" / m["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(m, "post", pages, posts, by_slug))
    (ROOT / "insights").mkdir(exist_ok=True)
    (ROOT / "insights/index.html").write_text(insights_index(pages, posts))
    for m in cases:
        out = ROOT / "case-studies" / m["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(m, "case", pages, posts, by_slug, cases))
    if cases:
        (ROOT / "case-studies/index.html").write_text(cases_index(pages, posts, cases))
    update_home(pages, posts, cases)
    (ROOT / "404.html").write_text(not_found(pages, posts))
    (ROOT / "privacy").mkdir(exist_ok=True)
    (ROOT / "privacy/index.html").write_text(privacy_page(pages, posts))
    (ROOT / "regions").mkdir(exist_ok=True)
    (ROOT / "regions/index.html").write_text(regions_page(pages, posts))
    for k in HUB_PAGES:
        (ROOT / k).mkdir(exist_ok=True)
        (ROOT / k / "index.html").write_text(hub_page(k, pages, posts))
    (ROOT / "play").mkdir(exist_ok=True)
    (ROOT / "play/index.html").write_text(play_page(pages, posts))

    urls = [("/", "1.0", "monthly"), ("/insights/", "0.8", "weekly"), ("/privacy/", "0.2", "yearly"), ("/play/", "0.5", "monthly")]
    urls += [(f"/{k}/", "0.8", "monthly") for k in HUB_PAGES] + [("/regions/", "0.8", "monthly"), ("/subscribe/", "0.4", "monthly")]
    urls += [(f"/{m['slug']}/", "0.8", "monthly") for m in regions]
    urls += [(f"/{m['slug']}/", "0.9", "monthly") for m in pages]
    # Articles report their own publish date; listing and service pages report the latest content date.
    newest = max([m.get("date", TODAY) for m in posts + cases] or [TODAY])
    urls = [(u, pr, c, newest) for u, pr, c in urls]
    urls += [(f"/insights/{m['slug']}/", "0.7", "yearly", m.get("date", newest)) for m in posts]
    if cases:
        urls += [("/case-studies/", "0.8", "weekly", newest)]
        urls += [(f"/case-studies/{m['slug']}/", "0.8", "yearly", m.get("date", newest)) for m in cases]
    sm = "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{lm}</lastmod><changefreq>{c}</changefreq>"
                 f"<priority>{pr}</priority></url>\n" for u, pr, c, lm in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + sm + "</urlset>\n")

    idx = [{"t": "Home", "u": "/", "k": "Page", "d": "Fractional CTO, principal engineer and AI architect"}]
    idx += [{"t": v["name"], "u": f"/{k}/", "k": "Page", "d": v["lede"]} for k, v in HUB_PAGES.items()]
    idx += [{"t": "Orbital Ops", "u": "/play/", "k": "Game", "d": "Free sci-fi browser game: defend production from incidents"},
            {"t": "Analyse your challenge", "u": "/#assess", "k": "Tool", "d": "Four questions, a first diagnosis"},
            {"t": "Case studies", "u": "/case-studies/", "k": "Page", "d": "All case studies"},
            {"t": "Insights", "u": "/insights/", "k": "Page", "d": "All articles"},
            {"t": "Book a call", "u": CAL, "k": "Contact", "d": "Free 30-minute introductory call"}]
    idx += [{"t": SERVICE_LABELS.get(m["slug"], m["h1"]), "u": f"/{m['slug']}/", "k": "Service", "d": m["description"]} for m in pages]
    idx += [{"t": "Fractional CTO worldwide", "u": "/regions/", "k": "Region", "d": "All regions and live working hours"}]
    idx += [{"t": label(m["slug"]), "u": f"/{m['slug']}/", "k": "Region", "d": m["description"], "g": " ".join(m.get("chips", []) + m.get("keywords", []))} for m in regions]
    idx += [{"t": m["h1"], "u": f"/case-studies/{m['slug']}/", "k": "Case study", "d": m["description"], "g": " ".join(m.get("tags", []))} for m in cases]
    idx += [{"t": m["h1"], "u": f"/insights/{m['slug']}/", "k": "Insight", "d": m["description"], "g": " ".join(m.get("tags", []))} for m in posts]
    (ROOT / "assets/search.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))

    llms = [f"# {NAME}", "",
            "> Fractional CTO, principal engineer and AI architect based in India, the United States and the UAE, working with teams across North America, Europe, the Middle East and Asia-Pacific. "
            "Ontology and knowledge graphs, production RAG and agentic AI, private LLMs, healthcare data (FHIR, OMOP, "
            "HIPAA), scalable data platforms (1M+ transactions/day) and multi-cloud infrastructure.", "",
            f"Contact: {EMAIL} · Book a call: {CAL}", "", "## Services"]
    llms += [f"- [{SERVICE_LABELS.get(m['slug'], m['h1'])}]({SITE}/{m['slug']}/): {m['description']}" for m in pages]
    llms += ["", "## Insights"]
    llms += [f"- [{m['h1']}]({SITE}/insights/{m['slug']}/): {m['description']}" for m in posts]
    if cases:
        llms += ["", "## Case studies"]
        llms += [f"- [{m['h1']}]({SITE}/case-studies/{m['slug']}/): {m['description']}" for m in cases]
        llms += ["", "## Use cases"]
        llms += [f"- [{u['title']} ({u['sector']})]({SITE}/case-studies/#uc-{u['id']}): {u['problem']}" for u in use_cases()]
    llms += ["", "## Worldwide", f"- [Fractional CTO worldwide]({SITE}/regions/): regional pages and live working hours"]
    llms += [f"- [{label(m['slug'])}]({SITE}/{m['slug']}/): {m['description']}" for m in REGIONS]
    llms += ["", "## About and approach"] + [f"- [{v['name']}]({SITE}/{k}/): {v['description']}" for k, v in HUB_PAGES.items()]
    llms += ["", "## Play", f"- [Orbital Ops]({SITE}/play/): a free sci-fi browser arcade game about defending production from incidents", "", "## Profile", f"- [Home]({SITE}/): case studies, capabilities, playbook, FAQ",
             "- [GitHub](https://github.com/caeser1996)",
             "- [Publication, Science Immunology](https://doi.org/10.1126/sciimmunol.abl9165)", ""]
    (ROOT / "llms.txt").write_text("\n".join(llms))

    news = [m for m in posts if m.get("format") == "tech-news" or "news" in m.get("tags", [])]
    allitems = sorted([(m, "insights") for m in posts] + [(m, "case-studies") for m in cases], key=lambda x: sort_key(x[0]), reverse=True)
    write_feed("/feed.xml", "Insights and case studies", "Fractional CTO and AI architect: insights, case studies and daily tech news.", allitems)
    write_feed("/insights/feed.xml", "Insights", FEEDS[1][2], [(m, "insights") for m in posts])
    write_feed("/insights/news.xml", "Daily tech news", FEEDS[2][2], [(m, "insights") for m in news])
    write_feed("/case-studies/feed.xml", "Case studies", FEEDS[3][2], [(m, "case-studies") for m in cases])
    (ROOT / "subscribe").mkdir(exist_ok=True)
    (ROOT / "subscribe/index.html").write_text(subscribe_page(pages, posts))
    stamp_assets()

    for m in pages + regions + posts + cases:
        print(f"{m['slug']:45} {words(m['body']):5} words  title {len(m['title'])}c  desc {len(m['description'])}c")


if __name__ == "__main__":
    main()

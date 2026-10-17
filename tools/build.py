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
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://caeser1996.github.io"
EMAIL = "sumantamukhopadhyaywork@gmail.com"
CAL = "https://calendar.app.google/fpARv4QHsYCLMo3a8"
NAME = "Sumanta Mukhopadhyay"
TODAY = datetime.date.today().isoformat()

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
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400'
    '&family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />'
)

THEME_INIT = """<script>
  document.documentElement.classList.add('js');
  var t='dark';try{t=localStorage.getItem('theme')||'dark';}catch(e){}
  document.documentElement.setAttribute('data-theme',t);
</script>"""

MOON = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
        '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')


def nav():
    return f"""<div class="progress" id="progress"></div>
<nav>
  <div class="nav-in">
    <a href="/" class="brand">Sumanta<span>.</span></a>
    <div class="nav-links">
      <a href="/#practice">Services</a>
      <a href="/#work">Case studies</a>
      <a href="/insights/">Insights</a>
      <a href="/#assess">Analyse</a>
      <a href="/#connect">Connect</a>
    </div>
    <div class="nav-r">
      <button class="theme" id="themeBtn" aria-label="Toggle colour theme">{MOON}</button>
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
  <p class="cm-foot">I reply personally within two business days. US &amp; UAE time zones.</p>
</dialog>
<div class="toast" id="toast" role="status" aria-live="polite"></div>"""


def footer(pages, posts):
    svc = "".join(f'<li><a href="/{p["slug"]}/">{e(SERVICE_LABELS.get(p["slug"], p["h1"]))}</a></li>' for p in pages)
    ins = "".join(f'<li><a href="/insights/{p["slug"]}/">{e(p["h1"])}</a></li>' for p in posts)
    return f"""<footer class="site-foot">
  <div class="wrap">
    <div class="fcols">
      <div class="fc fbrand">
        <a href="/" class="brand">Sumanta<span>.</span></a>
        <p>Fractional CTO, principal engineer and AI architect. Ontology, AI, healthcare data and cloud infrastructure, from strategy to production.</p>
        <p class="floc">United States &amp; UAE · working globally</p>
      </div>
      <div class="fc"><h4>Services</h4><ul>{svc}</ul></div>
      <div class="fc"><h4>Insights</h4><ul>{ins}<li><a href="/insights/">All articles →</a></li></ul></div>
      <div class="fc"><h4>Connect</h4><ul>
        <li><a href="{CAL}" target="_blank" rel="noopener">Book a 30-min call</a></li>
        <li><a href="mailto:{EMAIL}?subject=Engagement%20enquiry" data-contact="Engagement enquiry">Send a message</a></li>
        <li><a href="/#assess">Analyse your challenge</a></li>
        <li><a href="https://github.com/caeser1996" target="_blank" rel="noopener">GitHub</a></li>
      </ul></div>
    </div>
    <div class="fbot"><span>© <span id="yr">{TODAY[:4]}</span> {NAME}</span><span class="sp"></span><a href="/sitemap.xml">Sitemap</a></div>
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
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}" />
<meta name="keywords" content="{e(', '.join(keywords))}" />
<meta name="author" content="{NAME}" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<link rel="canonical" href="{url}" />
<meta name="theme-color" content="#111214" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
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


def related_html(paths, pages_by_slug, posts):
    cards = []
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


def page(meta, kind, pages, posts, pages_by_slug):
    slug = meta["slug"]
    if kind == "service":
        url = f"{SITE}/{slug}/"
        crumb = [("Home", f"{SITE}/"), (SERVICE_LABELS.get(slug, meta["h1"]), url)]
        main_ld = {"@type": "Service", "name": SERVICE_LABELS.get(slug, meta["h1"]), "description": meta["description"],
                   "provider": person_ref(), "url": url,
                   "areaServed": ["United States", "United Arab Emirates", "Worldwide"]}
        og_type = "website"
        meta_line = ""
    else:
        url = f"{SITE}/insights/{slug}/"
        crumb = [("Home", f"{SITE}/"), ("Insights", f"{SITE}/insights/"), (meta["h1"], url)]
        main_ld = {"@type": "Article", "headline": meta["h1"], "description": meta["description"],
                   "datePublished": meta.get("date", TODAY), "dateModified": meta.get("date", TODAY),
                   "author": person_ref(), "publisher": person_ref(), "mainEntityOfPage": url,
                   "image": f"{SITE}/assets/og/{slug}.png", "keywords": ", ".join(meta["keywords"]),
                   "wordCount": words(meta["body"])}
        og_type = "article"
        d = datetime.date.fromisoformat(meta.get("date", TODAY)).strftime("%-d %B %Y")
        meta_line = f'<div class="ameta"><span>{NAME}</span><span>{d}</span><span>{e(meta.get("readtime", ""))}</span></div>'
    graph = [main_ld, crumbs(crumb)]
    if meta.get("faq"):
        graph.append(faq_ld(meta["faq"]))
    ld = {"@context": "https://schema.org", "@graph": graph}
    og = f"{SITE}/assets/og/{slug}.png"
    bc = " <span>/</span> ".join(
        (f'<a href="{u.replace(SITE, "") or "/"}">{e(n)}</a>' if i < len(crumb) - 1 else f"<em>{e(n)}</em>")
        for i, (n, u) in enumerate(crumb))
    subject = SERVICE_LABELS.get(slug, meta["h1"]) if kind == "service" else f"Re: {meta['h1']}"
    article_cls = "prose article" if kind == "post" else "prose"
    return f"""{head(meta['title'], meta['description'], meta['keywords'], url, og, og_type, ld)}
<body class="sub {'is-post' if kind == 'post' else 'is-service'}">
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

  <article class="{article_cls}">
    {meta['body']}
  </article>

  {faq_html(meta.get('faq'))}
  {related_html(meta.get('related', []), pages_by_slug, [p for p in posts if p['slug'] != slug])}
  {cta_html(subject)}
</main>

{modal()}
{footer(pages, posts)}
{SCRIPTS}
</body>
</html>
"""


def insights_index(pages, posts):
    url = f"{SITE}/insights/"
    title = "Insights on AI, ontology, healthcare data & CTO leadership"
    desc = ("Practical articles by Sumanta Mukhopadhyay on fractional CTO work, ontologies and knowledge graphs, "
            "production RAG and LLMs, FHIR and OMOP, and private AI.")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "name": "Insights", "url": url, "author": person_ref(),
         "blogPost": [{"@type": "BlogPosting", "headline": p["h1"], "url": f"{SITE}/insights/{p['slug']}/",
                       "datePublished": p.get("date", TODAY)} for p in posts]},
        crumbs([("Home", f"{SITE}/"), ("Insights", url)])]}
    cards = "".join(
        f'<a class="post rise" href="/insights/{p["slug"]}/"><small>{e(p["kicker"])} · {e(p.get("readtime", ""))}</small>'
        f'<h2>{e(p["h1"])}</h2><p>{e(p["lede"])}</p><i>Read article →</i></a>' for p in posts)
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
  </header>
  <div class="posts">{cards}</div>
  {cta_html('Re: Insights')}
</main>
{modal()}
{footer(pages, posts)}
{SCRIPTS}
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


def update_home(pages, posts):
    p = ROOT / "index.html"
    s = p.read_text()
    cards = "".join(
        f'<a class="post rise" href="/insights/{q["slug"]}/"><small>{e(q["kicker"])} · {e(q.get("readtime", ""))}</small>'
        f'<h3>{e(q["h1"])}</h3><p>{e(q["lede"])}</p><i>Read article →</i></a>' for q in posts)
    svc = "".join(
        f'<a class="svc rise" href="/{q["slug"]}/"><b>{e(SERVICE_LABELS.get(q["slug"], q["h1"]))}</b><i>→</i></a>'
        for q in pages)
    blocks = {"INSIGHTS": f'<div class="posts">{cards}</div>', "SERVICES": f'<div class="svcs">{svc}</div>',
              "FOOTER": footer(pages, posts)}
    for k, v in blocks.items():
        s, n = re.subn(rf"<!-- {k}:START -->.*?<!-- {k}:END -->", f"<!-- {k}:START -->\n{v}\n<!-- {k}:END -->", s,
                       flags=re.S)
        if n != 1:
            raise SystemExit(f"index.html: marker {k} not found")
    p.write_text(s)


def main():
    pages = [load(f) for f in sorted((ROOT / "src/pages").glob("*.part"))]
    order = list(SERVICE_LABELS)
    pages.sort(key=lambda m: order.index(m["slug"]) if m["slug"] in order else 99)
    posts = [load(f) for f in sorted((ROOT / "src/insights").glob("*.part"))]
    posts.sort(key=lambda m: (m.get("date", ""), m["h1"]), reverse=True)
    by_slug = {m["slug"]: m for m in pages}

    for m in pages:
        out = ROOT / m["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page(m, "service", pages, posts, by_slug))
    for m in posts:
        out = ROOT / "insights" / m["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(m, "post", pages, posts, by_slug))
    (ROOT / "insights").mkdir(exist_ok=True)
    (ROOT / "insights/index.html").write_text(insights_index(pages, posts))
    update_home(pages, posts)
    (ROOT / "404.html").write_text(not_found(pages, posts))

    urls = [("/", "1.0", "monthly"), ("/insights/", "0.8", "weekly")]
    urls += [(f"/{m['slug']}/", "0.9", "monthly") for m in pages]
    urls += [(f"/insights/{m['slug']}/", "0.7", "yearly") for m in posts]
    sm = "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{c}</changefreq>"
                 f"<priority>{pr}</priority></url>\n" for u, pr, c in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + sm + "</urlset>\n")

    llms = [f"# {NAME}", "",
            "> Fractional CTO, principal engineer and AI architect based in the United States and the UAE. "
            "Ontology and knowledge graphs, production RAG and agentic AI, private LLMs, healthcare data (FHIR, OMOP, "
            "HIPAA), scalable data platforms (1M+ transactions/day) and multi-cloud infrastructure.", "",
            f"Contact: {EMAIL} · Book a call: {CAL}", "", "## Services"]
    llms += [f"- [{SERVICE_LABELS.get(m['slug'], m['h1'])}]({SITE}/{m['slug']}/): {m['description']}" for m in pages]
    llms += ["", "## Insights"]
    llms += [f"- [{m['h1']}]({SITE}/insights/{m['slug']}/): {m['description']}" for m in posts]
    llms += ["", "## Profile", f"- [Home]({SITE}/): case studies, capabilities, playbook, FAQ",
             "- [GitHub](https://github.com/caeser1996)",
             "- [Publication, Science Immunology](https://doi.org/10.1126/sciimmunol.abl9165)", ""]
    (ROOT / "llms.txt").write_text("\n".join(llms))

    for m in pages + posts:
        print(f"{m['slug']:45} {words(m['body']):5} words  title {len(m['title'])}c  desc {len(m['description'])}c")


if __name__ == "__main__":
    main()

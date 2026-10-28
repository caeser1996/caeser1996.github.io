<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
<xsl:output method="html" encoding="UTF-8"/>
<xsl:template match="/">
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title><xsl:value-of select="rss/channel/title"/> (RSS feed)</title>
<style>
body{margin:0;background:#fafafa;color:#09090b;font:16px/1.6 -apple-system,"Segoe UI",sans-serif}
.w{max-width:760px;margin:0 auto;padding:40px 20px}
.note{background:#eef4ff;border:1px solid #c7dafc;border-radius:12px;padding:16px 18px;font-size:15px}
.note code{background:#fff;border:1px solid #c7dafc;border-radius:6px;padding:2px 6px;word-break:break-all}
h1{font-size:30px;line-height:1.2;margin:26px 0 6px}
p.d{color:#52525b;margin:0 0 26px}
a{color:#2563eb;text-decoration:none}
.i{padding:16px 0;border-top:1px solid #e4e4e7}
.i a{font-weight:600;font-size:17px;color:#09090b}.i a:hover{color:#2563eb}
.i small{display:block;color:#71717a;font-size:13px;margin:4px 0}
.i p{margin:4px 0 0;color:#52525b;font-size:15px}
@media(prefers-color-scheme:dark){body{background:#09090b;color:#fafafa}.note{background:#111a2e;border-color:#1e3a6e}.note code{background:#09090b;border-color:#1e3a6e}p.d,.i p{color:#a1a1aa}.i{border-color:#27272a}.i a{color:#fafafa}a{color:#4c8dff}}
</style></head><body><div class="w">
<div class="note"><b>This is an RSS feed.</b> Copy this page's address, <code><xsl:value-of select="rss/channel/atom:link/@href"/></code>, into a feed reader such as Feedly, Inoreader or NetNewsWire to get every new post. <a href="/subscribe/">How to subscribe →</a></div>
<h1><xsl:value-of select="rss/channel/title"/></h1>
<p class="d"><xsl:value-of select="rss/channel/description"/> · <a href="/">Visit the site</a></p>
<xsl:for-each select="rss/channel/item">
<div class="i"><a><xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute><xsl:value-of select="title"/></a>
<small><xsl:value-of select="substring(pubDate,6,11)"/></small><p><xsl:value-of select="description"/></p></div>
</xsl:for-each>
</div></body></html>
</xsl:template>
</xsl:stylesheet>

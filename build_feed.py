"""Builds feed.xml: Prestige long-form YouTube uploads (no Shorts) as RSS 2.0
with thumbnails Zoho Campaigns can read ($[RI:IMAGE]$)."""
import re, urllib.request, html
from email.utils import format_datetime
from datetime import datetime

SRC = "https://www.youtube.com/feeds/videos.xml?playlist_id=UULF5HfUyPEBtJX9jgYUlxtxlw"
CHANNEL = "https://www.youtube.com/channel/UC5HfUyPEBtJX9jgYUlxtxlw"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30)

def thumb(vid):
    for name in ("maxresdefault", "sddefault", "hqdefault"):
        u = f"https://i.ytimg.com/vi/{vid}/{name}.jpg"
        try:
            r = get(u)
            if r.status == 200 and int(r.headers.get("Content-Length", "2000")) > 1500:
                return u
        except Exception:
            pass
    return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

xml = get(SRC).read().decode("utf-8")
items = []
for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S)[:10]:
    vid = re.search(r"<yt:videoId>(.*?)</yt:videoId>", e).group(1)
    title = html.unescape(re.search(r"<title>(.*?)</title>", e, re.S).group(1))
    pub = datetime.fromisoformat(re.search(r"<published>(.*?)</published>", e).group(1))
    d = re.search(r"<media:description>(.*?)</media:description>", e, re.S)
    desc = html.unescape(d.group(1)).strip().split("\n")[0][:300] if d else ""
    link = f"https://www.youtube.com/watch?v={vid}"
    img = thumb(vid)
    esc = html.escape
    items.append(f"""  <item>
    <title>{esc(title)}</title>
    <link>{link}</link>
    <guid isPermaLink="false">yt:{vid}</guid>
    <pubDate>{format_datetime(pub)}</pubDate>
    <description><![CDATA[<img src="{img}" alt="{esc(title)}" />]]></description>
    <enclosure url="{img}" type="image/jpeg" length="0" />
    <media:content url="{img}" medium="image" type="image/jpeg" />
    <media:thumbnail url="{img}" />
  </item>""")

out = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
  <title>Prestige Veteran Medical Consulting - Medical Team Monday</title>
  <link>{CHANNEL}</link>
  <description>Weekly long-form videos from the Prestige medical team (Shorts excluded).</description>
  <language>en-us</language>
{chr(10).join(items)}
</channel>
</rss>
"""
open("feed.xml", "w", encoding="utf-8").write(out)
print(f"wrote {len(items)} items")

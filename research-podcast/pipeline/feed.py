"""⑥ 配信物の生成：episodes.json から podcast.xml（RSS2.0+iTunes）と index.html を作る。"""
import os
import html
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from . import config


def _fmt_duration(sec):
    sec = int(sec)
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"


def write_feed(episodes):
    """episodes: 新しい順のリスト。各要素 dict(title, desc, date(ISO), file, bytes, duration, guid)"""
    base = config.PAGES_BASE_URL
    items = []
    for ep in episodes:
        pub = format_datetime(datetime.fromisoformat(ep["date"]).replace(tzinfo=timezone.utc))
        url = f"{base}/audio/{ep['file']}"
        items.append(f"""    <item>
      <title>{escape(ep['title'])}</title>
      <description>{escape(ep['desc'])}</description>
      <pubDate>{pub}</pubDate>
      <enclosure url="{escape(url)}" length="{ep['bytes']}" type="audio/mpeg"/>
      <guid isPermaLink="false">{escape(ep['guid'])}</guid>
      <itunes:duration>{_fmt_duration(ep['duration'])}</itunes:duration>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(config.PODCAST_TITLE)}</title>
    <link>{escape(base)}</link>
    <language>{config.PODCAST_LANG}</language>
    <description>{escape(config.PODCAST_DESC)}</description>
    <itunes:author>{escape(config.PODCAST_AUTHOR)}</itunes:author>
    <itunes:explicit>false</itunes:explicit>
    <itunes:category text="Science"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    with open(os.path.join(config.DOCS_DIR, "podcast.xml"), "w", encoding="utf-8") as f:
        f.write(rss)


def write_index(episodes):
    base = config.PAGES_BASE_URL
    rows = "\n".join(
        f'<li><strong>{html.escape(ep["title"])}</strong><br>'
        f'<small>{ep["date"][:10]} · {_fmt_duration(ep["duration"])}</small><br>'
        f'<audio controls preload="none" src="audio/{ep["file"]}"></audio></li>'
        for ep in episodes
    )
    page = f"""<!doctype html><meta charset="utf-8">
<title>{html.escape(config.PODCAST_TITLE)}</title>
<style>body{{font-family:-apple-system,system-ui,sans-serif;max-width:680px;margin:40px auto;
padding:0 16px;background:#0b0b0c;color:#e8e8ea}}a{{color:#6aa3ff}}li{{margin:24px 0;list-style:none}}
audio{{width:100%;margin-top:6px}}code{{background:#1c1c1f;padding:2px 6px;border-radius:4px}}</style>
<h1>{html.escape(config.PODCAST_TITLE)}</h1>
<p>{html.escape(config.PODCAST_DESC)}</p>
<p>購読用RSS: <code>{base}/podcast.xml</code></p>
<ul>{rows}</ul>
"""
    with open(os.path.join(config.DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)

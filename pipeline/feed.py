"""⑥ 単一フィード：共有 episodes.json から podcast.xml（両シリーズ混在）と index.html を生成。"""
import os
import html
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from . import config


def _fmt_duration(sec):
    sec = int(sec)
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"


def _audio_rel(ep):
    # 新形式は audio_rel を持つ。旧エピソードは audio/<file> にフォールバック。
    return ep.get("audio_rel") or f"audio/{ep.get('file', '')}"


def write_feed(episodes):
    base = config.PAGES_BASE_URL
    items = []
    for ep in episodes:
        try:
            pub = format_datetime(datetime.fromisoformat(ep["date"]).replace(tzinfo=timezone.utc))
        except Exception:
            pub = format_datetime(datetime.now(timezone.utc))
        url = f"{base}/{_audio_rel(ep)}"
        season = ep.get("season")
        season_tag = f"\n      <itunes:season>{season}</itunes:season>" if season else ""
        items.append(f"""    <item>
      <title>{escape(ep['title'])}</title>
      <description>{escape(ep['desc'])}</description>
      <pubDate>{pub}</pubDate>
      <enclosure url="{escape(url)}" length="{ep.get('bytes', 0)}" type="audio/mpeg"/>
      <guid isPermaLink="false">{escape(ep.get('guid', ep.get('file','')))}</guid>
      <itunes:duration>{_fmt_duration(ep.get('duration', 0))}</itunes:duration>{season_tag}
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
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    with open(os.path.join(config.DOCS_DIR, "podcast.xml"), "w", encoding="utf-8") as f:
        f.write(rss)


def write_index(episodes):
    rows = "\n".join(
        f'<li><span class="s">{html.escape(str(ep.get("series","")))}</span>'
        f'<strong>{html.escape(ep["title"])}</strong><br>'
        f'<small>{ep.get("date","")[:10]} · {_fmt_duration(ep.get("duration",0))}</small><br>'
        f'<audio controls preload="none" src="{html.escape(_audio_rel(ep))}"></audio></li>'
        for ep in episodes
    )
    page = f"""<!doctype html><meta charset="utf-8">
<title>{html.escape(config.PODCAST_TITLE)}</title>
<style>body{{font-family:-apple-system,system-ui,sans-serif;max-width:680px;margin:40px auto;
padding:0 16px;background:#0b0b0c;color:#e8e8ea}}a{{color:#6aa3ff}}li{{margin:24px 0;list-style:none}}
audio{{width:100%;margin-top:6px}}code{{background:#1c1c1f;padding:2px 6px;border-radius:4px}}
.s{{display:inline-block;font-size:12px;color:#9aa;margin-right:8px}}</style>
<h1>{html.escape(config.PODCAST_TITLE)}</h1>
<p>{html.escape(config.PODCAST_DESC)}</p>
<p>購読用RSS: <code>{config.PAGES_BASE_URL}/podcast.xml</code></p>
<ul>{rows}</ul>
"""
    with open(os.path.join(config.DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)

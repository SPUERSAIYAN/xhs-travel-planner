#!/usr/bin/env python3
"""Create a deployable single-file travel-plan.html from itinerary JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from generate_map_links import ensure_place_links
from validate_itinerary import validate


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def build_html(data: dict[str, Any]) -> str:
    payload = (
        json.dumps(data, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace("</script", "<\\/script")
    )
    title = f"{data.get('trip', {}).get('destination', '旅行')}计划"

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{ color:#18211f; background:#f6f2e8; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; min-width:320px; background:#f6f2e8; }}
    button,a {{ font:inherit; }}
    .app {{ width:min(100%,780px); margin:0 auto; padding:0 14px 38px; }}
    .hero {{ position:sticky; top:0; z-index:5; margin:0 -14px; padding:20px 14px 16px; color:#fffdf7; background:#245b52; box-shadow:0 12px 28px rgba(24,33,31,.18); }}
    .kicker {{ display:flex; gap:8px; align-items:center; color:#d8efe7; font-size:.86rem; }}
    h1 {{ margin:8px 0 10px; font-size:clamp(2rem,11vw,4rem); line-height:.98; letter-spacing:0; }}
    h2 {{ margin:0; font-size:1.18rem; line-height:1.25; }}
    p {{ line-height:1.55; }}
    .meta {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .meta span {{ padding:7px 10px; border:1px solid rgba(255,255,255,.25); border-radius:999px; background:rgba(255,255,255,.12); font-size:.86rem; }}
    .tabs {{ position:sticky; top:142px; z-index:4; display:grid; grid-auto-flow:column; grid-auto-columns:minmax(58px,1fr); gap:8px; margin:0 -14px 12px; padding:10px 14px; overflow-x:auto; background:rgba(246,242,232,.95); backdrop-filter:blur(12px); }}
    .tab {{ min-height:42px; border:1px solid #ccd7cf; border-radius:8px; background:#fffaf0; color:#29413c; font-weight:800; }}
    .tab.active {{ border-color:#245b52; background:#f0b84c; color:#18211f; }}
    .panel {{ margin-top:14px; padding:16px; border:1px solid #d7dccf; border-radius:8px; background:rgba(255,250,240,.88); }}
    .heading {{ display:flex; gap:10px; align-items:center; margin-bottom:10px; }}
    .heading .icon {{ display:grid; width:30px; height:30px; place-items:center; border-radius:50%; background:#e6f0eb; color:#245b52; }}
    .heading p,.muted,.sub {{ margin:0; color:#66706b; font-size:.84rem; }}
    .timeline {{ display:grid; gap:10px; margin-top:14px; }}
    .card {{ border:1px solid #dfe3dc; border-radius:8px; overflow:hidden; background:#fff; }}
    .card-main {{ display:grid; width:100%; grid-template-columns:34px minmax(0,1fr) 24px; gap:10px; padding:14px; border:0; background:transparent; color:inherit; text-align:left; }}
    .dot {{ display:grid; width:30px; height:30px; place-items:center; border-radius:50%; background:#245b52; color:white; font-weight:900; }}
    .card-title {{ display:grid; gap:4px; min-width:0; }}
    .card-title strong {{ overflow-wrap:anywhere; }}
    .detail {{ display:none; padding:0 14px 14px 58px; }}
    .card.open .detail {{ display:grid; gap:10px; }}
    .chev {{ transition:transform .18s ease; align-self:center; }}
    .card.open .chev {{ transform:rotate(180deg); }}
    .tags,.buttons {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .tags span {{ padding:4px 8px; border-radius:999px; background:#e8f1ed; color:#245b52; font-size:.8rem; }}
    .map {{ display:inline-flex; min-height:38px; align-items:center; justify-content:center; gap:6px; padding:8px 12px; border-radius:8px; text-decoration:none; font-weight:900; border:1px solid #bdc8bf; color:#245b52; background:#fffaf0; }}
    .map.primary {{ border-color:#245b52; background:#245b52; color:#fff; }}
    .warning {{ margin-top:10px; padding:12px; border-left:4px solid #d06f3c; border-radius:8px; background:#fff4ea; }}
    .warning.high {{ border-left-color:#c43d32; }}
    .warning.low {{ border-left-color:#f0b84c; }}
    .warning p {{ margin:6px 0 0; color:#5d4034; }}
    .sources {{ display:grid; gap:8px; }}
    .source {{ border:1px solid #e1e4dd; border-radius:8px; background:#fbfcf7; padding:10px; }}
    .source a {{ color:#245b52; font-weight:800; overflow-wrap:anywhere; }}
    .source p {{ margin:4px 0; color:#59645f; font-size:.9rem; }}
    .assumption {{ margin-top:8px; color:#3e4b47; }}
    @media (min-width:700px) {{ .hero {{ border-radius:0 0 18px 18px; }} .tabs {{ top:158px; }} }}
  </style>
</head>
<body>
  <main class="app">
    <header class="hero">
      <div class="kicker">小红书来源 · 手机旅行计划</div>
      <h1 id="trip-title"></h1>
      <div class="meta" id="trip-meta"></div>
    </header>
    <nav class="tabs" id="tabs" aria-label="每日路线"></nav>
    <section class="panel" id="day-panel"></section>
    <section class="panel" id="warnings-panel"></section>
    <section class="panel" id="assumptions-panel"></section>
    <section class="panel" id="sources-panel"></section>
  </main>
  <script id="itinerary-data" type="application/json">{payload}</script>
  <script>
    const itinerary = JSON.parse(document.getElementById('itinerary-data').textContent);
    const places = new Map(itinerary.places.map(place => [place.id, place]));
    const sources = new Map(itinerary.sources.map(source => [source.id, source]));
    const warnings = new Map(itinerary.warnings.map(warning => [warning.id, warning]));
    let activeDayId = itinerary.days[0]?.id;
    const $ = id => document.getElementById(id);
    const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
    const unique = items => [...new Set(items.filter(Boolean))];
    const confidence = value => ({{confirmed:'已确认',candidate:'候选',avoid:'避坑',assumption:'推断'}}[value] || '未标注');
    function renderMeta() {{
      $('trip-title').textContent = itinerary.trip.destination + '旅行计划';
      const range = typeof itinerary.trip.dateRange === 'string' ? itinerary.trip.dateRange : itinerary.trip.dayCount + '天';
      $('trip-meta').innerHTML = [range, itinerary.trip.travelers, itinerary.trip.style, itinerary.trip.baseArea && '住 ' + itinerary.trip.baseArea].filter(Boolean).map(item => `<span>${{escapeHtml(item)}}</span>`).join('');
    }}
    function renderTabs() {{
      $('tabs').innerHTML = itinerary.days.map(day => `<button class="tab ${{day.id === activeDayId ? 'active' : ''}}" data-day="${{day.id}}">D${{day.dayNumber}}</button>`).join('');
      $('tabs').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {{ activeDayId = button.dataset.day; render(); }}));
    }}
    function mapButtons(links) {{
      if (!links) return '<p class="muted">暂无地图链接</p>';
      return `<div class="buttons">${{links.amap ? `<a class="map primary" target="_blank" rel="noreferrer" href="${{escapeHtml(links.amap)}}">高德地图</a>` : ''}}${{links.baidu ? `<a class="map" target="_blank" rel="noreferrer" href="${{escapeHtml(links.baidu)}}">百度地图</a>` : ''}}</div>`;
    }}
    function sourceList(ids) {{
      const list = unique(ids).map(id => sources.get(id)).filter(Boolean);
      if (!list.length) return '<p class="muted">此项暂无可读来源，按候选/推断处理。</p>';
      return `<div class="sources">${{list.map(source => `<article class="source"><strong>${{escapeHtml(source.title || source.id)}}</strong><p>${{escapeHtml(source.author || '未知作者')}} · ${{escapeHtml(source.publishedDate || '日期未知')}}</p><p>${{escapeHtml(source.excerpt || '')}}</p>${{source.url ? `<a target="_blank" rel="noreferrer" href="${{escapeHtml(source.url)}}">打开小红书来源</a>` : '<span class="muted">无链接</span>'}}</article>`).join('')}}</div>`;
    }}
    function warningBlocks(ids) {{
      return unique(ids).map(id => warnings.get(id)).filter(Boolean).map(warning => `<article class="warning ${{escapeHtml(warning.severity)}}"><strong>${{escapeHtml(warning.title)}}</strong><p>${{escapeHtml(warning.detail || '')}}</p>${{warning.mitigation ? `<p>建议：${{escapeHtml(warning.mitigation)}}</p>` : ''}}</article>`).join('');
    }}
    function renderDay() {{
      const day = itinerary.days.find(item => item.id === activeDayId) || itinerary.days[0];
      $('day-panel').innerHTML = `<div class="heading"><span class="icon">路线</span><div><p>Day ${{day.dayNumber}}</p><h2>${{escapeHtml(day.title)}}</h2></div></div>${{day.summary ? `<p>${{escapeHtml(day.summary)}}</p>` : ''}}<div class="timeline">${{day.items.map((item, index) => {{
        const place = item.placeId ? places.get(item.placeId) : null;
        const ids = unique([...(item.sourceIds || []), ...((place && place.sourceIds) || [])]);
        const links = (place && place.mapLinks) || item.mapLinks;
        return `<article class="card"><button class="card-main" type="button"><span class="dot">${{index + 1}}</span><span class="card-title"><span class="sub">${{escapeHtml(item.timeBlock)}}${{item.duration ? ' · ' + escapeHtml(item.duration) : ''}}</span><strong>${{escapeHtml(item.title)}}</strong>${{place ? `<span class="sub">${{escapeHtml(place.area || place.city)}} · ${{confidence(place.confidence)}}</span>` : ''}}</span><span class="chev">⌄</span></button><div class="detail">${{place?.tags?.length ? `<div class="tags">${{place.tags.map(tag => `<span>${{escapeHtml(tag)}}</span>`).join('')}}</div>` : ''}}${{place?.reason ? `<p>${{escapeHtml(place.reason)}}</p>` : ''}}${{(item.notes || []).map(note => `<p>${{escapeHtml(note)}}</p>`).join('')}}${{item.transportToNext ? `<p>下一程：${{escapeHtml(item.transportToNext)}}</p>` : ''}}${{mapButtons(links)}}${{warningBlocks(item.warningIds || [])}}${{sourceList(ids)}}</div></article>`;
      }}).join('')}}</div>`;
      document.querySelectorAll('.card-main').forEach(button => button.addEventListener('click', () => button.closest('.card').classList.toggle('open')));
    }}
    function renderWarnings() {{
      $('warnings-panel').innerHTML = `<div class="heading"><span class="icon">避坑</span><div><p>Warnings</p><h2>路线前先看</h2></div></div>${{itinerary.warnings.map(warning => `<article class="warning ${{escapeHtml(warning.severity)}}"><strong>${{escapeHtml(warning.title)}}</strong><p>${{escapeHtml(warning.detail || '')}}</p>${{warning.mitigation ? `<p>建议：${{escapeHtml(warning.mitigation)}}</p>` : ''}}</article>`).join('')}}`;
    }}
    function renderAssumptions() {{
      $('assumptions-panel').innerHTML = `<div class="heading"><span class="icon">说明</span><div><p>Scope</p><h2>数据边界</h2></div></div>${{(itinerary.trip.assumptions || []).map(item => `<p class="assumption">${{escapeHtml(item)}}</p>`).join('')}}`;
    }}
    function renderSources() {{
      $('sources-panel').innerHTML = `<div class="heading"><span class="icon">来源</span><div><p>Sources</p><h2>${{itinerary.sources.length}} 条小红书笔记/评论</h2></div></div>${{sourceList(itinerary.sources.map(source => source.id))}}`;
    }}
    function render() {{ renderMeta(); renderTabs(); renderDay(); renderWarnings(); renderAssumptions(); renderSources(); }}
    render();
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a deployable single-file travel-plan.html.")
    parser.add_argument("itinerary", type=Path)
    parser.add_argument("output", type=Path, nargs="?", default=Path("travel-plan.html"))
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.itinerary.read_text(encoding="utf-8"))
    data = ensure_place_links(data)
    errors, warnings = validate(data)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors and not args.skip_validation:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    args.output.write_text(build_html(data), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
    :root {{
      color: #111827;
      background: #eceef2;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      font-synthesis: none;
      text-rendering: optimizeLegibility;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-width: 320px; background: #eceef2; }}
    button, a {{ font: inherit; }}
    button {{ cursor: pointer; }}
    .phone {{
      width: min(100%, 430px);
      min-height: 100vh;
      margin: 0 auto;
      background: #fff;
      overflow: hidden;
      box-shadow: 0 18px 60px rgba(17,24,39,.12);
    }}
    .hero {{
      position: relative;
      min-height: 224px;
      padding: 36px 28px 34px;
      color: #fff;
      background:
        linear-gradient(90deg, rgba(12,22,34,.76), rgba(12,22,34,.38) 56%, rgba(12,22,34,.22)),
        linear-gradient(180deg, rgba(12,22,34,.12), rgba(12,22,34,.74)),
        var(--hero-image),
        linear-gradient(135deg, #25364b, #65717e);
      background-size: cover;
      background-position: center;
      border-bottom-left-radius: 8px;
      border-bottom-right-radius: 8px;
    }}
    .hero-fallback {{
      --hero-image: radial-gradient(circle at 70% 30%, rgba(255,194,48,.34), transparent 28%),
        linear-gradient(135deg, #1f3348, #76808c);
    }}
    .chips, .meta, .bottom-actions, .card-actions, .route-strip, .save-page {{
      display: flex;
      align-items: center;
    }}
    .hero-copy {{ position: relative; z-index: 1; }}
    .city-line {{ display: flex; align-items: baseline; gap: 12px; }}
    .city-line h1 {{
      margin: 0;
      max-width: 13em;
      font-size: clamp(1.72rem, 8vw, 2.18rem);
      line-height: 1.08;
      letter-spacing: 0;
      font-weight: 900;
      text-shadow: 0 6px 24px rgba(0,0,0,.28);
    }}
    .script-name {{
      display: none;
    }}
    .hero-subtitle {{ display: none; }}
    .meta {{ gap: 8px; color: rgba(255,255,255,.9); font-size: .94rem; margin-top: 12px; }}
    .chips {{ flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
    .chip {{
      display: inline-flex;
      min-height: 30px;
      align-items: center;
      gap: 6px;
      padding: 6px 11px;
      border-radius: 10px;
      color: #fff;
      background: rgba(37,99,235,.86);
      font-weight: 800;
      font-size: .84rem;
    }}
    .chip:nth-child(1) {{ background: rgba(249,115,22,.9); }}
    .chip:nth-child(2) {{ background: rgba(124,58,237,.9); }}
    .chip:nth-child(3) {{ background: rgba(22,163,74,.9); }}
    .save-page {{
      margin-top: 14px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 34px;
      padding: 6px 14px;
      border: 1px solid rgba(255,255,255,.78);
      border-radius: 999px;
      color: #fff;
      background: rgba(0,0,0,.18);
      backdrop-filter: blur(8px);
      font-weight: 800;
      font-size: .84rem;
    }}
    .weather {{
      display: none;
    }}
    .sheet {{
      position: relative;
      z-index: 2;
      margin-top: -8px;
      padding: 0 20px 24px;
      border-top-left-radius: 8px;
      border-top-right-radius: 8px;
      background: #fff;
    }}
    .tabs {{
      position: sticky;
      top: 0;
      z-index: 4;
      display: grid;
      grid-auto-flow: column;
      grid-auto-columns: minmax(82px, 1fr);
      gap: 8px;
      margin: 0 -20px;
      padding: 12px 20px 8px;
      overflow-x: auto;
      background: rgba(255,255,255,.96);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid #eef2f7;
    }}
    .tab {{
      position: relative;
      min-height: 42px;
      border: 0;
      background: transparent;
      color: #7c818c;
      font-size: .96rem;
      font-weight: 800;
    }}
    .tab.active {{ color: #216bff; }}
    .tab.active::after {{
      content: "";
      position: absolute;
      left: 50%;
      bottom: 0;
      width: 78%;
      height: 2px;
      border-radius: 999px;
      background: #216bff;
      transform: translateX(-50%);
    }}
    .day-panel {{
      margin-top: 12px;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
    }}
    .day-heading {{ display: none; }}
    .day-title {{ min-width: 0; }}
    .day-title h2 {{ margin: 0; font-size: 1.2rem; line-height: 1.25; letter-spacing: 0; }}
    .day-title p {{ margin: 5px 0 0; color: #7c818c; font-size: .86rem; }}
    .budget {{
      flex: 0 0 auto;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 8px 10px;
      border-radius: 999px;
      background: #fff;
      color: #6b7280;
      font-size: .82rem;
      box-shadow: inset 0 0 0 1px #f0ece5;
    }}
    .budget strong {{ color: #f59e0b; font-size: 1rem; }}
    .route-strip {{
      justify-content: center;
      gap: 8px;
      min-height: 38px;
      margin-bottom: 14px;
      padding: 8px 12px;
      border: 1px solid #dce6f7;
      border-radius: 8px;
      color: #1f2937;
      background: linear-gradient(180deg, #fff, #f8fbff);
      font-weight: 800;
      font-size: .88rem;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .route-strip .pin {{ color: #216bff; font-size: 1.05rem; }}
    .timeline {{ position: relative; display: grid; gap: 14px; }}
    .timeline::before {{
      content: "";
      position: absolute;
      left: 58px;
      top: 20px;
      bottom: 24px;
      width: 2px;
      background: #dbeafe;
    }}
    .item-row {{ position: relative; display: grid; grid-template-columns: 70px minmax(0,1fr); gap: 12px; align-items: start; }}
    .time {{
      position: relative;
      padding-top: 12px;
      font-size: 1rem;
      font-weight: 800;
      color: #216bff;
    }}
    .time::after {{
      content: "";
      position: absolute;
      right: 4px;
      top: 18px;
      width: 9px;
      height: 9px;
      border: 2px solid #216bff;
      border-radius: 50%;
      background: #fff;
      z-index: 1;
    }}
    .plan-card {{
      position: relative;
      display: grid;
      grid-template-columns: 88px minmax(0,1fr) 24px;
      gap: 12px;
      min-height: 98px;
      padding: 0 0 0 0;
      border: 0;
      border-radius: 8px;
      background: #fff;
      color: inherit;
      text-align: left;
      box-shadow: none;
    }}
    .thumb {{
      width: 88px;
      height: 88px;
      border-radius: 8px;
      object-fit: cover;
      background:
        linear-gradient(135deg, rgba(255,194,51,.8), rgba(57,84,112,.78)),
        #dfe5ee;
    }}
    .card-copy {{ min-width: 0; }}
    .card-title-line {{ display: flex; flex-wrap: wrap; gap: 7px; align-items: center; margin-bottom: 6px; }}
    .card-title-line strong {{ font-size: 1.12rem; line-height: 1.2; overflow-wrap: anywhere; }}
    .tag {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 7px;
      font-size: .78rem;
      font-weight: 900;
      color: #047857;
      background: #daf8e8;
    }}
    .tag.food {{ color: #ea580c; background: #ffedd5; }}
    .tag.photo {{ color: #9333ea; background: #f3e8ff; }}
    .tag.warn {{ color: #f97316; background: #fff7ed; }}
    .card-meta {{ display: flex; flex-wrap: wrap; gap: 8px; color: #8a909b; font-size: .86rem; }}
    .card-note {{ margin: 8px 0 0; color: #6b7280; line-height: 1.45; font-size: .92rem; }}
    .check-circle {{
      align-self: start;
      width: 18px;
      height: 18px;
      border: 2px solid #d1d5db;
      border-radius: 4px;
      margin-top: 4px;
    }}
    .detail {{
      display: none;
      grid-column: 1 / -1;
      margin-top: 4px;
      padding-top: 10px;
      border-top: 1px solid #f0f1f4;
      color: #4b5563;
      line-height: 1.55;
    }}
    .plan-card.open .detail {{ display: grid; gap: 10px; }}
    .card-actions {{ flex-wrap: wrap; gap: 8px; }}
    .pill-button {{
      display: inline-flex;
      min-height: 36px;
      align-items: center;
      gap: 7px;
      padding: 7px 13px;
      border-radius: 999px;
      border: 1px solid #e5e7eb;
      color: #374151;
      background: #fff;
      font-weight: 800;
      text-decoration: none;
    }}
    .warning-box, .rainy-box {{
      padding: 12px;
      border-radius: 14px;
      background: #fff7ed;
      color: #9a3412;
      font-size: .9rem;
    }}
    .rainy-box {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 16px 0;
      border: 1px solid #dbeafe;
      background: #eff6ff;
      color: #243b68;
    }}
    .rainy-box strong {{ display: block; color: #1e3a8a; }}
    .source-list {{ display: grid; gap: 8px; }}
    .source {{
      padding: 10px;
      border-radius: 12px;
      background: #f9fafb;
      color: #4b5563;
      font-size: .86rem;
    }}
    .source a {{ color: #1d4ed8; font-weight: 800; overflow-wrap: anywhere; }}
    .section-panel {{
      margin-top: 14px;
      padding: 16px 14px;
      border-radius: 18px;
      background: #fff;
      box-shadow: 0 10px 28px rgba(17,24,39,.06);
    }}
    .section-panel h2 {{ margin: 0 0 10px; font-size: 1.08rem; }}
    .bottom-bar {{
      position: sticky;
      bottom: 0;
      z-index: 6;
      display: grid;
      grid-template-columns: 1.35fr 1fr 1fr 1fr;
      gap: 8px;
      margin: 18px -20px 0;
      padding: 12px 12px 14px;
      background: rgba(255,255,255,.94);
      backdrop-filter: blur(14px);
      border-top: 1px solid #eef0f4;
    }}
    .budget-summary {{
      display: grid;
      grid-template-columns: 38px minmax(0,1fr);
      gap: 8px;
      align-items: center;
      min-height: 56px;
      padding: 7px 6px;
      border: 1px solid #eef0f4;
      border-radius: 12px;
      color: #64748b;
      background: #fff;
      font-size: .7rem;
    }}
    .budget-summary .coin {{
      display: grid;
      width: 34px;
      height: 34px;
      place-items: center;
      border-radius: 50%;
      color: #15803d;
      background: #dcfce7;
      font-weight: 900;
    }}
    .budget-summary strong {{ display: block; color: #15803d; font-size: 1.05rem; line-height: 1.1; }}
    .bottom-button {{
      display: inline-flex;
      min-height: 56px;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 4px;
      border-radius: 12px;
      border: 1px solid #e5e7eb;
      color: #334155;
      background: #fff;
      font-weight: 900;
      font-size: .72rem;
      text-decoration: none;
    }}
    .bottom-button .icon {{ color: #216bff; font-size: 1.1rem; line-height: 1; }}
    .bottom-button.primary {{ border-color: #e5e7eb; background: #fff; color: #334155; }}
    @media (max-width: 390px) {{
      .hero {{ padding-left: 24px; padding-right: 24px; }}
      .city-line h1 {{ font-size: 1.68rem; }}
      .plan-card {{ grid-template-columns: 74px minmax(0,1fr) 22px; }}
      .thumb {{ width: 74px; height: 74px; }}
      .bottom-bar {{ gap: 6px; }}
      .budget-summary {{ font-size: .64rem; }}
      .bottom-button {{ font-size: .66rem; }}
    }}
  </style>
</head>
<body>
  <main class="phone">
    <header class="hero hero-fallback" id="hero">
      <div class="hero-copy">
        <div class="city-line"><h1 id="city-title"></h1><span class="script-name" id="city-script"></span></div>
        <div class="hero-subtitle" id="hero-subtitle"></div>
        <div class="meta" id="hero-meta"></div>
        <div class="chips" id="hero-chips"></div>
        <button class="save-page" type="button" id="save-page-top">▱ 保存页面</button>
      </div>
      <div class="weather" id="weather-pill"></div>
    </header>
    <section class="sheet">
      <nav class="tabs" id="tabs" aria-label="每日路线"></nav>
      <section class="day-panel" id="day-panel"></section>
      <section class="rainy-box" id="backup-panel"></section>
      <section class="section-panel" id="budget-panel"></section>
      <section class="section-panel" id="warnings-panel"></section>
      <section class="section-panel" id="assumptions-panel"></section>
      <section class="section-panel" id="sources-panel"></section>
      <nav class="bottom-bar">
        <div class="budget-summary" id="budget-summary"><span class="coin">￥</span><span><small>预算总计</small><strong>待估算</strong><small>不含往返交通</small></span></div>
        <button class="bottom-button" type="button" data-scroll="budget-panel"><span class="icon">▥</span>查看预算</button>
        <button class="bottom-button" type="button" id="today-map"><span class="icon">▮</span>今日地图</button>
        <button class="bottom-button primary" type="button" id="save-plan-bottom"><span class="icon">▱</span>保存行程</button>
      </nav>
    </section>
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
    const first = (...values) => values.find(value => value !== undefined && value !== null && value !== '');
    const categoryLabel = value => {{
      const labels = {{restaurant:'美食',cafe:'美食',attraction:'景点',neighborhood:'路线',hotel:'住宿',shop:'购物',transport:'交通',avoid:'避坑',other:'打卡'}};
      return labels[value] || '打卡';
    }};
    const tagClass = value => {{
      if (['restaurant','cafe'].includes(value)) return 'food';
      if (value === 'attraction') return 'photo';
      if (value === 'avoid') return 'warn';
      return '';
    }};
    function displayRange() {{
      const range = itinerary.trip.dateRange;
      if (!range) return itinerary.trip.dayCount + '天';
      if (typeof range === 'string') return range;
      return [range.start, range.end].filter(Boolean).join(' - ');
    }}
    function renderHero() {{
      const trip = itinerary.trip;
      const days = trip.dayCount || itinerary.days.length || 1;
      const nights = first(trip.nightCount, trip.nights, Math.max(days - 1, 0));
      $('city-title').textContent = trip.title || `${{trip.destination || '旅行'}} ${{days}}天${{nights}}晚旅行计划`;
      $('city-script').textContent = trip.destinationEn || trip.englishName || 'Travel';
      $('hero-meta').innerHTML = [displayRange(), trip.travelers, trip.baseArea && '住 ' + trip.baseArea].filter(Boolean).map(item => `<span>${{escapeHtml(item)}}</span>`).join('<span>·</span>');
      const styleText = String(trip.style || '轻松路线');
      const chips = unique(['美食', styleText.includes('拍') ? '拍照' : '打卡', styleText.includes('轻松') ? '轻松路线' : '顺路路线']);
      $('hero-chips').innerHTML = chips.map(chip => `<span class="chip">${{escapeHtml(chip)}}</span>`).join('');
      const weather = trip.weather || trip.weatherText || '26°C';
      $('weather-pill').innerHTML = `⛅ <span>${{escapeHtml(weather)}}</span>`;
      if (trip.heroImage || trip.coverImage) {{
        $('hero').style.setProperty('--hero-image', `url("${{String(trip.heroImage || trip.coverImage).replace(/"/g, '%22')}}")`);
        $('hero').classList.remove('hero-fallback');
      }}
    }}
    function renderTabs() {{
      $('tabs').innerHTML = itinerary.days.map(day => `<button class="tab ${{day.id === activeDayId ? 'active' : ''}}" data-day="${{day.id}}">Day ${{day.dayNumber}}</button>`).join('');
      $('tabs').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {{ activeDayId = button.dataset.day; render(); }}));
    }}
    function sourceList(ids) {{
      const list = unique(ids).map(id => sources.get(id)).filter(Boolean);
      if (!list.length) return '<p class="muted">此项暂无可读来源，按候选/推断处理。</p>';
      return `<div class="source-list">${{list.map(source => `<article class="source"><strong>${{escapeHtml(source.title || source.id)}}</strong><p>${{escapeHtml(source.author || '未知作者')}} · ${{escapeHtml(source.publishedDate || '日期未知')}}</p><p>${{escapeHtml(source.excerpt || '')}}</p>${{source.url ? `<a target="_blank" rel="noreferrer" href="${{escapeHtml(source.url)}}">打开小红书来源</a>` : ''}}</article>`).join('')}}</div>`;
    }}
    function mapButtons(links) {{
      if (!links) return '<p class="muted">暂无地图链接</p>';
      return `<div class="card-actions">${{links.amap ? `<a class="pill-button" target="_blank" rel="noreferrer" href="${{escapeHtml(links.amap)}}">📍 打开地图</a>` : ''}}${{links.baidu ? `<a class="pill-button" target="_blank" rel="noreferrer" href="${{escapeHtml(links.baidu)}}">备用地图</a>` : ''}}</div>`;
    }}
    function warningBlocks(ids) {{
      return unique(ids).map(id => warnings.get(id)).filter(Boolean).map(warning => `<div class="warning-box">⚠️ <strong>${{escapeHtml(warning.title)}}</strong><br>${{escapeHtml(warning.detail || '')}}${{warning.mitigation ? `<br>建议：${{escapeHtml(warning.mitigation)}}` : ''}}</div>`).join('');
    }}
    function renderDay() {{
      const day = itinerary.days.find(item => item.id === activeDayId) || itinerary.days[0];
      const budget = first(day.budgetEstimate, day.budget, itinerary.trip.budgetEstimate, itinerary.trip.budget);
      const routeNames = day.items.map(item => item.title).filter(Boolean).slice(0, 4).join(' → ');
      $('day-panel').innerHTML = `<div class="day-heading"><div class="day-title"><h2>Day ${{day.dayNumber}} · ${{escapeHtml(day.title)}}</h2><p>${{escapeHtml(day.summary || '按顺路性安排今日路线')}}</p></div>${{budget ? `<div class="budget">预算小计 <strong>${{escapeHtml(budget)}}</strong></div>` : ''}}</div><div class="route-strip"><span class="pin">⌖</span><span>${{escapeHtml(routeNames || day.title || '今日路线')}}</span></div><div class="timeline">${{day.items.map((item) => {{
        const place = item.placeId ? places.get(item.placeId) : null;
        const ids = unique([...(item.sourceIds || []), ...((place && place.sourceIds) || [])]);
        const links = (place && place.mapLinks) || item.mapLinks;
        const image = first(item.imageUrl, item.image, place && (place.imageUrl || place.image));
        const category = place?.confidence === 'avoid' ? 'avoid' : (place?.category || item.category || 'other');
        const meta = [place?.area || place?.city, item.duration, item.cost || place?.cost].filter(Boolean).join(' · ');
        return `<div class="item-row"><div class="time">${{escapeHtml(item.timeBlock || '')}}</div><button class="plan-card" type="button"><img class="thumb" alt="" src="${{image ? escapeHtml(image) : ''}}" onerror="this.removeAttribute('src')"><div class="card-copy"><div class="card-title-line"><strong>${{escapeHtml(item.title)}}</strong><span class="tag ${{tagClass(category)}}">${{categoryLabel(category)}}</span></div>${{meta ? `<div class="card-meta">${{escapeHtml(meta)}}</div>` : ''}}<p class="card-note">${{escapeHtml((item.notes && item.notes[0]) || place?.reason || '点击展开详情')}}</p></div><span class="check-circle"></span><div class="detail">${{place?.reason ? `<p>${{escapeHtml(place.reason)}}</p>` : ''}}${{(item.notes || []).slice(1).map(note => `<p>${{escapeHtml(note)}}</p>`).join('')}}${{item.transportToNext ? `<p>下一程：${{escapeHtml(item.transportToNext)}}</p>` : ''}}${{mapButtons(links)}}${{warningBlocks(item.warningIds || [])}}${{sourceList(ids)}}</div></button></div>`;
      }}).join('')}}</div>`;
      document.querySelectorAll('.plan-card').forEach(card => card.addEventListener('click', () => card.classList.toggle('open')));
      const firstMap = day.items.map(item => {{
        const place = item.placeId ? places.get(item.placeId) : null;
        return (place && place.mapLinks && place.mapLinks.amap) || (item.mapLinks && item.mapLinks.amap);
      }}).find(Boolean);
      $('today-map').onclick = () => firstMap ? window.open(firstMap, '_blank') : document.getElementById('day-panel').scrollIntoView({{behavior:'smooth'}});
    }}
    function renderBackup() {{
      const day = itinerary.days.find(item => item.id === activeDayId) || itinerary.days[0] || {{}};
      const assumptions = itinerary.trip.assumptions || [];
      $('backup-panel').innerHTML = `<div><strong>雨天备选</strong><div>${{escapeHtml(day.backup || assumptions[0] || '把室外点替换为商场、博物馆、咖啡和室内餐厅。')}}</div></div><span>›</span>`;
    }}
    function renderWarnings() {{
      $('warnings-panel').innerHTML = `<h2>避坑提醒</h2>${{itinerary.warnings.map(warning => `<div class="warning-box"><strong>${{escapeHtml(warning.title)}}</strong><p>${{escapeHtml(warning.detail || '')}}</p>${{warning.mitigation ? `<p>建议：${{escapeHtml(warning.mitigation)}}</p>` : ''}}</div>`).join('')}}`;
    }}
    function renderBudget() {{
      const dayBudgets = itinerary.days.map(day => `<p><strong>Day ${{day.dayNumber}}</strong>：${{escapeHtml(day.budgetEstimate || day.budget || '待估算')}}</p>`).join('');
      const totalBudget = first(itinerary.trip.budgetEstimate, itinerary.trip.budget, '待估算');
      $('budget-panel').innerHTML = `<h2>预算明细</h2><p><strong>总预算：</strong>${{escapeHtml(totalBudget)}}</p>${{dayBudgets}}<p class="muted">预算用于行程参考，实际价格以现场、预约平台或菜单为准。</p>`;
    }}
    function renderAssumptions() {{
      $('assumptions-panel').innerHTML = `<h2>数据边界</h2>${{(itinerary.trip.assumptions || []).map(item => `<p>${{escapeHtml(item)}}</p>`).join('')}}`;
    }}
    function renderSources() {{
      $('sources-panel').innerHTML = `<h2>小红书来源 · ${{itinerary.sources.length}} 条</h2>${{sourceList(itinerary.sources.map(source => source.id))}}`;
    }}
    function wireBottomBar() {{
      document.querySelectorAll('[data-scroll]').forEach(button => button.addEventListener('click', () => document.getElementById(button.dataset.scroll).scrollIntoView({{behavior:'smooth'}})));
      const totalBudget = first(itinerary.trip.budgetEstimate, itinerary.trip.budget, itinerary.days.map(day => day.budgetEstimate || day.budget).filter(Boolean).join(' / '));
      $('budget-summary').innerHTML = `<span class="coin">￥</span><span><small>预算总计</small><strong>${{escapeHtml(totalBudget || '待估算')}}</strong><small>不含往返交通</small></span>`;
      $('save-page-top').onclick = downloadPage;
      $('save-plan-bottom').onclick = downloadPage;
    }}
    function downloadPage() {{
      const html = '<!doctype html>\\n' + document.documentElement.outerHTML;
      const blob = new Blob([html], {{type: 'text/html;charset=utf-8'}});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'travel-plan.html';
      document.body.appendChild(link);
      link.click();
      URL.revokeObjectURL(link.href);
      link.remove();
    }}
    function render() {{
      renderHero();
      renderTabs();
      renderDay();
      renderBackup();
      renderBudget();
      renderWarnings();
      renderAssumptions();
      renderSources();
      wireBottomBar();
    }}
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

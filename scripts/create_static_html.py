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


def build_html(data: dict[str, Any]) -> str:
    payload = (
        json.dumps(data, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace("</script", "<\\/script")
    )
    title = html.escape(f"{data.get('trip', {}).get('destination', '旅行')}旅行计划", quote=True)
    template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITLE__</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", sans-serif; overflow-x: hidden; }
        .page-shell { width: min(100vw, 28rem); max-width: 100vw; min-width: 0; overflow-x: hidden; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .hero-cover {
            background:
                linear-gradient(180deg, rgba(15,23,42,.25), rgba(15,23,42,.82)),
                var(--hero-image),
                linear-gradient(135deg, #0f172a, #312e81);
            background-size: cover;
            background-position: center;
        }
        .hero-default {
            --hero-image: radial-gradient(circle at 72% 24%, rgba(249,115,22,.32), transparent 32%),
                linear-gradient(125deg, #172033, #28304c 56%, #115e59);
        }
        .detail-panel[hidden], .budget-dialog[hidden] { display: none; }
        .tab-btn { flex: 1 1 0; min-width: 0; }
        .place-thumb:empty::after {
            content: attr(data-label);
            color: currentColor;
            font-size: 11px;
            font-weight: 700;
            text-align: center;
        }
    </style>
</head>
<body class="bg-slate-50 min-h-screen text-gray-800 flex justify-center">
    <main class="page-shell bg-white shadow-xl min-h-screen flex flex-col justify-between">
        <div class="flex-1 overflow-y-auto hide-scrollbar">
            <header id="hero" class="hero-cover hero-default relative h-56 text-white p-5 flex flex-col justify-end">
                <h1 id="trip-title" class="text-2xl font-bold tracking-wide"></h1>
                <p id="trip-meta" class="text-xs text-slate-300 mt-1"></p>
                <div id="trip-tags" class="flex gap-2 mt-3 text-xs"></div>
                <button id="save-page" type="button" class="absolute top-5 right-5 border border-white/30 bg-white/10 px-3 py-1.5 rounded-full text-xs flex items-center gap-1 backdrop-blur-sm active:scale-95 transition-transform">
                    &#128190; 保存页面
                </button>
            </header>

            <nav id="tabs" class="flex border-b text-center text-sm font-medium text-gray-400 sticky top-0 bg-white z-10 shadow-sm shadow-black/5" aria-label="每日路线"></nav>
            <section id="day-content"></section>
            <section id="sources-panel" class="mx-4 mb-5 rounded-xl border border-slate-100 bg-white p-4"></section>
        </div>

        <footer class="border-t bg-white p-4 sticky bottom-0 z-20 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
            <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2 min-w-0 flex-1">
                    <div class="w-9 h-9 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold text-lg shrink-0">¥</div>
                    <div class="min-w-0">
                        <p id="budget-caption" class="text-[10px] text-gray-400 leading-none">预算总计</p>
                        <p id="budget-total" class="text-base font-black text-green-600 mt-1 truncate">待估算</p>
                    </div>
                </div>
                <button id="btn-budget" type="button" class="border border-blue-100 bg-blue-50 text-blue-600 rounded-xl px-3 py-2.5 text-[11px] font-bold active:scale-95 transition-transform shadow-sm shrink-0">
                    &#128202; 查看预算明细
                </button>
            </div>
            <p class="text-[9px] text-center text-gray-300 mt-3">行程仅供参考 · 小红书来源可追溯 · xhs-travel-planner</p>
        </footer>
    </main>

    <div id="budget-dialog" class="budget-dialog fixed inset-0 z-30 bg-slate-900/35 flex items-end justify-center" hidden>
        <div class="w-full max-w-md rounded-t-2xl bg-white p-5 shadow-2xl">
            <div class="flex justify-between items-center mb-4">
                <h2 class="font-bold text-slate-800">预计消费明细</h2>
                <button id="close-budget" type="button" class="text-gray-400 text-xl leading-none" aria-label="关闭">&times;</button>
            </div>
            <div id="budget-details" class="space-y-2 text-sm"></div>
            <p class="mt-4 text-[11px] text-gray-400">数据根据来源与规划估算，不包含未注明的大交通费用。</p>
        </div>
    </div>

    <script id="itinerary-data" type="application/json">__PAYLOAD__</script>
    <script>
        const itinerary = JSON.parse(document.getElementById('itinerary-data').textContent);
        const places = new Map((itinerary.places || []).map(place => [place.id, place]));
        const sources = new Map((itinerary.sources || []).map(source => [source.id, source]));
        const warningMap = new Map((itinerary.warnings || []).map(warning => [warning.id, warning]));
        let activeDayId = itinerary.days[0]?.id;
        const $ = id => document.getElementById(id);
        const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;', "'":'&#39;'}[char]));
        const uniq = values => [...new Set((values || []).filter(Boolean))];
        const first = (...values) => values.find(value => value !== undefined && value !== null && value !== '');

        function dayById() {
            return itinerary.days.find(day => day.id === activeDayId) || itinerary.days[0];
        }

        function displayRange() {
            const range = itinerary.trip.dateRange;
            if (!range) return '';
            return typeof range === 'string' ? range : [range.start, range.end].filter(Boolean).join(' - ');
        }

        function renderHero() {
            const trip = itinerary.trip;
            const days = trip.dayCount || itinerary.days.length;
            const nights = first(trip.nightCount, trip.nights, Math.max(days - 1, 0));
            $('trip-title').textContent = trip.title || `${trip.destination} ${days}天${nights}晚旅行计划`;
            $('trip-meta').textContent = [displayRange(), trip.travelers, trip.baseArea && `住 ${trip.baseArea}`].filter(Boolean).join(' · ');
            const style = String(trip.style || '');
            const tags = uniq([style.includes('美食') ? '美食' : '美食', style.includes('拍') ? '拍照' : '打卡', style.includes('轻松') ? '轻松路线' : '顺路路线']);
            const colors = ['bg-orange-500/80', 'bg-purple-600/80', 'bg-emerald-600/80'];
            $('trip-tags').innerHTML = tags.map((tag, index) => `<span class="${colors[index % colors.length]} px-2.5 py-1 rounded-full backdrop-blur-sm">${esc(tag)}</span>`).join('');
            const image = trip.heroImage || trip.coverImage;
            if (image) {
                $('hero').style.setProperty('--hero-image', `url("${String(image).replace(/"/g, '%22')}")`);
                $('hero').classList.remove('hero-default');
            }
        }

        function renderTabs() {
            $('tabs').innerHTML = itinerary.days.map(day =>
                `<button type="button" data-day="${esc(day.id)}" class="tab-btn flex-1 py-3 truncate ${day.id === activeDayId ? 'text-blue-600 border-b-2 border-blue-600 font-semibold' : 'text-gray-400'}">Day ${day.dayNumber}</button>`
            ).join('');
            $('tabs').querySelectorAll('.tab-btn').forEach(button => button.onclick = () => {
                activeDayId = button.dataset.day;
                renderTabs();
                renderDay();
            });
        }

        function categoryStyle(category, confidence) {
            if (confidence === 'avoid') return ['避坑', 'bg-red-50 text-red-600', 'bg-red-50 text-red-600 border-red-100', '&#9888;'];
            if (category === 'restaurant' || category === 'cafe') return ['美食', 'bg-orange-50 text-orange-600', 'bg-orange-50 text-orange-600 border-orange-100', '&#127858;'];
            if (category === 'attraction') return ['景点', 'bg-green-50 text-green-600', 'bg-emerald-50 text-emerald-600 border-emerald-100', '&#8962;'];
            return ['拍照', 'bg-purple-50 text-purple-600', 'bg-purple-50 text-purple-600 border-purple-100', '&#9673;'];
        }

        function sourceHtml(sourceIds) {
            const listed = uniq(sourceIds).map(id => sources.get(id)).filter(Boolean);
            if (!listed.length) return '<p class="text-[11px] text-amber-600 mt-2">暂无可读来源，此项仅作候选参考。</p>';
            return listed.map(source => `
                <article class="mt-2 rounded-lg bg-slate-50 p-2 text-[11px] text-slate-500">
                    <strong class="text-slate-700">${esc(source.title || source.id)}</strong>
                    <p>${esc([source.author, source.publishedDate].filter(Boolean).join(' · ') || '来源信息待补')}</p>
                    ${source.excerpt ? `<p class="mt-1">${esc(source.excerpt)}</p>` : ''}
                    ${source.url ? `<a class="mt-1 inline-block font-semibold text-blue-600" href="${esc(source.url)}" target="_blank" rel="noreferrer">打开小红书笔记</a>` : ''}
                </article>`).join('');
        }

        function detailHtml(item, place) {
            const links = item.mapLinks || place?.mapLinks || {};
            const sourceIds = uniq([...(item.sourceIds || []), ...(place?.sourceIds || [])]);
            const warningHtml = (item.warningIds || []).map(id => warningMap.get(id)).filter(Boolean).map(warning =>
                `<p class="mt-2 rounded-md bg-orange-50 px-2 py-1 text-[11px] text-orange-700">&#9888; ${esc(warning.title)} ${esc(warning.detail || '')}</p>`
            ).join('');
            return `
                <div class="detail-panel mt-2 border-t border-slate-100 pt-2" hidden>
                    ${place?.reason ? `<p class="text-[11px] text-gray-500">${esc(place.reason)}</p>` : ''}
                    ${(place?.tips || []).map(tip => `<p class="text-[11px] text-gray-500">提示：${esc(tip)}</p>`).join('')}
                    ${warningHtml}
                    <div class="flex gap-2 mt-2">
                        ${links.amap ? `<a href="${esc(links.amap)}" target="_blank" rel="noreferrer" class="text-[10px] text-blue-600 border border-blue-100 rounded-md px-2 py-1">&#128205; 打开高德地图</a>` : ''}
                        ${links.baidu ? `<a href="${esc(links.baidu)}" target="_blank" rel="noreferrer" class="text-[10px] text-slate-500 border border-slate-200 rounded-md px-2 py-1">百度备用</a>` : ''}
                    </div>
                    ${sourceHtml(sourceIds)}
                </div>`;
        }

        function itemHtml(item) {
            const place = item.placeId ? places.get(item.placeId) : null;
            const [label, badgeClass, thumbClass, icon] = categoryStyle(place?.category || item.category, place?.confidence);
            const image = first(item.imageUrl, item.image, place?.imageUrl, place?.image);
            const meta = [place?.area || place?.city, item.duration, item.cost || place?.cost].filter(Boolean).join(' · ');
            const warnings = (item.warningIds || []).map(id => warningMap.get(id)).filter(Boolean);
            const thumb = image
                ? `<img src="${esc(image)}" alt="" class="w-20 h-20 object-cover rounded-xl shrink-0">`
                : `<div class="place-thumb w-20 h-20 ${thumbClass} rounded-xl flex flex-col gap-1 items-center justify-center shrink-0 border" data-label="${esc(place?.name || label)}"><span class="text-xl">${icon}</span></div>`;
            return `
                <article class="flex gap-4 mb-6 relative items-start">
                    <div class="w-12 text-sm text-blue-600 font-bold pt-0.5 text-right">${esc(item.timeBlock)}</div>
                    <div class="w-3 h-3 rounded-full bg-white border-2 border-blue-500 z-10 mt-1.5 -ml-1.5 shadow-sm"></div>
                    <div class="flex-1 flex gap-3 min-w-0">
                        ${thumb}
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-1.5">
                                <h3 class="font-bold text-sm text-slate-800 truncate">${esc(item.title)}</h3>
                                <span class="text-[10px] ${badgeClass} px-1.5 py-0.5 rounded shrink-0">${label}</span>
                            </div>
                            ${meta ? `<p class="text-[11px] text-gray-400 mt-0.5">${esc(meta)}</p>` : ''}
                            <p class="text-[11px] text-gray-500 mt-1 line-clamp-1">${esc((item.notes || [])[0] || place?.reason || '')}</p>
                            ${warnings.slice(0, 1).map(warning => `<div class="inline-flex items-center text-[10px] bg-orange-50 text-orange-700 px-1.5 py-0.5 rounded-full mt-1.5 font-medium border border-orange-200">&#9888; ${esc(warning.title)}</div>`).join('')}
                            <button type="button" class="toggle-detail text-[10px] text-blue-600 border border-blue-100 rounded-md px-2 py-0.5 mt-1.5 active:bg-blue-50">展开详情 &#8964;</button>
                            ${detailHtml(item, place)}
                        </div>
                        <input type="checkbox" aria-label="标记完成" class="w-4 h-4 rounded border-gray-300 mt-1 text-blue-600 focus:ring-blue-500 shrink-0">
                    </div>
                </article>`;
        }

        function renderDay() {
            const day = dayById();
            const route = day.items.slice(0, 4).map(item => item.title).join(' → ');
            const warnings = (itinerary.warnings || []).filter(item => !item.dayId || item.dayId === day.id);
            $('day-content').innerHTML = `
                <div class="m-4 p-2.5 bg-slate-50/80 rounded-xl text-xs text-slate-600 flex items-center justify-center gap-2 border border-slate-100 truncate">
                    <span class="text-red-400">&#128205;</span><span class="truncate">${esc(route || day.title)}</span>
                </div>
                <div class="px-4 relative">
                    <div class="absolute left-10 top-4 bottom-4 w-0.5 bg-slate-100"></div>
                    ${day.items.map(itemHtml).join('') || '<p class="py-8 text-center text-sm text-gray-400">今日暂无详细数据。</p>'}
                </div>
                <aside class="mx-4 mb-4 p-3 rounded-xl bg-blue-50 border border-blue-100 text-xs text-slate-600 flex gap-3">
                    <span class="text-xl">&#127783;</span><div><strong class="text-blue-700">雨天备选</strong><p>${esc(day.backup || itinerary.trip.assumptions?.[0] || '优先调整为室内景点与餐饮路线。')}</p></div>
                </aside>
                ${warnings.length ? `<section class="mx-4 mb-4 rounded-xl border border-orange-100 bg-orange-50 p-3"><h2 class="text-xs font-bold text-orange-700 mb-2">避坑提醒</h2>${warnings.map(warning => `<p class="text-[11px] text-orange-700 mb-1">&#9888; ${esc(warning.title)}：${esc(warning.detail || '')}</p>`).join('')}</section>` : ''}`;
            document.querySelectorAll('.toggle-detail').forEach(button => button.onclick = event => {
                const panel = event.currentTarget.nextElementSibling;
                const open = panel.hasAttribute('hidden');
                panel.toggleAttribute('hidden', !open);
                event.currentTarget.innerHTML = open ? '收起详情 &#8963;' : '展开详情 &#8964;';
            });
        }

        function renderSources() {
            $('sources-panel').innerHTML = `<h2 class="text-sm font-bold text-slate-700 mb-2">小红书来源 · ${itinerary.sources.length} 条</h2>${sourceHtml(itinerary.sources.map(source => source.id))}`;
        }

        function renderBudget() {
            const trip = itinerary.trip;
            $('budget-caption').textContent = `预算总计${trip.travelers ? ` (${trip.travelers})` : ''}`;
            $('budget-total').textContent = first(trip.budgetEstimate, trip.budget, '待估算');
            $('budget-details').innerHTML = itinerary.days.map(day =>
                `<div class="flex justify-between border-b border-slate-100 pb-2"><span>Day ${day.dayNumber} · ${esc(day.title)}</span><strong class="text-green-600">${esc(first(day.budgetEstimate, day.budget, '待估算'))}</strong></div>`
            ).join('');
        }

        function downloadPage() {
            const content = '<!DOCTYPE html>\\n' + document.documentElement.outerHTML;
            const url = URL.createObjectURL(new Blob([content], {type: 'text/html;charset=utf-8'}));
            const link = document.createElement('a');
            link.href = url;
            link.download = 'travel-plan.html';
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(url);
        }

        function wireActions() {
            $('save-page').onclick = downloadPage;
            $('btn-budget').onclick = () => $('budget-dialog').removeAttribute('hidden');
            $('close-budget').onclick = () => $('budget-dialog').setAttribute('hidden', '');
            $('budget-dialog').onclick = event => {
                if (event.target === $('budget-dialog')) $('budget-dialog').setAttribute('hidden', '');
            };
        }

        renderHero();
        renderTabs();
        renderDay();
        renderSources();
        renderBudget();
        wireActions();
    </script>
</body>
</html>
"""
    return template.replace("__TITLE__", title).replace("__PAYLOAD__", payload)


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

---
name: xhs-travel-planner
description: Create source-backed travel itineraries from real 小红书/Xiaohongshu/RedNote notes after first opening a browser for the user to scan-code login, then turn the collected notes into deployable mobile-first single-file HTML pages with daily routes, expandable place cards, avoid-pit warnings, source citations, and 高德-first map links. Use when the user asks to research 小红书 travel notes, extract restaurants/attractions/hotels/避坑, make a route-checked trip plan, or generate a clickable travel planner webpage for GitHub Pages/mobile sharing.
---

# xhs-travel-planner

## Core Workflow

Use this skill to produce a source-backed, phone-friendly travel planner from real 小红书 notes. The final output is a deployable single-file `travel-plan.html` that can be renamed to `index.html` and published on GitHub Pages.

1. Confirm the brief only when missing details block the itinerary: destination, dates or trip length, travelers, travel style, must-go places, budget, pace, and hotel/base area if known.
2. Before searching, open a browser to 小红书 and require the user to scan-code login in that browser session. Prefer `python scripts/open_xhs_login.py --keyword "<destination> 美食 避坑"` when a local browser is available. Do not accept account passwords, Cookie strings, or verification codes.
3. Gather 小红书 notes only from the logged-in browser session. Do not use non-XHS web sources as itinerary evidence.
4. Do not bypass CAPTCHA, rate limits, robots controls, paywalls, or platform access restrictions. If the site asks for verification, ask the user to complete it in the browser.
5. Keep source traceability. Every place, restaurant, route tip, and warning must link back to one or more source records whenever possible.
6. Extract and deduplicate places, restaurants, shops, neighborhoods, transport tips, reservation notes, opening-hour risks, queue warnings, price warnings, and "avoid" advice.
7. Build a day-by-day route by clustering nearby items, checking map search/navigation links, and minimizing backtracking. Use 高德 links first and 百度 links as fallback.
8. Generate `travel-plan.html` with `scripts/create_static_html.py`.
9. Validate the itinerary with `scripts/validate_itinerary.py` before presenting it.

## User Templates

When the user asks how to use the skill or wants a reusable workflow, provide:

- `assets/brief-template.md` as the fill-in user brief.
- `references/prompt-templates.md` as the copy-paste 攻略提示词 set.
- `assets/itinerary-template.json` as the skeleton for the structured itinerary.

## Research Rules

Read `references/xhs-research-workflow.md` before collecting notes. Use it for query patterns, credibility checks, and extraction rules.

Minimum source standard:

- Prefer at least 8-15 relevant notes for a multi-day trip, or fewer only when the user provides a narrow source set.
- Record `id`, `platform`, `url`, `title`, `author`, `publishedDate`, and `capturedAt` when available.
- Mark recommendations as `confirmed` only when the source is specific enough to identify the place and reason.
- Mark vague mentions, uncertain names, or unsourced AI inferences as `candidate`.
- Preserve negative advice as `warnings`; do not bury it inside attraction notes.

## Itinerary Data

Use `references/itinerary-schema.md` as the canonical JSON contract. The top-level object must include:

- `trip`: destination, dates or day count, travelers, style, base area, and assumptions.
- `sources[]`: source records for 小红书 notes opened or verified in the logged-in browser session.
- `places[]`: normalized places with category, area, address if known, source IDs, confidence, tags, and map links.
- `warnings[]`: avoid-pit advice with severity, affected place/day when known, and source IDs.
- `days[]`: ordered route items with time blocks, transport notes, map links, source IDs, and alternatives.

Generate map links with:

```bash
python scripts/generate_map_links.py itinerary.json --write
```

Validate with:

```bash
python scripts/validate_itinerary.py itinerary.json
```

## HTML App Generation

Read `references/html-app-spec.md` before creating the app.

Default single-file output:

```bash
python scripts/generate_map_links.py itinerary.json --write
python scripts/validate_itinerary.py itinerary.json
python scripts/create_static_html.py itinerary.json travel-plan.html
```

To deploy on GitHub Pages, copy or upload `travel-plan.html` as `index.html` in the target Pages directory or repository root.

The HTML page must be mobile-first and include:

- The Tailwind CDN H5 layout specified in `references/html-app-spec.md`: cover hero, blue day tabs, compact route timeline, and bottom budget summary.
- A `保存页面` button that downloads the generated HTML in the browser.
- Expandable place details with 高德 and 百度 map buttons.
- Source links placed inside each related place detail; do not add a long standalone source list.
- Daily and overall 避坑 information.
- No standalone `数据边界` section; surface uncertainty only where it affects a place or warning.
- Empty states for missing addresses, no warnings, and no source URL.

## Quality Bar

Before final delivery:

- Confirm every non-obvious recommendation has a source ID or is labeled as an assumption/candidate.
- Confirm every displayed map button is generated from name plus city/area/address, or from coordinates when available.
- Prefer practical route order over "top ranked" order when the two conflict.
- Explain any unresolved uncertainty: unverified opening hours, possible seasonal closure, unclear branch, or missing exact address.
- Run `quick_validate.py` on the skill when editing this skill itself.

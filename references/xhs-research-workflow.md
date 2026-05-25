# 小红书 Research Workflow

Use this guide when gathering real 小红书/Xiaohongshu/RedNote notes for a travel itinerary.

## Mandatory Login Step

- Always begin by opening a browser to 小红书 search or homepage and asking the user to scan-code login.
- Prefer running `python scripts/open_xhs_login.py --keyword "<destination> 美食 避坑"` to open a dedicated browser profile.
- Continue only after the user confirms the opened browser session is logged in and can display note cards.
- Never ask for or store account passwords, Cookie strings, local storage values, SMS codes, or CAPTCHA answers.
- If a verification challenge appears, pause and ask the user to complete it manually in the browser.
- If the logged-in browser cannot be automated or read, stop and explain that the current environment cannot collect notes from 小红书.

## Access Boundary

- Use only the user's logged-in browser session to collect 小红书 notes.
- Do not treat non-XHS web pages as evidence for places, routes, or warnings.
- Do not bypass login, CAPTCHA, rate limits, access controls, or platform restrictions.
- If a note cannot be opened or copied, record it as inaccessible and move on.
- User-provided XHS links can guide search, but the source content should still be opened or verified in the logged-in browser session when possible.

## Search Patterns

Combine destination with intent-specific terms:

- Core route: `<destination> 行程`, `<destination> 路线`, `<destination> 几天几晚`, `<destination> citywalk`
- Food: `<destination> 美食`, `<destination> 餐厅`, `<destination> 咖啡`, `<destination> 夜市`
- Avoid-pit: `<destination> 避坑`, `<destination> 雷`, `<destination> 排队`, `<destination> 不推荐`
- Logistics: `<destination> 交通`, `<destination> 预约`, `<destination> 门票`, `<destination> 营业时间`
- Neighborhoods: `<destination> 住宿区域`, `<destination> 商圈`, `<destination> 地铁`

For multi-day trips, search both the full trip and individual neighborhoods/attractions.

## Coverage And Sampling

- Open and retain at least 8 notes for a one-day/narrow brief, 15 notes for a 2-4 day trip, and 20 notes for trips of 5 days or more.
- Use at least five distinct query intents for a multi-day plan: route, food, avoid-pit, logistics, and a key area/attraction. Add restaurant or night-market searches for food-first briefs.
- Browse beyond the first few cards when results are repetitive or promotional. Deduplicate repost-like or near-identical recommendations.
- Prefer notes whose visible engagement is strong relative to the other results returned for the same query. Likes and saves are useful selection signals; comments can reveal current queue, closure, or branch issues.
- Do not treat engagement as truth. Cross-check heavily liked recommendations against other independent notes, especially for price, queue, closures, reservations, and "避坑" claims.
- If fewer notes are accessible because of verification, limited results, or user-supplied links only, record the limitation instead of silently lowering the standard.

## Source Capture

Create one `sources[]` item per 小红书 note opened or verified in the logged-in browser session. Capture what is available:

- `id`: stable local ID, such as `xhs-001`
- `platform`: `xhs`, `user`, or another explicit source type
- `url`
- `title`
- `author`
- `publishedDate`
- `capturedAt`
- `excerpt`: short paraphrase or copied snippet allowed by the user
- `likes`: visible like count, as a number or visible display string
- `collects`: visible save/favorite count, as a number or visible display string
- `comments`: visible comment count, as a number or visible display string
- `query`: search phrase that surfaced this note

Do not invent missing URLs, authors, dates, note titles, or engagement numbers. Use `null` for unknown fields. A retained source must be an opened/verified real note, not an AI-written summary or a result card that could not be opened.

## Credibility Checks

Prefer notes that include:

- Visible higher likes/saves among comparable search results, while still checking substance.
- Specific place names, branches, or addresses.
- Recent dates or comments that match the trip season.
- Photos, receipts, route screenshots, or concrete timing details.
- Multiple independent notes agreeing on the same warning or recommendation.

Treat these as weaker:

- High engagement but no usable visit detail or clear place identification.
- Pure listicles with no visit detail.
- Reposts, generic influencer roundups, or suspiciously promotional wording.
- Notes that name a place but provide no reason, address, branch, or context.
- Old notes for restaurants, pop-ups, exhibitions, seasonal sights, or ticket policies.

## Extraction Rules

For each source, extract:

- Places: attractions, restaurants, cafes, shops, hotels, neighborhoods, stations.
- Reasons: what the source says is good, bad, crowded, expensive, photogenic, or skippable.
- Constraints: opening hours, reservation needs, ticketing, queue timing, transport, weather dependence.
- Avoid-pit items: scams, overpriced places, branch confusion, long detours, poor food, closures, tourist traps.

Normalize duplicate places by name plus city/area. Keep branch names when branch confusion matters.

## Confidence Labels

Use:

- `confirmed`: specific enough and source-backed.
- `candidate`: plausible but vague, single weak source, branch unclear, or address missing.
- `avoid`: primarily a negative recommendation.
- `assumption`: created by reasoning rather than directly stated by a source.

The final app may show candidates, but it must visually separate them from confirmed route items.

## Completion Check

Before itinerary generation:

- Count retained, opened sources against the minimum for the trip length.
- Check that high-importance route items are supported by more than one independent note when available.
- Check that visible engagement was captured for notes where the page displayed it.
- Report access limitations or missing engagement fields rather than filling them in.

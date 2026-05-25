# Mobile H5 Travel Plan Spec

Generate one deployable `travel-plan.html` with `scripts/create_static_html.py`. The template uses Tailwind CSS via CDN as in the approved H5 design, and works as `index.html` on GitHub Pages.

## Required Experience

- Design mobile-first as a polished H5 travel page; desktop should center the same phone-width experience.
- Open on the itinerary, not a marketing landing page.
- Keep controls thumb-friendly: day tabs, expandable details/map links, source citations, and a sticky bottom budget bar.
- Do not render fake phone status bars, back buttons, favorite buttons, share circles, or other native-app chrome.
- Let the user scan the route in order without reading long prose.
- Make uncertainty concise: label candidate or missing-address items at the related place card, without a separate data-boundary section.

## Required Views

- Immersive H5 hero: cover image, trip title, dates, travelers, style chips, and a `保存页面` button.
- White itinerary body below the hero.
- Day tabs: one tab per day with a short blue active underline.
- Route strip: a compact `地点 A -> 地点 B -> 地点 C` summary under the tabs.
- Daily route timeline: ordered items with time block on the left, dotted vertical line, place card on the right.
- Place detail expansion: reason, tips, warnings, source citations, 高德 button, 百度 button.
- Backup card: rainy-day or queue-heavy alternative plan for the active day/trip.
- Budget detail section.
- Avoid-pit section: overall warnings and day-specific warnings.
- Bottom bar: budget summary and `查看预算明细` button.

## Interaction Rules

- Day tabs update the visible route without full page reload.
- Place cards expand/collapse.
- Map buttons open in a new tab/window.
- `保存页面` downloads the current HTML in the browser as `travel-plan.html`; do not replace it with an alert.
- Each place detail shows only its related source citation links to the originating 小红书 notes when URLs exist.
- Do not create a standalone `小红书来源` list or `数据边界` section below the itinerary.
- Missing map data should show disabled explanatory text, not a broken link.

## Visual Constraints

- Prioritize readable Chinese text on mobile.
- Use a blue route accent, white cards, muted gray metadata, and small colored category pills.
- Match the Tailwind H5 template: `max-w-md`, slate background, `h-56` hero, blue active tabs, compact timeline, and green budget summary.
- Use small H5-like radii for the hero/body/card system; avoid fake iOS status UI.
- Avoid decorative cards inside cards.
- Use stable dimensions for tabs, buttons, badges, and timeline markers.
- Do not make a one-color theme; the app should feel like a travel utility, not a flat poster.
- Keep text inside buttons and cards from overflowing on narrow screens.
- Prefer real or supplied image URLs for hero/place thumbnails. If no image exists, the page must still render with a graceful fallback.

## Acceptance Criteria

- `python scripts/create_static_html.py itinerary.json travel-plan.html` succeeds.
- At 390px width, day tabs, route cards, warning blocks, and map buttons do not overlap.
- The first viewport shows the hero and the start of the itinerary sheet.
- Route items look like a timeline: visible times, markers, and cards.
- Every displayed recommendation exposes related source links in its expanded detail, or shows a compact candidate label when needed.
- Every map link uses encoded query text or coordinates.
- The app remains useful with no warnings, no exact addresses, or sources without URLs.

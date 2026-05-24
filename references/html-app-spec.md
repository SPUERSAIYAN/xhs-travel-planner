# Mobile H5 Travel Plan Spec

Generate a self-contained `travel-plan.html` with `scripts/create_static_html.py`. The file must work when opened directly, renamed to `index.html`, or uploaded to GitHub Pages.

## Required Experience

- Design mobile-first as a polished H5 travel page; desktop should center the same phone-width experience.
- Open on the itinerary, not a marketing landing page.
- Keep controls thumb-friendly: day tabs, clear map buttons, expandable source citations, and a sticky bottom action bar.
- Do not render fake phone status bars, back buttons, favorite buttons, share circles, or other native-app chrome.
- Let the user scan the route in order without reading long prose.
- Make uncertainty visible: candidates, assumptions, and missing address states should be labeled.

## Required Views

- Immersive H5 hero: cover image, trip title, dates, travelers, style chips, and a `保存页面` button.
- Flat white itinerary body slightly overlapping the hero.
- Day tabs: one tab per day with a short blue active underline.
- Route strip: a compact `地点 A -> 地点 B -> 地点 C` summary under the tabs.
- Daily route timeline: ordered items with time block on the left, dotted vertical line, place card on the right.
- Place detail expansion: reason, tips, warnings, source citations, 高德 button, 百度 button.
- Backup card: rainy-day or queue-heavy alternative plan for the active day/trip.
- Budget detail section.
- Avoid-pit section: overall warnings and day-specific warnings.
- Source panel: source title, platform, author/date if available, and link when available.
- Bottom action bar: budget summary, view budget, today map, save itinerary.

## Interaction Rules

- Day tabs update the visible route without full page reload.
- Place cards expand/collapse.
- Map buttons open in a new tab/window.
- `保存页面` and `保存行程` download the current single-file HTML in the browser as `travel-plan.html`.
- Source buttons expose citations without hiding the route.
- Missing map data should show disabled explanatory text, not a broken link.

## Visual Constraints

- Prioritize readable Chinese text on mobile.
- Use a blue route accent, white cards, muted gray metadata, and small colored category pills.
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
- Every displayed recommendation has visible source or assumption/candidate labeling.
- Every map link uses encoded query text or coordinates.
- The app remains useful with no warnings, no exact addresses, or sources without URLs.

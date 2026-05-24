# Mobile App-Style HTML Spec

Generate a self-contained `travel-plan.html` with `scripts/create_static_html.py`. The file must work when opened directly, renamed to `index.html`, or uploaded to GitHub Pages.

## Required Experience

- Design mobile-first as a polished phone travel app; desktop should center the same phone-width experience.
- Open on the itinerary, not a marketing landing page.
- Keep controls thumb-friendly: day tabs, clear map buttons, expandable source citations, and a sticky bottom action bar.
- Let the user scan the route in order without reading long prose.
- Make uncertainty visible: candidates, assumptions, and missing address states should be labeled.

## Required Views

- Immersive hero: destination in large Chinese type, English/script subtitle, dates, travelers, style chips, weather/budget hint, and optional cover image.
- Rounded itinerary sheet: white panel overlapping the hero with iOS-like radius and shadow.
- Day tabs: one tab per day with a short yellow active underline.
- Daily route timeline: ordered items with time block on the left, dotted vertical line, place card on the right.
- Place detail expansion: reason, tips, warnings, source citations, 高德 button, 百度 button.
- Backup card: rainy-day or queue-heavy alternative plan for the active day/trip.
- Avoid-pit section: overall warnings and day-specific warnings.
- Source panel: source title, platform, author/date if available, and link when available.
- Bottom action bar: budget, today map, share/copy link.

## Interaction Rules

- Day tabs update the visible route without full page reload.
- Place cards expand/collapse.
- Map buttons open in a new tab/window.
- Source buttons expose citations without hiding the route.
- Missing map data should show disabled explanatory text, not a broken link.

## Visual Constraints

- Prioritize readable Chinese text on mobile.
- Use a warm yellow accent, white cards, muted gray metadata, and small colored category pills.
- Use large rounded corners for the hero/sheet, but keep individual cards controlled and clean.
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

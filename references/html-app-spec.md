# Mobile HTML App Spec

Generate a self-contained `travel-plan.html` with `scripts/create_static_html.py`. The file must work when opened directly, renamed to `index.html`, or uploaded to GitHub Pages.

## Required Experience

- Design mobile-first; desktop may be a wider version of the same itinerary, not a separate dashboard.
- Open on the itinerary, not a marketing landing page.
- Keep controls thumb-friendly: sticky day tabs, clear map buttons, expandable source citations.
- Let the user scan the route in order without reading long prose.
- Make uncertainty visible: candidates, assumptions, and missing address states should be labeled.

## Required Views

- Trip header: destination, dates or day count, base area, travel style, and assumption count.
- Day tabs: one tab per day, sticky under the header.
- Daily route timeline: ordered items with time block, place, category, tags, source count, and notes.
- Place detail expansion: reason, tips, warnings, source citations, 高德 button, 百度 button.
- Avoid-pit section: overall warnings and day-specific warnings.
- Source panel: source title, platform, author/date if available, and link when available.

## Interaction Rules

- Day tabs update the visible route without full page reload.
- Place cards expand/collapse.
- Map buttons open in a new tab/window.
- Source buttons expose citations without hiding the route.
- Missing map data should show disabled explanatory text, not a broken link.

## Visual Constraints

- Prioritize readable Chinese text on mobile.
- Avoid decorative cards inside cards.
- Use stable dimensions for tabs, buttons, badges, and timeline markers.
- Do not make a one-color theme; use a restrained but varied palette.
- Keep text inside buttons and cards from overflowing on narrow screens.

## Acceptance Criteria

- `python scripts/create_static_html.py itinerary.json travel-plan.html` succeeds.
- At 390px width, day tabs, route cards, warning blocks, and map buttons do not overlap.
- Every displayed recommendation has visible source or assumption/candidate labeling.
- Every map link uses encoded query text or coordinates.
- The app remains useful with no warnings, no exact addresses, or sources without URLs.

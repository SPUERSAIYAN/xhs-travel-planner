# Itinerary JSON Contract

Use this as the canonical data shape for the generated travel planner. The scripts validate the required parts of this contract without requiring a full JSON Schema dependency.

## Top-Level Shape

```json
{
  "trip": {},
  "sources": [],
  "places": [],
  "warnings": [],
  "days": []
}
```

## `trip`

Required:

- `destination`: city, region, or country.
- `dayCount`: integer greater than zero.

Recommended:

- `dateRange`: display string or `{ "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" }`.
- `travelers`: traveler count and profile.
- `style`: food, family, citywalk, photography, museum, relaxed, budget, luxury, etc.
- `baseArea`: hotel or preferred area.
- `destinationEn` or `englishName`: short English/script subtitle for the mobile hero.
- `heroImage` or `coverImage`: remote image URL for the top hero.
- `weather` or `weatherText`: short display text, such as `26°C` or `多云 26°C`.
- `budgetEstimate` or `budget`: trip-level budget display string.
- `assumptions[]`: assumptions made because the user or sources did not specify details.

## `sources[]`

Required:

- `id`: stable ID used by `sourceIds`.
- `platform`: `xhs`, `user`, `web`, or another explicit source type.
- `title`: string or `null`.
- `url`: string or `null`.

Recommended:

- `author`
- `publishedDate`
- `capturedAt`
- `excerpt`
- `mobileShareUrl`: platform-generated share/copy-link URL for the mobile button, typically `https://xhslink.com/...`.
- `desktopUrl`: optional PC browser note URL when distinct from `url`.
- `query`: query phrase used to discover the note.
- `likes`: visible like count when shown.
- `collects`: visible save/favorite count when shown.
- `comments`: visible comment count when shown.

Every source should have either `url` or `title`; otherwise it is too hard to audit. For XHS mobile output, capture `mobileShareUrl` using the note's own share/copy-link action rather than constructing it. Retain at least 15 opened sources for 2-4 days and 20 for 5+ days, unless access limitations are recorded. Engagement fields are observation-only: do not infer or fabricate unavailable counts.

## `places[]`

Required:

- `id`: stable ID.
- `name`: display name.
- `city`: city or destination.
- `category`: `attraction`, `restaurant`, `cafe`, `shop`, `hotel`, `neighborhood`, `transport`, or `other`.
- `confidence`: `confirmed`, `candidate`, `avoid`, or `assumption`.
- `sourceIds[]`: IDs from `sources[]`; empty only for explicit assumptions.

Recommended:

- `area`
- `address`
- `coordinates`: `{ "lat": number, "lng": number }`
- `tags[]`
- `reason`
- `tips[]`
- `imageUrl` or `image`: remote image URL for route cards.
- `cost`: short display string such as `人均 ¥90`.
- `mapLinks`: `{ "amap": string, "baidu": string }`

Deduplicate by normalized `name + city + area`. Preserve branch names when they change the visitor experience.

## `warnings[]`

Required:

- `id`
- `title`
- `severity`: `low`, `medium`, or `high`.
- `sourceIds[]`

Recommended:

- `placeId`
- `dayId`
- `detail`
- `mitigation`
- `category`: `queue`, `reservation`, `price`, `transport`, `closure`, `weather`, `tourist-trap`, or `other`.

## `days[]`

Required:

- `id`: stable ID, such as `day-1`.
- `dayNumber`: integer.
- `title`
- `items[]`

Each `items[]` entry requires:

- `id`
- `timeBlock`: morning, lunch, afternoon, dinner, evening, flexible, or a display string.
- `title`
- `placeId` when tied to a known place.
- `sourceIds[]`

Recommended per item:

- `duration`
- `transportToNext`
- `mapLinks`
- `imageUrl` or `image`
- `cost`
- `notes[]`
- `warningIds[]`
- `alternatives[]`

Recommended per day:

- `summary`
- `budgetEstimate` or `budget`
- `backup`: rainy-day or queue-heavy alternative plan.

## Map Links

Use 高德 as primary and 百度 as fallback:

```json
{
  "mapLinks": {
    "amap": "https://uri.amap.com/search?keyword=...",
    "baidu": "https://map.baidu.com/search/..."
  }
}
```

When exact coordinates are unknown, generate search links from `name + city + area/address`. Do not invent coordinates.

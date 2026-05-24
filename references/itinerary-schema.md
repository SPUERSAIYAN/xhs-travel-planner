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

Every source should have either `url` or `title`; otherwise it is too hard to audit.

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
- `notes[]`
- `warningIds[]`
- `alternatives[]`

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

#!/usr/bin/env python3
"""Generate 高德 and 百度 map links for itinerary places and route items."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote


def query_for_place(place: dict[str, Any], destination: str = "") -> str:
    parts = [
        place.get("name"),
        place.get("address"),
        place.get("area"),
        place.get("city") or destination,
    ]
    return " ".join(str(part).strip() for part in parts if part).strip()


def amap_link(place: dict[str, Any], destination: str = "") -> str:
    coords = place.get("coordinates")
    name = str(place.get("name") or "目的地")
    if isinstance(coords, dict) and coords.get("lng") is not None and coords.get("lat") is not None:
        return (
            "https://uri.amap.com/marker"
            f"?position={quote(str(coords['lng']))},{quote(str(coords['lat']))}"
            f"&name={quote(name)}"
        )
    query = query_for_place(place, destination)
    city = str(place.get("city") or destination or "")
    return f"https://uri.amap.com/search?keyword={quote(query)}&city={quote(city)}&view=map"


def baidu_link(place: dict[str, Any], destination: str = "") -> str:
    query = query_for_place(place, destination)
    return f"https://map.baidu.com/search/{quote(query)}"


def ensure_place_links(data: dict[str, Any]) -> dict[str, Any]:
    destination = str(data.get("trip", {}).get("destination") or "")
    place_by_id: dict[str, dict[str, Any]] = {}

    for place in data.get("places", []):
        if not isinstance(place, dict):
            continue
        place.setdefault("mapLinks", {})
        place["mapLinks"]["amap"] = amap_link(place, destination)
        place["mapLinks"]["baidu"] = baidu_link(place, destination)
        if place.get("id"):
            place_by_id[str(place["id"])] = place

    for day in data.get("days", []):
        if not isinstance(day, dict):
            continue
        for item in day.get("items", []):
            if not isinstance(item, dict):
                continue
            place = place_by_id.get(str(item.get("placeId")))
            if place:
                item["mapLinks"] = dict(place.get("mapLinks", {}))
            elif item.get("title"):
                synthetic_place = {
                    "name": item.get("title"),
                    "city": destination,
                    "area": item.get("area"),
                    "address": item.get("address"),
                }
                item["mapLinks"] = {
                    "amap": amap_link(synthetic_place, destination),
                    "baidu": baidu_link(synthetic_place, destination),
                }

    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Add 高德 and 百度 map links to itinerary JSON.")
    parser.add_argument("itinerary", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path. Defaults to stdout unless --write is used.")
    parser.add_argument("--write", action="store_true", help="Rewrite the input file in place.")
    args = parser.parse_args()

    data = json.loads(args.itinerary.read_text(encoding="utf-8"))
    enriched = ensure_place_links(data)
    text = json.dumps(enriched, ensure_ascii=False, indent=2) + "\n"

    if args.write:
        args.itinerary.write_text(text, encoding="utf-8")
    elif args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

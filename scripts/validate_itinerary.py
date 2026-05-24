#!/usr/bin/env python3
"""Validate xhs-travel-planner itinerary JSON."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


VALID_CONFIDENCE = {"confirmed", "candidate", "avoid", "assumption"}
VALID_SEVERITY = {"low", "medium", "high"}


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Top-level itinerary must be a JSON object")
    return data


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    trip = data.get("trip")
    sources = as_list(data.get("sources"))
    places = as_list(data.get("places"))
    trip_warnings = as_list(data.get("warnings"))
    days = as_list(data.get("days"))

    require(isinstance(trip, dict), "trip must be an object", errors)
    require(isinstance(data.get("sources"), list), "sources must be an array", errors)
    require(isinstance(data.get("places"), list), "places must be an array", errors)
    require(isinstance(data.get("warnings"), list), "warnings must be an array", errors)
    require(isinstance(data.get("days"), list), "days must be an array", errors)

    if isinstance(trip, dict):
        require(bool(trip.get("destination")), "trip.destination is required", errors)
        require(isinstance(trip.get("dayCount"), int) and trip["dayCount"] > 0, "trip.dayCount must be a positive integer", errors)

    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source_id = source.get("id")
        require(isinstance(source_id, str) and bool(source_id), f"{prefix}.id is required", errors)
        require(bool(source.get("platform")), f"{prefix}.platform is required", errors)
        if source_id:
            source_ids.add(source_id)
        if not source.get("url") and not source.get("title"):
            warnings.append(f"{prefix} should include url or title for auditability")

    place_ids: set[str] = set()
    place_keys: list[str] = []
    for index, place in enumerate(places):
        prefix = f"places[{index}]"
        if not isinstance(place, dict):
            errors.append(f"{prefix} must be an object")
            continue
        place_id = place.get("id")
        name = place.get("name")
        confidence = place.get("confidence")
        require(isinstance(place_id, str) and bool(place_id), f"{prefix}.id is required", errors)
        require(isinstance(name, str) and bool(name), f"{prefix}.name is required", errors)
        require(bool(place.get("city")), f"{prefix}.city is required", errors)
        require(bool(place.get("category")), f"{prefix}.category is required", errors)
        require(confidence in VALID_CONFIDENCE, f"{prefix}.confidence must be one of {sorted(VALID_CONFIDENCE)}", errors)
        if place_id:
            place_ids.add(place_id)
        if name:
            key = "|".join(str(place.get(part, "")).strip().lower() for part in ("name", "city", "area"))
            place_keys.append(key)
        source_refs = as_list(place.get("sourceIds"))
        if confidence != "assumption":
            require(bool(source_refs), f"{prefix}.sourceIds is required unless confidence is assumption", errors)
        for source_id in source_refs:
            if source_id not in source_ids:
                errors.append(f"{prefix}.sourceIds references unknown source {source_id!r}")
        if not place.get("address") and not place.get("area") and not place.get("coordinates"):
            warnings.append(f"{prefix} has no address, area, or coordinates; map search may be broad")

    duplicate_places = [key for key, count in Counter(place_keys).items() if key and count > 1]
    for key in duplicate_places:
        warnings.append(f"Duplicate normalized place key: {key}")

    warning_ids: set[str] = set()
    for index, item in enumerate(trip_warnings):
        prefix = f"warnings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        warning_id = item.get("id")
        require(isinstance(warning_id, str) and bool(warning_id), f"{prefix}.id is required", errors)
        require(bool(item.get("title")), f"{prefix}.title is required", errors)
        require(item.get("severity") in VALID_SEVERITY, f"{prefix}.severity must be one of {sorted(VALID_SEVERITY)}", errors)
        if warning_id:
            warning_ids.add(warning_id)
        for source_id in as_list(item.get("sourceIds")):
            if source_id not in source_ids:
                errors.append(f"{prefix}.sourceIds references unknown source {source_id!r}")
        place_id = item.get("placeId")
        if place_id and place_id not in place_ids:
            errors.append(f"{prefix}.placeId references unknown place {place_id!r}")

    day_numbers: list[int] = []
    for index, day in enumerate(days):
        prefix = f"days[{index}]"
        if not isinstance(day, dict):
            errors.append(f"{prefix} must be an object")
            continue
        require(bool(day.get("id")), f"{prefix}.id is required", errors)
        require(isinstance(day.get("dayNumber"), int), f"{prefix}.dayNumber must be an integer", errors)
        require(bool(day.get("title")), f"{prefix}.title is required", errors)
        require(isinstance(day.get("items"), list), f"{prefix}.items must be an array", errors)
        if isinstance(day.get("dayNumber"), int):
            day_numbers.append(day["dayNumber"])
        for item_index, route_item in enumerate(as_list(day.get("items"))):
            item_prefix = f"{prefix}.items[{item_index}]"
            if not isinstance(route_item, dict):
                errors.append(f"{item_prefix} must be an object")
                continue
            require(bool(route_item.get("id")), f"{item_prefix}.id is required", errors)
            require(bool(route_item.get("timeBlock")), f"{item_prefix}.timeBlock is required", errors)
            require(bool(route_item.get("title")), f"{item_prefix}.title is required", errors)
            place_id = route_item.get("placeId")
            if place_id and place_id not in place_ids:
                errors.append(f"{item_prefix}.placeId references unknown place {place_id!r}")
            for warning_id in as_list(route_item.get("warningIds")):
                if warning_id not in warning_ids:
                    errors.append(f"{item_prefix}.warningIds references unknown warning {warning_id!r}")
            for source_id in as_list(route_item.get("sourceIds")):
                if source_id not in source_ids:
                    errors.append(f"{item_prefix}.sourceIds references unknown source {source_id!r}")

    for duplicate_day in [number for number, count in Counter(day_numbers).items() if count > 1]:
        errors.append(f"Duplicate dayNumber: {duplicate_day}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an xhs-travel-planner itinerary JSON file.")
    parser.add_argument("itinerary", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    try:
        data = load_json(args.itinerary)
        errors, warnings = validate(data)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors or (args.strict and warnings):
        return 1

    print(f"OK: {args.itinerary} is valid ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

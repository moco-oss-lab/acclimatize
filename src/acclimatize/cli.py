"""Command line interface.

Usage:
    acclimatize "Lima:0:2,Sacred Valley:2800:2,Machu Picchu:2430:1,Cusco:3400:2,Uyuni:3656:2"

Each stop is ``name:altitude_m:nights`` and stops are comma separated.
"""

from __future__ import annotations

import sys

from .core import Stop, assess_itinerary


def parse_stops(spec: str) -> list[Stop]:
    stops: list[Stop] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.rsplit(":", 2)
        if len(parts) != 3:
            raise ValueError(
                f"Invalid stop {chunk!r}; expected name:altitude_m:nights"
            )
        name, altitude, nights = parts
        stops.append(
            Stop(name=name.strip(), altitude_m=int(altitude), nights=int(nights))
        )
    if len(stops) < 2:
        raise ValueError("Provide at least two stops")
    return stops


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip())
        return 2
    try:
        stops = parse_stops(argv[0])
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    report = assess_itinerary(stops)
    print(report.format())
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

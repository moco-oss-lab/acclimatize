"""Altitude acclimatisation heuristics for multi-stop itineraries.

The rules implemented here are planning heuristics, not medical advice:

* Entering high altitude from below 3,000 m, avoid increasing the
  sleeping altitude by more than 1,000 m in a single move.
* Once already sleeping at or above 3,000 m, avoid increasing the
  sleeping altitude by more than 500 m in a single move.
* After a cumulative gain of 1,000 m above 3,000 m, plan at least one
  extra rest night before ascending further.
* Any single move that lands at or above 3,500 m after a gain of more
  than 1,000 m is flagged as high risk.
"""

from __future__ import annotations

from dataclasses import dataclass, field

HIGH_ALTITUDE_THRESHOLD_M = 3000
VERY_HIGH_ALTITUDE_M = 3500
MAX_SLEEPING_GAIN_M = 500
MAX_ENTRY_GAIN_M = 1000
REST_GAIN_INTERVAL_M = 1000


@dataclass(frozen=True)
class Stop:
    """One overnight stop on an itinerary."""

    name: str
    altitude_m: int
    nights: int = 1

    def __post_init__(self) -> None:
        if self.altitude_m < 0:
            raise ValueError("altitude_m must be >= 0")
        if self.nights < 1:
            raise ValueError("nights must be >= 1")


@dataclass(frozen=True)
class Warning:
    """A single acclimatisation warning for a move between two stops."""

    from_stop: str
    to_stop: str
    gain_m: int
    severity: str  # "medium" or "high"
    message: str


@dataclass
class Report:
    warnings: list[Warning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.warnings

    def format(self) -> str:
        if self.ok:
            return "OK: no rapid-ascent warnings for this itinerary."
        lines = ["Acclimatisation warnings:"]
        for w in self.warnings:
            lines.append(
                f"- [{w.severity}] {w.from_stop} -> {w.to_stop} "
                f"(+{w.gain_m} m): {w.message}"
            )
        return "\n".join(lines)


def assess_itinerary(stops: list[Stop]) -> Report:
    """Assess consecutive sleeping-altitude moves in ``stops``."""
    report = Report()
    gain_since_rest = 0

    for prev, curr in zip(stops, stops[1:]):
        gain = curr.altitude_m - prev.altitude_m

        if curr.altitude_m < HIGH_ALTITUDE_THRESHOLD_M or gain <= 0:
            if curr.nights >= 2:
                gain_since_rest = 0
            continue

        max_gain = (
            MAX_SLEEPING_GAIN_M
            if prev.altitude_m >= HIGH_ALTITUDE_THRESHOLD_M
            else MAX_ENTRY_GAIN_M
        )
        warned = False
        if gain > max_gain:
            warned = True
            severity = (
                "high"
                if curr.altitude_m >= VERY_HIGH_ALTITUDE_M and gain > 1000
                else "medium"
            )
            report.warnings.append(
                Warning(
                    from_stop=prev.name,
                    to_stop=curr.name,
                    gain_m=gain,
                    severity=severity,
                    message=(
                        f"Sleeping altitude rises by more than {max_gain} m "
                        "in one move at high altitude. Add an intermediate "
                        "stop or extra nights before this move."
                    ),
                )
            )

        gain_since_rest += max(gain, 0)
        if not warned and gain_since_rest >= REST_GAIN_INTERVAL_M and curr.nights < 2:
            report.warnings.append(
                Warning(
                    from_stop=prev.name,
                    to_stop=curr.name,
                    gain_m=gain,
                    severity="medium",
                    message=(
                        "Cumulative gain of 1,000 m or more above 3,000 m "
                        "without a rest stop of at least 2 nights. Plan a "
                        "rest day here."
                    ),
                )
            )
            gain_since_rest = 0

        if curr.nights >= 2:
            gain_since_rest = 0

    return report

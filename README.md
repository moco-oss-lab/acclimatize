# acclimatize

Check a multi-stop itinerary for rapid-ascent altitude risks, before the
headache does it for you.

`acclimatize` applies simple, well-known acclimatisation heuristics to the
sleeping altitudes of a trip:

- Entering high altitude from below 3,000 m, avoid increasing sleeping
  altitude by more than 1,000 m in a single move; once already sleeping
  at or above 3,000 m, keep single moves to 500 m or less.
- After a cumulative gain of 1,000 m above 3,000 m, plan a rest stop of at
  least 2 nights before ascending further.
- A single move landing at or above 3,500 m after a gain of more than
  1,000 m is flagged as high risk.

> These are planning heuristics, not medical advice. Consult a clinician
> about altitude medication and personal risk factors before travelling
> to high altitude.

## Install

```bash
pip install .
```

Requires Python 3.10+. No dependencies.

## Usage

Each stop is `name:altitude_m:nights`, comma separated, in travel order:

```bash
acclimatize "Lima:0:2,Sacred Valley:2800:2,Machu Picchu:2430:1,Cusco:3400:2,Uyuni:3656:2"
# OK: no rapid-ascent warnings for this itinerary.

acclimatize "Lima:0:2,Uyuni:3656:1"
# Acclimatisation warnings:
# - [high] Lima -> Uyuni (+3656 m): Sleeping altitude rises by more than 500 m ...
```

The command exits with status 1 when warnings are found, so it can be
used in scripts.

## Library use

```python
from acclimatize import Stop, assess_itinerary

report = assess_itinerary([
    Stop("Lima", 0, nights=2),
    Stop("Cusco", 3400, nights=2),
])
print(report.format())
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## License

MIT

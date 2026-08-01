'''Parsing/loading logic for the "Name, Description" medication spreadsheet
format (see pharmacy/management/commands/load_medications.py). Kept separate
from the management command so it can be unit tested without touching a
real file.

Expected columns (header row optional):
    Name        - "Drug Name (Active Ingredient)", e.g.
                  "Albadry Plus (Novibiocin Sodium and Penicillin G Procaine)"
    Description - free text directions, expected to contain "MILK=..." and/or
                  "MEAT=..." withdrawal periods somewhere in the text, e.g.
                  "...Infuse 1 tube... MEAT=30D, MILK=72H post-calving..."
'''

import re

from .models import Medication

NAME_PATTERN = re.compile(r'^(?P<name>.+?)\s*\((?P<ingredient>[^)]+)\)\s*$')
MILK_PATTERN = re.compile(r'MILK\s*=\s*(\d+\s*[A-Za-z]+)', re.IGNORECASE)
MEAT_PATTERN = re.compile(r'MEAT(?:/SLAUGHTER)?\s*=\s*(\d+\s*[A-Za-z]+)', re.IGNORECASE)

_HOURS_PER_UNIT = {
    'h': 1, 'hr': 1, 'hrs': 1, 'hour': 1, 'hours': 1,
    'd': 24, 'day': 24, 'days': 24,
}


def _to_hours(value_text):
    '''"30D" -> 720, "60 HRS" -> 60, unrecognized units -> None.'''
    match = re.match(r'(\d+)\s*([A-Za-z]+)', value_text)
    if not match:
        return None
    number, unit = match.groups()
    hours_per_unit = _HOURS_PER_UNIT.get(unit.lower())
    return int(number) * hours_per_unit if hours_per_unit else None


def _longest(matches):
    '''Some descriptions list more than one withdrawal period -- one per
    indication (e.g. dry-cow therapy vs. lactating-cow mastitis in the same
    row). Pick the longest/most conservative one rather than silently
    dropping the rest; this is only a "preload" convenience, so anything
    with multiple distinct periods is worth a manual spot-check afterward.'''
    if not matches:
        return ""
    return max(matches, key=lambda m: _to_hours(m) or 0).strip()


def parse_name(raw_name):
    '''Split "Drug Name (Active Ingredient)" into (drug_name, active_ingredient).
    Falls back to using the whole string as drug_name if there's no
    trailing parenthetical.'''
    raw_name = (raw_name or "").strip()
    match = NAME_PATTERN.match(raw_name)
    if match:
        return match.group("name").strip(), match.group("ingredient").strip()
    return raw_name, ""


def parse_withhold_periods(description):
    '''Pull MILK=/MEAT= withdrawal periods out of a free-text description.
    If more than one appears (different indications in one cell), keep the
    longest/most conservative one -- see _longest().'''
    description = description or ""
    milk = _longest(MILK_PATTERN.findall(description))
    meat = _longest(MEAT_PATTERN.findall(description))
    return milk, meat


def iter_medication_rows(worksheet):
    '''Yield (name, description) for each non-empty row, skipping a header
    row if the first cell is literally "Name".'''
    rows = worksheet.iter_rows(values_only=True)
    first_row = next(rows, None)
    if first_row is None:
        return
    is_header = first_row and first_row[0] and str(first_row[0]).strip().lower() == "name"
    if not is_header and first_row[0]:
        yield first_row[0], (first_row[1] if len(first_row) > 1 else "")
    for row in rows:
        if not row or not row[0]:
            continue
        yield row[0], (row[1] if len(row) > 1 else "")


def load_medications_from_workbook(workbook, sheet_name=None, dry_run=False):
    '''Load/update Medication records from an openpyxl Workbook.
    Returns {"created": int, "updated": int, "skipped": [raw names]}.'''
    sheet = workbook[sheet_name] if sheet_name else workbook.active
    created = 0
    updated = 0
    skipped = []

    for raw_name, raw_description in iter_medication_rows(sheet):
        drug_name, active_ingredient = parse_name(raw_name)
        if not drug_name:
            skipped.append(raw_name)
            continue

        milk, meat = parse_withhold_periods(raw_description)
        defaults = {
            "active_ingredient": active_ingredient,
            "directions": (raw_description or "").strip(),
            "milk_withhold_period": milk,
            "meat_withhold_period": meat,
        }

        if dry_run:
            if Medication.objects.filter(drug_name=drug_name).exists():
                updated += 1
            else:
                created += 1
            continue

        _, was_created = Medication.objects.update_or_create(
            drug_name=drug_name, defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {"created": created, "updated": updated, "skipped": skipped}

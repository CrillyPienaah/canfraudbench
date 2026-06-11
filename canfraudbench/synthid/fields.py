"""
Field-level generators for synthetic Canadian onboarding records.

SAFETY INVARIANT: nothing here produces a real, assignable identifier for a
real person. In particular:

  * Social Insurance Numbers are NOT real. Legitimate/most records use numbers
    that deliberately FAIL the Luhn checksum (so they can never collide with a
    valid issued SIN). Only the BLENDED typology, which specifically needs a
    structurally-plausible identifier to exercise a checksum-aware detector,
    emits a Luhn-passing 9-digit number -- but it is still drawn at random from
    the full space and is overwhelmingly unassigned; we additionally avoid the
    900-series (temporary) and 000-prefixes. These are test fixtures, not PII.
  * Names are sampled from generic token lists, not real registries.
  * Addresses use real Canadian *province/city* labels but fictitious civic
    numbers and the documentation postal-code forms.

This module is intentionally dependency-light (stdlib only) so the benchmark
is trivially reproducible.
"""

import random
import string
from datetime import date, timedelta

PROVINCES = ["ON", "BC", "AB", "QC", "MB", "SK", "NS", "NB", "NL", "PE"]
PROVINCE_CITIES = {
    "ON": ["Toronto", "Ottawa", "Mississauga", "Pickering", "Hamilton"],
    "BC": ["Vancouver", "Victoria", "Surrey", "Burnaby"],
    "AB": ["Calgary", "Edmonton", "Red Deer"],
    "QC": ["Montreal", "Quebec City", "Laval", "Gatineau"],
    "MB": ["Winnipeg", "Brandon"],
    "SK": ["Saskatoon", "Regina"],
    "NS": ["Halifax", "Dartmouth"],
    "NB": ["Fredericton", "Moncton", "Saint John"],
    "NL": ["St. John's"],
    "PE": ["Charlottetown"],
}
_FIRST = ["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Riley", "Casey",
          "Jamie", "Avery", "Quinn", "Kwame", "Amara", "Felix", "Nadia",
          "Omar", "Priya", "Sofia", "Liam", "Noah", "Aria"]
_LAST = ["Smith", "Brown", "Tremblay", "Nguyen", "Patel", "Singh", "Wong",
         "Martin", "Roy", "Gagnon", "Okafor", "Mensah", "Lopez", "Khan",
         "Macdonald", "Lavoie", "Cote", "Pelletier", "Ahmed", "Ali"]


def _luhn_checksum(digits):
    total, alt = 0, False
    for d in reversed(digits):
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10


def make_sin(rng, *, luhn_valid):
    """Return a 9-digit string. luhn_valid=False guarantees an INVALID SIN."""
    while True:
        first = rng.randint(1, 8)  # avoid 0-prefix and 9-series (temporary)
        body = [first] + [rng.randint(0, 9) for _ in range(8)]
        valid = _luhn_checksum(body) == 0
        if valid == luhn_valid:
            return "".join(str(d) for d in body)


def make_name(rng):
    return rng.choice(_FIRST), rng.choice(_LAST)


def make_dob(rng, min_age=18, max_age=85):
    age = rng.randint(min_age, max_age)
    days = rng.randint(0, 364)
    return date.today() - timedelta(days=age * 365 + days)


def make_postal(rng):
    # Documentation-style format A1A 1A1 (not validated against real FSAs).
    L = string.ascii_uppercase
    return f"{rng.choice(L)}{rng.randint(0,9)}{rng.choice(L)} " \
           f"{rng.randint(0,9)}{rng.choice(L)}{rng.randint(0,9)}"


def make_address(rng):
    prov = rng.choice(PROVINCES)
    city = rng.choice(PROVINCE_CITIES[prov])
    return {
        "civic": rng.randint(1, 9999),
        "city": city,
        "province": prov,
        "postal": make_postal(rng),
    }


def make_device_id(rng):
    return "dev_" + "".join(rng.choices(string.hexdigits.lower(), k=12))

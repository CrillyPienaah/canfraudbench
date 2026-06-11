"""
Canadian synthetic-identity fraud typologies.

These are the documented patterns that the Track-A generator instantiates.
The point of grounding generation in named typologies (rather than arbitrary
noise) is twofold:

  1. A validator can trace every positive label back to a recognizable
     real-world fraud pattern -- this is what makes the benchmark *credible*
     to a bank fraud team rather than a toy.
  2. It lets us report performance *per typology*, which is far more useful
     than a single aggregate AUC: a model that catches fabricated identities
     but misses synthetic-identity "credit washing" has a specific, nameable
     blind spot.

Typology definitions are drawn from public descriptions of synthetic-identity
fraud (e.g. how blended/"Frankenstein" identities combine a real SIN with a
fabricated name and DOB; how nominee/"piggyback" tradelines are used to age a
thin file). No proprietary or confidential typology is encoded here.

NOTE ON SIN VALUES: This module never generates a real, assignable Social
Insurance Number. All identity numbers are drawn from documentation/test
ranges and/or fail the Luhn check by construction unless a typology
specifically requires a *structurally valid* (but still fictitious) number to
exercise a detector. See synthid/fields.py.
"""

from dataclasses import dataclass
from enum import Enum


class Typology(str, Enum):
    LEGITIMATE = "legitimate"
    # A wholly invented identity: no underlying real person.
    FABRICATED = "fabricated"
    # Real-but-mismatched components stitched together
    # (classic "Frankenstein"/blended synthetic identity).
    BLENDED = "blended"
    # A thin/young file artificially aged via nominee or piggyback tradelines
    # to appear established ("credit washing"/file-aging).
    FILE_AGED = "file_aged"
    # Many applications sharing subtle linked attributes
    # (same device, address cluster, or contact reuse) -- mule/farm signal.
    LINKED_CLUSTER = "linked_cluster"
    # Identity components internally inconsistent in ways a rules engine
    # would miss but a model should catch (e.g. issue-date/age contradictions).
    INCONSISTENT = "inconsistent"


@dataclass(frozen=True)
class TypologySpec:
    typology: Typology
    label: int  # 1 = fraud, 0 = legitimate
    description: str
    # Approximate share among the *fraud* class (sums to ~1 over fraud types).
    fraud_mix_weight: float


SPECS = {
    Typology.LEGITIMATE: TypologySpec(
        Typology.LEGITIMATE, 0,
        "Internally consistent, plausibly-distributed legitimate applicant.",
        0.0,
    ),
    Typology.FABRICATED: TypologySpec(
        Typology.FABRICATED, 1,
        "Wholly invented identity; no real underlying person. Often clean but "
        "statistically atypical correlations between fields.",
        0.30,
    ),
    Typology.BLENDED: TypologySpec(
        Typology.BLENDED, 1,
        "Blended/Frankenstein: real structural identifier paired with "
        "fabricated name/DOB; mismatch between components.",
        0.30,
    ),
    Typology.FILE_AGED: TypologySpec(
        Typology.FILE_AGED, 1,
        "Thin file artificially aged (nominee/piggyback tradelines); "
        "credit history inconsistent with declared age/tenure.",
        0.20,
    ),
    Typology.LINKED_CLUSTER: TypologySpec(
        Typology.LINKED_CLUSTER, 1,
        "Member of an application cluster sharing latent attributes "
        "(device/address/contact reuse) indicative of a farm/mule network.",
        0.15,
    ),
    Typology.INCONSISTENT: TypologySpec(
        Typology.INCONSISTENT, 1,
        "Internally contradictory fields (e.g. document issue date precedes "
        "DOB-implied eligibility) that univariate rules tend to miss.",
        0.05,
    ),
}

FRAUD_TYPOLOGIES = [t for t, s in SPECS.items() if s.label == 1]
FRAUD_MIX = {t: SPECS[t].fraud_mix_weight for t in FRAUD_TYPOLOGIES}

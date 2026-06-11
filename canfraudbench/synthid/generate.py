"""
Track-A generator: produces a labelled synthetic-identity onboarding dataset.

Each record is a Canadian onboarding application with engineered signal that
reflects its typology (see typologies.py). The generator emits BOTH:

  * raw-ish fields (for anyone who wants to build their own features), and
  * a compact numeric feature vector + label + typology tag (what baselines
    and the leaderboard consume).

Design choices that matter for a governance benchmark:

  * Reproducible: a fixed seed yields a byte-identical dataset.
  * Per-typology labels are preserved so metrics can be sliced by fraud type.
  * A synthetic "protected attribute" (region grouping) is included so that
    fairness metrics are *computable* -- this is REQUIRED to demonstrate the
    E-23 fairness dimension. It is synthetic and carries no real demographic
    data about any real person.
"""

import argparse
import json
import os
import random

from .typologies import Typology, FRAUD_TYPOLOGIES, FRAUD_MIX, SPECS
from . import fields as F


def _base_record(rng):
    first, last = F.make_name(rng)
    dob = F.make_dob(rng)
    addr = F.make_address(rng)
    return {
        "first_name": first,
        "last_name": last,
        "dob": dob.isoformat(),
        "address": addr,
        "device_id": F.make_device_id(rng),
        "declared_credit_tenure_months": rng.randint(6, 360),
        "thin_file": 0,
    }


def _apply_typology(rec, typ, rng, cluster_pool):
    """Mutate a base record to express a typology; return feature signals."""
    age_years = (
        __import__("datetime").date.today().year - int(rec["dob"][:4])
    )
    sig = {
        "sin_luhn_valid": 0,
        "name_struct_anomaly": 0.0,
        "dob_doc_inconsistency": 0.0,
        "tenure_vs_age_gap": 0.0,
        "cluster_link_score": 0.0,
        "field_entropy": rng.uniform(0.4, 0.6),
    }

    if typ == Typology.LEGITIMATE:
        rec["sin"] = F.make_sin(rng, luhn_valid=False)
        # legitimate tenure broadly consistent with age
        plausible = max(0, (age_years - 18)) * 12
        rec["declared_credit_tenure_months"] = min(
            rec["declared_credit_tenure_months"],
            max(6, plausible),
        )
        sig["tenure_vs_age_gap"] = max(
            0.0, rec["declared_credit_tenure_months"] - plausible
        ) / 360.0

    elif typ == Typology.FABRICATED:
        rec["sin"] = F.make_sin(rng, luhn_valid=False)
        sig["field_entropy"] = rng.uniform(0.7, 0.95)  # atypical correlations
        sig["name_struct_anomaly"] = rng.uniform(0.3, 0.8)

    elif typ == Typology.BLENDED:
        # structurally-plausible (Luhn-valid) but fictitious identifier
        rec["sin"] = F.make_sin(rng, luhn_valid=True)
        sig["sin_luhn_valid"] = 1
        sig["name_struct_anomaly"] = rng.uniform(0.5, 1.0)  # mismatch
        sig["dob_doc_inconsistency"] = rng.uniform(0.2, 0.7)

    elif typ == Typology.FILE_AGED:
        rec["sin"] = F.make_sin(rng, luhn_valid=False)
        rec["thin_file"] = 1
        implied_max = max(0, (age_years - 18)) * 12
        # claim more tenure than age plausibly allows
        rec["declared_credit_tenure_months"] = implied_max + rng.randint(60, 180)
        sig["tenure_vs_age_gap"] = (
            rec["declared_credit_tenure_months"] - implied_max
        ) / 360.0

    elif typ == Typology.LINKED_CLUSTER:
        rec["sin"] = F.make_sin(rng, luhn_valid=False)
        # share a device/address fragment with the cluster pool
        if cluster_pool:
            anchor = rng.choice(cluster_pool)
            rec["device_id"] = anchor["device_id"]
            rec["address"]["postal"] = anchor["address"]["postal"]
        sig["cluster_link_score"] = rng.uniform(0.6, 1.0)

    elif typ == Typology.INCONSISTENT:
        rec["sin"] = F.make_sin(rng, luhn_valid=False)
        sig["dob_doc_inconsistency"] = rng.uniform(0.6, 1.0)

    return sig


def _feature_vector(rec, sig):
    return {
        "f_sin_luhn_valid": sig["sin_luhn_valid"],
        "f_name_struct_anomaly": round(sig["name_struct_anomaly"], 4),
        "f_dob_doc_inconsistency": round(sig["dob_doc_inconsistency"], 4),
        "f_tenure_vs_age_gap": round(sig["tenure_vs_age_gap"], 4),
        "f_cluster_link_score": round(sig["cluster_link_score"], 4),
        "f_field_entropy": round(sig["field_entropy"], 4),
        "f_thin_file": rec["thin_file"],
        "f_province_group": 0,  # filled below
    }


def generate(n, seed, fraud_rate=0.20):
    rng = random.Random(seed)
    records, cluster_pool = [], []
    n_fraud = int(n * fraud_rate)
    n_legit = n - n_fraud

    # build fraud-type counts from the documented mix
    fraud_counts = {t: int(n_fraud * FRAUD_MIX[t]) for t in FRAUD_TYPOLOGIES}
    # fix rounding
    while sum(fraud_counts.values()) < n_fraud:
        fraud_counts[FRAUD_TYPOLOGIES[0]] += 1

    plan = [Typology.LEGITIMATE] * n_legit
    for t, c in fraud_counts.items():
        plan += [t] * c
    rng.shuffle(plan)

    for typ in plan:
        rec = _base_record(rng)
        sig = _apply_typology(rec, typ, rng, cluster_pool)
        if typ == Typology.LINKED_CLUSTER and len(cluster_pool) < 50:
            cluster_pool.append(rec)
        feats = _feature_vector(rec, sig)
        # synthetic protected attribute (region grouping) for fairness metrics
        prov = rec["address"]["province"]
        group = 0 if prov in ("ON", "QC", "BC", "AB") else 1
        feats["f_province_group"] = group
        records.append({
            "id": f"can_{len(records):07d}",
            "raw": rec,
            "features": feats,
            "protected_group": group,
            "typology": typ.value,
            "label": SPECS[typ].label,
        })
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=23)
    ap.add_argument("--fraud_rate", type=float, default=0.20)
    ap.add_argument("--out", default="data/synthid/")
    args = ap.parse_args()

    recs = generate(args.n, args.seed, args.fraud_rate)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"canfraudbench_synthid_n{args.n}_seed{args.seed}.jsonl")
    with open(path, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    n_fraud = sum(r["label"] for r in recs)
    print(f"wrote {len(recs)} records ({n_fraud} fraud, "
          f"{len(recs)-n_fraud} legit) -> {path}")


if __name__ == "__main__":
    main()

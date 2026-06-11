"""
Track-B evaluation harness.

Consumes a stream of samples from any DocumentAdapter plus a scoring function
score_fn(sample) -> probability_of_forgery, and produces the SAME E-23 evidence
pack structure as Track A -- with metrics sliced by attack_type and doc_type so
a model's blind spots are visible.

The harness is image-agnostic: it does not load pixels itself. Your score_fn
receives the sample dict (including image_path) and is responsible for whatever
model inference it needs. This keeps the benchmark a protocol and lets people
plug in any vision model without CanFraudBench taking an image dependency.

For fairness in Track B, the 'protected group' analogue is `region` (a proxy
slice). Document-fraud fairness is more nuanced than tabular onboarding, so we
report region-sliced selection/TPR but flag in the pack that this is a proxy,
not a protected-attribute guarantee.
"""

import argparse
import importlib
import json
import os
from collections import defaultdict

from canfraudbench.documents.adapters import load_samples
from canfraudbench.metrics import core as M
from canfraudbench.governance import e23_mapping as G


def evaluate(samples, score_fn, alert_rate=0.20, reference_scores=None):
    samples = list(samples)
    if not samples:
        raise ValueError("No samples produced by adapter.")

    y = [s["label"] for s in samples]
    proba = [float(score_fn(s)) for s in samples]
    regions = [s["region"] for s in samples]
    attacks = [s["attack_type"] for s in samples]
    docs = [s["doc_type"] for s in samples]

    cutoff = sorted(proba, reverse=True)[max(0, int(len(proba) * alert_rate) - 1)]
    pred = [1 if p >= cutoff else 0 for p in proba]

    metrics = {
        "auc": M.roc_auc(y, proba),
        "ks": M.ks_statistic(y, proba),
        "brier": M.brier_score(y, proba),
        "ece": M.expected_calibration_error(y, proba),
        "psi": M.population_stability_index(reference_scores or proba, proba),
        "explanation_coverage": 0.0,  # set by your model if it emits explanations
    }
    fair = M.fairness_report(y, pred, regions)
    metrics.update({k: fair[k] for k in
                    ("adverse_impact_ratio", "equal_opportunity_gap",
                     "demographic_parity_gap")})

    # recall sliced by attack type (only over positive samples of that type)
    def recall_slice(keys):
        out = {}
        for kv in set(keys):
            idx = [i for i, k in enumerate(keys) if k == kv]
            pos = [i for i in idx if y[i] == 1]
            if not pos:
                continue
            tp = sum(1 for i in pos if pred[i] == 1)
            out[kv] = round(tp / len(pos), 4)
        return out

    metrics["recall_by_attack_type"] = recall_slice(attacks)
    metrics["recall_by_doc_type"] = recall_slice(docs)

    pack = G.build_evidence_pack(
        submission_meta={
            "track": "B_document_presentation_attack",
            "n_samples": len(samples),
            "source_datasets": sorted({s["source_dataset"] for s in samples}),
            "alert_rate": alert_rate,
        },
        metrics=metrics,
    )
    pack["notes"] = {
        "fairness_proxy": "Track-B fairness uses `region` as a proxy slice; it "
                          "is NOT a protected-attribute guarantee. Interpret as "
                          "a coverage check across source populations.",
        "explanation_coverage": "Defaults to 0.0 unless your score_fn reports "
                                 "per-decision explanations; set accordingly.",
    }
    return pack


def _load_score_fn(spec):
    """spec = 'module:function'. The function takes a sample dict, returns float."""
    mod, fn = spec.split(":")
    return getattr(importlib.import_module(mod), fn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True,
                    choices=["manifest", "sidtd", "midv2020"])
    ap.add_argument("--root", required=True, help="local dataset root")
    ap.add_argument("--manifest", default=None, help="manifest path (manifest adapter)")
    ap.add_argument("--score_fn", required=True,
                    help="'module:function' returning P(forgery) for a sample")
    ap.add_argument("--alert_rate", type=float, default=0.20)
    ap.add_argument("--report", default="out/evidence_pack_trackB.json")
    args = ap.parse_args()

    kw = {"manifest": args.manifest} if args.adapter == "manifest" and args.manifest else {}
    samples = load_samples(args.adapter, args.root, **kw)
    score_fn = _load_score_fn(args.score_fn)

    pack = evaluate(samples, score_fn, alert_rate=args.alert_rate)
    os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
    with open(args.report, "w") as fh:
        json.dump(pack, fh, indent=2)
    m = pack["metrics"]
    print(f"AUC={m['auc']:.3f} ECE={m['ece']:.3f} PSI={m['psi']:.3f} "
          f"AIR={m['adverse_impact_ratio']:.3f} overall={pack['overall_status']}")
    print("recall by attack:", json.dumps(m["recall_by_attack_type"]))
    print(f"evidence pack -> {args.report}")


if __name__ == "__main__":
    main()

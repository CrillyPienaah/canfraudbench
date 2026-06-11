"""
Correctness tests for CanFraudBench metrics. Run: python tests/test_metrics.py

These check the metric implementations against cases with known answers, so a
reviewer can trust the numbers without re-deriving them.
"""

import math
from canfraudbench.metrics import core as M
from canfraudbench.governance import e23_mapping as G


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def test_auc_perfect_and_random():
    # perfectly separable -> AUC 1.0
    assert approx(M.roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 1.0)
    # reversed -> AUC 0.0
    assert approx(M.roc_auc([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]), 0.0)
    # tie everywhere -> 0.5
    assert approx(M.roc_auc([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5]), 0.5)


def test_brier_bounds():
    assert approx(M.brier_score([1, 0], [1.0, 0.0]), 0.0)
    assert approx(M.brier_score([1, 0], [0.0, 1.0]), 1.0)


def test_psi_zero_for_identical():
    d = [i / 100 for i in range(100)]
    assert M.population_stability_index(d, d) < 1e-6


def test_psi_positive_for_shift():
    ref = [0.1] * 100
    act = [0.9] * 100
    assert M.population_stability_index(ref, act) > 0.25


def test_fairness_air():
    # group 0 flagged 50%, group 1 flagged 100% -> AIR = 0.5
    yt = [1, 1, 1, 1]
    yp = [1, 0, 1, 1]
    g = [0, 0, 1, 1]
    rep = M.fairness_report(yt, yp, g)
    assert approx(rep["adverse_impact_ratio"], 0.5)
    assert rep["passes_four_fifths"] is False


def test_e23_overall_fail_on_fairness():
    metrics = {"auc": 0.99, "ks": 0.9, "brier": 0.02, "ece": 0.01,
               "psi": 0.01, "adverse_impact_ratio": 0.59,
               "equal_opportunity_gap": 0.4, "explanation_coverage": 1.0}
    pack = G.build_evidence_pack({"model": "t"}, metrics)
    assert pack["overall_status"] == "FAIL"
    assert pack["e23_assessment"]["fairness"]["status"] == "FAIL"
    assert pack["e23_assessment"]["discrimination"]["status"] == "PASS"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS  {fn.__name__}")
    print(f"\nAll {len(fns)} tests passed.")

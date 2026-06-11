"""
CanFraudBench metrics: the full evidence set an E-23 validator needs.

Deliberately stdlib-only (no sklearn/numpy required) so that running the
benchmark is frictionless and the numbers are auditable line-by-line. If you
have numpy/sklearn installed you are free to swap these out; results match.

Four families, mapped to E-23 dimensions:

  Discrimination  -> conceptual soundness / outcomes analysis  (AUC, KS)
  Calibration     -> conceptual soundness                      (ECE, Brier)
  Stability       -> ongoing monitoring / drift                (PSI)
  Fairness        -> bias & fairness                           (AIR, EO gap,
                                                                demographic
                                                                parity gap)
"""

import math
from collections import defaultdict


# ----------------------------- discrimination -----------------------------

def roc_auc(y_true, y_score):
    """Rank-based AUC (Mann-Whitney). O(n log n)."""
    paired = sorted(zip(y_score, y_true), key=lambda t: t[0])
    # assign ranks with tie-averaging
    ranks = [0.0] * len(paired)
    i = 0
    while i < len(paired):
        j = i
        while j + 1 < len(paired) and paired[j + 1][0] == paired[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    n_pos = sum(1 for _, y in paired if y == 1)
    n_neg = len(paired) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    sum_ranks_pos = sum(r for r, (_, y) in zip(ranks, paired) if y == 1)
    return (sum_ranks_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def ks_statistic(y_true, y_score, bins=100):
    pos = sorted(s for s, y in zip(y_score, y_true) if y == 1)
    neg = sorted(s for s, y in zip(y_score, y_true) if y == 0)
    if not pos or not neg:
        return float("nan")
    grid = [i / bins for i in range(bins + 1)]
    def cdf(arr, t):
        return sum(1 for v in arr if v <= t) / len(arr)
    return max(abs(cdf(neg, t) - cdf(pos, t)) for t in grid)


# ------------------------------- calibration -------------------------------

def brier_score(y_true, y_prob):
    return sum((p - y) ** 2 for p, y in zip(y_prob, y_true)) / len(y_true)


def expected_calibration_error(y_true, y_prob, bins=10):
    buckets = defaultdict(list)
    for y, p in zip(y_true, y_prob):
        b = min(bins - 1, int(p * bins))
        buckets[b].append((y, p))
    n = len(y_true)
    ece = 0.0
    for b, items in buckets.items():
        conf = sum(p for _, p in items) / len(items)
        acc = sum(y for y, _ in items) / len(items)
        ece += (len(items) / n) * abs(acc - conf)
    return ece


# ----------------------- stability / drift (PSI) ---------------------------

def population_stability_index(expected, actual, bins=10):
    """PSI between an expected (reference) and actual score distribution.

    PSI < 0.10  : no significant shift
    0.10 - 0.25 : moderate shift (investigate)
    > 0.25      : major shift (model likely needs revalidation)
    """
    lo, hi = 0.0, 1.0
    edges = [lo + (hi - lo) * i / bins for i in range(bins + 1)]
    def dist(arr):
        counts = [0] * bins
        for v in arr:
            b = min(bins - 1, max(0, int((v - lo) / (hi - lo) * bins)))
            counts[b] += 1
        total = len(arr)
        return [(c / total) if total else 0.0 for c in counts]
    e, a = dist(expected), dist(actual)
    psi = 0.0
    for ei, ai in zip(e, a):
        ei = max(ei, 1e-6)
        ai = max(ai, 1e-6)
        psi += (ai - ei) * math.log(ai / ei)
    return psi


# --------------------------------- fairness --------------------------------

def _confusion(y_true, y_pred):
    tp = fp = tn = fn = 0
    for y, p in zip(y_true, y_pred):
        if p == 1 and y == 1: tp += 1
        elif p == 1 and y == 0: fp += 1
        elif p == 0 and y == 0: tn += 1
        else: fn += 1
    return tp, fp, tn, fn


def fairness_report(y_true, y_pred, groups):
    """Group-wise selection (flag) rates and true-positive rates, plus the
    Adverse Impact Ratio and equal-opportunity / demographic-parity gaps.

    'Selection' here = being flagged as fraud (the adverse action)."""
    by_group = defaultdict(lambda: {"yt": [], "yp": []})
    for y, p, g in zip(y_true, y_pred, groups):
        by_group[g]["yt"].append(y)
        by_group[g]["yp"].append(p)

    per = {}
    for g, d in by_group.items():
        tp, fp, tn, fn = _confusion(d["yt"], d["yp"])
        sel_rate = (tp + fp) / max(1, len(d["yp"]))   # flagged share
        tpr = tp / max(1, (tp + fn))                  # recall on fraud
        per[g] = {"selection_rate": sel_rate, "tpr": tpr, "n": len(d["yp"])}

    sel_rates = [v["selection_rate"] for v in per.values()]
    tprs = [v["tpr"] for v in per.values()]
    air = (min(sel_rates) / max(sel_rates)) if max(sel_rates) > 0 else float("nan")
    return {
        "per_group": per,
        "adverse_impact_ratio": air,          # 0.8 (four-fifths) is the floor
        "passes_four_fifths": air >= 0.8 if air == air else False,
        "demographic_parity_gap": max(sel_rates) - min(sel_rates),
        "equal_opportunity_gap": max(tprs) - min(tprs),
    }

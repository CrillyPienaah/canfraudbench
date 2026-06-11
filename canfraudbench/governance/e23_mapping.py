"""
OSFI Guideline E-23 mapping.

This is what distinguishes CanFraudBench from a pure-ML leaderboard: every
metric is attached to the model-risk expectation it provides evidence for, so
a submission output doubles as a *validation evidence pack* a Canadian
model-risk function could drop into a model file.

The mapping reflects the structure of OSFI's final E-23 (Model Risk
Management), published 11 Sep 2025, effective 1 May 2027, which applies across
the model lifecycle: design/conceptual soundness, review/independent
validation, deployment, and ongoing monitoring -- and explicitly extends to
AI/ML models. The descriptions here are a practitioner's plain-language
restatement, NOT quotations of the guideline. Always validate wording and
applicability against the official text and your own model-risk policy; this
tool is decision-support, not regulatory advice.

Each dimension carries a 'status' computed from thresholds that the submitter
can override to match their institution's risk appetite.
"""

E23_DIMENSIONS = {
    "discrimination": {
        "lifecycle_stage": "Design / conceptual soundness; ongoing outcomes analysis",
        "expectation": "The model meaningfully separates fraud from non-fraud "
                       "and that separation is demonstrated, not assumed.",
        "evidence_metrics": ["auc", "ks"],
    },
    "calibration": {
        "lifecycle_stage": "Conceptual soundness",
        "expectation": "Predicted fraud probabilities correspond to observed "
                       "frequencies, so scores can support consistent decisioning.",
        "evidence_metrics": ["brier", "ece"],
    },
    "stability": {
        "lifecycle_stage": "Ongoing monitoring",
        "expectation": "Input/score distributions are monitored for drift, with "
                       "thresholds that trigger investigation or revalidation.",
        "evidence_metrics": ["psi"],
    },
    "fairness": {
        "lifecycle_stage": "Conceptual soundness; ongoing monitoring",
        "expectation": "Adverse outcomes (fraud flags) do not fall "
                       "disproportionately on protected groups without justification.",
        "evidence_metrics": ["adverse_impact_ratio", "equal_opportunity_gap",
                              "demographic_parity_gap"],
    },
    "explainability": {
        "lifecycle_stage": "Conceptual soundness; deployment",
        "expectation": "Individual decisions can be explained in terms a "
                       "validator and an adversely-affected customer could follow.",
        "evidence_metrics": ["explanation_coverage"],
    },
    "stability_of_concept_under_adversary": {
        "lifecycle_stage": "Ongoing monitoring (fraud-specific)",
        "expectation": "Because fraud is adversarial and non-stationary, "
                       "performance degradation between reference and recent "
                       "data is surfaced explicitly.",
        "evidence_metrics": ["psi", "auc_delta_vs_reference"],
    },
}

DEFAULT_THRESHOLDS = {
    "auc_min": 0.75,
    "ks_min": 0.30,
    "ece_max": 0.10,
    "psi_warn": 0.10,
    "psi_fail": 0.25,
    "air_min": 0.80,            # four-fifths rule
    "eo_gap_max": 0.10,
    "explanation_coverage_min": 0.95,
}


def _status(ok, warn=False):
    return "PASS" if ok else ("WARN" if warn else "FAIL")


def assess(metrics, thresholds=None):
    """Turn a flat metrics dict into per-dimension E-23 statuses.

    `metrics` may contain: auc, ks, brier, ece, psi, auc_delta_vs_reference,
    adverse_impact_ratio, equal_opportunity_gap, demographic_parity_gap,
    explanation_coverage.
    """
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    out = {}

    auc = metrics.get("auc")
    ks = metrics.get("ks")
    out["discrimination"] = {
        "status": _status(auc is not None and auc >= t["auc_min"]
                          and (ks is None or ks >= t["ks_min"])),
        "values": {"auc": auc, "ks": ks},
    }

    ece = metrics.get("ece")
    out["calibration"] = {
        "status": _status(ece is not None and ece <= t["ece_max"]),
        "values": {"brier": metrics.get("brier"), "ece": ece},
    }

    psi = metrics.get("psi")
    out["stability"] = {
        "status": ("PASS" if (psi is not None and psi < t["psi_warn"])
                   else "WARN" if (psi is not None and psi < t["psi_fail"])
                   else "FAIL"),
        "values": {"psi": psi},
    }

    air = metrics.get("adverse_impact_ratio")
    eo = metrics.get("equal_opportunity_gap")
    out["fairness"] = {
        "status": _status(
            air is not None and air >= t["air_min"]
            and (eo is None or eo <= t["eo_gap_max"]),
            warn=(air is not None and 0.7 <= air < t["air_min"]),
        ),
        "values": {
            "adverse_impact_ratio": air,
            "equal_opportunity_gap": eo,
            "demographic_parity_gap": metrics.get("demographic_parity_gap"),
        },
    }

    cov = metrics.get("explanation_coverage")
    out["explainability"] = {
        "status": _status(cov is not None and cov >= t["explanation_coverage_min"]),
        "values": {"explanation_coverage": cov},
    }

    return out


def build_evidence_pack(submission_meta, metrics, thresholds=None):
    assessment = assess(metrics, thresholds)
    overall = "PASS"
    for dim in assessment.values():
        if dim["status"] == "FAIL":
            overall = "FAIL"; break
        if dim["status"] == "WARN" and overall == "PASS":
            overall = "WARN"
    return {
        "benchmark": "CanFraudBench",
        "schema_version": "0.1",
        "submission": submission_meta,
        "metrics": metrics,
        "e23_assessment": assessment,
        "e23_dimensions_reference": E23_DIMENSIONS,
        "thresholds": {**DEFAULT_THRESHOLDS, **(thresholds or {})},
        "overall_status": overall,
        "disclaimer": "Decision-support only; not regulatory advice. Validate "
                      "against the official OSFI E-23 text and institutional policy.",
    }

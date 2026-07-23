# CanFraudBench — Canadian Identity-Fraud Benchmark with OSFI E-23 Governance Mapping

> **Core finding:** The reference baseline scores **AUC 0.969** and is classified **🚫 BLOCKED**
> under OSFI E-23 governance criteria — its Adverse Impact Ratio (0.59) breaches the
> four-fifths fairness rule. Discrimination without governance is not a passing model.

A public, reproducible benchmark for synthetic-identity fraud detection in a Canadian
financial-onboarding context — where every metric maps to OSFI Guideline E-23 model-risk expectations.

[![Dataset](https://img.shields.io/badge/HuggingFace-Dataset-yellow)](https://huggingface.co/datasets/CrillyPienaah/CanFraudBench)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: Apache 2.0](https://img.shields.io/badge/Code-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## Reference Baseline Evidence Pack

| E-23 Dimension | Metric | Score | Status |
|----------------|--------|-------|--------|
| Discrimination | AUC | 0.969 | ✅ PASS |
| Calibration | Brier Score | 0.048 | ✅ PASS |
| Fairness | AIR (four-fifths rule) | 0.59 | ❌ FAIL |
| Stability | PSI (holdout) | 0.031 | ✅ PASS |
| Explainability | Top-3 SHAP features documented | Yes | ✅ PASS |
| **Overall E-23 Status** | | | **🚫 BLOCKED** |

Rankings sort by E-23 status first, then mean per-typology recall, then AUC.
A high-AUC model that fails a governance dimension does not outrank a governable one.

---

## Quick Start

```bash
git clone https://github.com/CrillyPienaah/canfraudbench
cd canfraudbench
pip install -r requirements.txt
```

**Load the dataset:**
```python
import json, urllib.request

URL = "https://huggingface.co/datasets/CrillyPienaah/CanFraudBench/resolve/main/canfraudbench_synthid_n20000_seed23.jsonl"
records = [json.loads(l) for l in urllib.request.urlopen(URL)]
X = [list(r["features"].values()) for r in records]
y = [r["label"] for r in records]
groups = [r["protected_group"] for r in records]
```

**Reproduce the dataset from scratch:**
```bash
python -m canfraudbench.synthid.generate --n 20000 --seed 23 --out data/synthid/
```

**Run the reference baseline + evidence pack:**
```bash
python -m canfraudbench.evaluate --data data/synthid/ --model baseline
```

---

## Repository Structure

```
canfraudbench/
├── canfraudbench/
│   ├── synthid/
│   │   └── generate.py        # Deterministic synthetic data generator
│   ├── metrics/
│   │   └── e23_governance.py  # AUC, AIR, PSI, Brier, SHAP -> E-23 evidence pack
│   └── evaluate.py            # End-to-end evaluation harness
├── data/
│   └── synthid/               # Generated data (gitignored, load from HF)
├── docs/
│   └── DATA_ETHICS.md         # Honest scope, privacy guarantees
├── notebooks/
│   └── reference_baseline.ipynb  # Reproduces the BLOCKED verdict
├── requirements.txt
└── README.md
```

---

## Why This Exists

OSFI Guideline E-23 (Model Risk Management) takes effect **1 May 2027** and applies to all
models at all federally regulated financial institutions, including AI/ML and third-party models.
Yet there is no public Canadian benchmark for identity-fraud detection — the strong open corpora
that exist (MIDV-2020, SIDTD, IDNet) are all US/European and none is framed against Canadian
regulatory expectations.

CanFraudBench fills that gap. Every score is paired with the E-23 evidence dimension it speaks
to (discrimination, calibration, stability/drift, fairness, explainability). A submission
produces a **validation evidence pack**, not just an AUC.

---

## Dataset — Track A (Synthetic Identity)

| Property | Value |
|----------|-------|
| Records | 20,000 |
| Legitimate | 16,000 |
| Fraud | 4,000 (20%) |
| Seed | 23 (deterministic) |
| Format | JSON Lines (.jsonl) |

**Fraud typology breakdown:**

| Typology | Count | Description |
|----------|-------|-------------|
| fabricated | 1,200 | Wholly invented identity |
| blended | 1,200 | Real structural identifier + fabricated name/DOB |
| file_aged | 800 | Thin file artificially aged |
| linked_cluster | 600 | Application cluster (device/address reuse) |
| inconsistent | 200 | Internally contradictory fields |
| legitimate | 16,000 | Internally consistent applicant |

---

## Submitting to the Leaderboard

Submit the produced evidence pack (metrics, never raw data). Rankings sort by E-23 status
first, then mean per-typology recall, then AUC. See `docs/SUBMISSION.md` for the full protocol.

---

## Privacy & Ethics

- **Fully synthetic.** No real person's data is present.
- **No real SINs.** Most records deliberately fail the Luhn checksum.
- **Honest scope.** Typology-grounded simulator, not a DP mechanism — stated plainly, not overclaimed.
- **Not affiliated with OSFI.** Decision-support only, not regulatory advice.

See `docs/DATA_ETHICS.md` for full details.

---

## Citation

```bibtex
@misc{canfraudbench2026,
  title  = {CanFraudBench: A Canadian Identity-Fraud Benchmark with OSFI E-23 Governance Mapping},
  author = {Pienaah, Christopher},
  year   = {2026},
  url    = {https://github.com/CrillyPienaah/canfraudbench}
}
```

---

**Author:** Christopher Crilly Pienaah  
**Portfolio:** [chris-pienaah-portfolio.vercel.app](https://chris-pienaah-portfolio.vercel.app)  
**LinkedIn:** [linkedin.com/in/christopher-crilly-pienaah](https://linkedin.com/in/christopher-crilly-pienaah)

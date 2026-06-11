# CanFraudBench

**A public, reproducible benchmark and evaluation protocol for identity-fraud detection in a Canadian financial-onboarding context — with every metric mapped to OSFI Guideline E-23 model-risk expectations.**

CanFraudBench is not another detection model. It is the *measuring stick*: a
standardized way to evaluate how well a synthetic-identity or document-fraud
model performs, **and** whether the evidence it produces would satisfy a Canadian
model-risk validator under OSFI Guideline E-23 (effective 1 May 2027).

It exists because there is, today, **no public Canadian benchmark** for
identity-fraud detection. The strong open corpora that do exist
(MIDV-2020, SIDTD, DLC-2021, FMIDV, IDNet) are all US- and Europe-based, and
none of them is framed against Canadian regulatory expectations.

---

## The two tracks

| Track | Question it answers | Data basis |
|---|---|---|
| **Track A — Synthetic Identity** | Can a model flag blended / fabricated ("Frankenstein") identities at onboarding? | High-fidelity **synthetic** PII generated from documented Canadian synthetic-ID typologies, with a stated differential-privacy guarantee. Fully publishable; contains no real person's data. |
| **Track B — Document & Presentation Attack** | Can a model flag forged or AI-manipulated ID documents and liveness spoofs? | A standardized harness over **existing, research-licensed public datasets** (MIDV-2020 / SIDTD / DLC-2021 / IDNet), re-contextualized for Canadian document types. We redistribute **no** source images; we provide loaders, splits, and the evaluation protocol. |

> **Why not "real" Canadian customer data?** Real Canadian identity data
> (names, SINs, passport/licence images, biometrics) is the most regulated
> category of data under PIPEDA and cannot be lawfully published by an
> individual. Every credible public dataset in this field is therefore
> synthetic-by-design *or* research-licensed. CanFraudBench follows the same
> principle: realism without exposing a single real identity. See
> [`docs/DATA_ETHICS.md`](docs/DATA_ETHICS.md).

---

## What makes it a *governance* benchmark

Every score CanFraudBench reports is paired with the E-23 expectation it speaks
to. A submission produces not just an AUC, but a **validation evidence pack**:
discrimination, calibration, stability/drift, fairness across demographic
slices, and explainability coverage — the dimensions an independent validator
must check. See [`canfraudbench/governance/e23_mapping.py`](canfraudbench/governance/e23_mapping.py).

---

## Quick start

```bash
pip install -e .
# Track A: generate the synthetic-identity benchmark set (reproducible seed)
python -m canfraudbench.synthid.generate --n 20000 --seed 23 --out data/synthid/

# Run the reference baseline and produce a full E-23 evidence pack
python baselines/baseline_synthid.py --data data/synthid/ --report out/evidence_pack.json
```

## Submitting to the leaderboard

CanFraudBench is **submission-by-protocol**: you run the evaluation harness on
your own model and submit the produced `evidence_pack.json` (predictions +
metrics, never raw data). See [`leaderboard/HOW_TO_SUBMIT.md`](leaderboard/HOW_TO_SUBMIT.md).

## Status

Both tracks are **live**:

- **Track A** (synthetic identity): generator, metrics, governance mapping, and
  a calibrated reference baseline that runs end to end.
- **Track B** (document/presentation attack): adapters (SIDTD, MIDV-2020, and a
  generic manifest adapter for any local dataset) plus an evaluation harness
  that produces the same E-23 evidence pack, sliced by attack type and document
  type. Point it at your licensed local copy of the source datasets — images
  are never rebundled.

The reference scorers are deliberately weak floors; both currently post a high
AUC yet **fail overall** on a governance dimension (Track A on fairness, Track B
on calibration), which is the benchmark's entire point.

## License

Code: Apache-2.0. Generated Track-A data: CC BY 4.0. Track-B source datasets
remain under their respective original licenses.

## Citation

See [`CITATION.cff`](CITATION.cff).

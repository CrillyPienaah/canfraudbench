# How to Submit to the CanFraudBench Leaderboard

CanFraudBench is **submission-by-protocol**. You never upload raw data — you
run the evaluation harness against your own model and submit the resulting
`evidence_pack.json`. This keeps the benchmark reproducible and privacy-clean.

## Steps

1. **Get the data.**
   - Track A: generate it deterministically:
     `python -m canfraudbench.synthid.generate --n 20000 --seed 23 --out data/synthid/`
   - Track B: obtain the source datasets from their maintainers under their
     licenses and configure the adapter.

2. **Score it with your model**, producing a probability per record.

3. **Produce the evidence pack.** Wrap your scorer so it emits the same
   `evidence_pack.json` the reference baseline does (use
   `canfraudbench.governance.e23_mapping.build_evidence_pack`). The pack must
   contain: discrimination (AUC/KS), calibration (Brier/ECE), stability (PSI vs
   the published reference split), fairness (AIR, EO gap, demographic-parity
   gap), explainability coverage, and per-typology recall.

4. **Open a pull request** adding your pack to `leaderboard/submissions/` and a
   row to `leaderboard/LEADERBOARD.md`. Include: model description, whether it
   used external data, and a link to reproducible code.

## Ranking

Submissions are **not** ranked by AUC alone. The primary sort is:

1. **Overall E-23 status** (PASS > WARN > FAIL) — a model that fails fairness
   or calibration does not outrank one that passes, regardless of AUC.
2. Among same-status models: mean per-typology recall (rewards models with no
   blind spots over models that ace one easy typology).
3. Tie-break: AUC.

This ordering is the whole point: it rewards *governable* models, not just
discriminative ones. A 0.99-AUC model that fails the four-fifths rule sits
below a 0.92-AUC model that passes every dimension.

## Integrity

- Report whether your model saw any of the evaluation split during training.
- Self-reported packs are accepted but flagged as such until reproduced.
- Reproducibility (seed, code link) is required for a verified badge.

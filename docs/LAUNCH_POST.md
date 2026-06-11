# CanFraudBench — Launch Post (LinkedIn)

> Lead with the result, link the repo, name the deadline. Keep it tight.
> Paste the leaderboard screenshot (the "0.969 AUC / FAIL" row) as the image.

---

**A fraud model can score 0.969 AUC and still fail OSFI E-23. I built a benchmark that shows exactly why.**

Most fraud-model leaderboards rank by accuracy. But starting May 1, 2027, every model at every federally regulated financial institution in Canada falls under OSFI Guideline E-23 — internal *and* third-party models, scored not just on whether they work, but on whether you can validate, monitor, and explain them.

So I built **CanFraudBench**: the first public Canadian identity-fraud benchmark where every score is mapped to an E-23 evidence dimension — discrimination, calibration, stability/drift, fairness, and explainability.

The first thing it surfaced, using its own reference baseline:

→ **AUC 0.969. KS 0.90. Calibration clean. Drift flat.**
→ **And it FAILS overall** — because its Adverse Impact Ratio is 0.59, below the four-fifths fairness floor.

A team optimizing for AUC alone ships that model. Then it triggers a fair-treatment problem no one caught, because the dashboard only showed the number that looked good.

That's the whole point of the benchmark: **discrimination without governance is not a passing model.**

Two tracks, both live:
• **Track A — synthetic identity** (fully synthetic, no real PII; typologies grounded in documented Canadian synthetic-ID fraud)
• **Track B — document & presentation attack** (an adapter protocol over research-licensed datasets like MIDV-2020 / SIDTD — images never rebundled)

Every submission produces an E-23 evidence pack, not just a score. Rankings sort by governance status *first*, AUC last.

It's open source. I'd genuinely like model-risk and fraud DS folks to break it, argue with the thresholds, and submit their own models.

Repo: [link]
The honest caveats (what's a simulator vs. what's real) are in the README — I'd rather you trust the project because it's clear about its scope than because it oversells.

#ModelRisk #OSFI #FraudDetection #ResponsibleAI #Fintech #Canada

---

## Posting notes
- Image: the leaderboard table, or a two-line card: "AUC 0.969 → E-23: FAIL (fairness)."
- First comment: drop the direct link to DATA_ETHICS.md and the (ε,δ)-DP note — it pre-empts the "is this just synthetic noise?" objection and signals rigor.
- Do NOT claim it's adopted, endorsed, or affiliated with OSFI. It maps to the public guideline; it is not approved by anyone. Say "mapped to," never "compliant with."
- Reply to every substantive comment within the first 2 hours — early engagement is what gets it in front of the risk community.

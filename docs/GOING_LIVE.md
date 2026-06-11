# Going Live: Publish Checklist

This is the highest-leverage step. The benchmark generates zero demand until it
is public. Everything below is on your machine; none of it needs more code from
me.

## 1. Push to GitHub (public)

```bash
cd canfraudbench
git init
git add .
git commit -m "CanFraudBench v0.1 — Canadian identity-fraud benchmark with OSFI E-23 mapping"
# create an EMPTY public repo named canfraudbench on GitHub first, then:
git remote add origin https://github.com/CrillyPienaah/canfraudbench.git
git branch -M main
git push -u origin main
```

Reproduce the results so the README's numbers are live, not asserted:

```bash
pip install -e .
python -m canfraudbench.synthid.generate --n 20000 --seed 23 --out data/synthid/
python baselines/baseline_synthid.py \
  --data data/synthid/canfraudbench_synthid_n20000_seed23.jsonl \
  --report out/evidence_pack.json
python tests/test_metrics.py && python tests/test_trackb.py
```

## 2. Verify before you broadcast (do not skip)

- [ ] Read the live OSFI E-23 text and confirm the wording in
      `governance/e23_mapping.py` is a fair restatement. Fix anything that
      drifts. (The May 1, 2027 effective date is confirmed.)
- [ ] Confirm you never say "OSFI-compliant" or "OSFI-approved" anywhere —
      only "mapped to E-23." The project is independent and unaffiliated.
- [ ] Confirm DATA_ETHICS.md's honesty notes are intact (Track A = simulator,
      not DP-from-real-data; Track B = adapters, no rebundled images).
- [ ] Tests green.

## 3. Seed the leaderboard

The two reference packs are already in `leaderboard/submissions/`. Add 1–2 more
baselines yourself so the leaderboard visibly *discriminates* between
approaches (a gradient-boosted model and a rules-only screen are good choices).
An empty or single-row leaderboard reads as a stub; 3–4 rows reads as alive.

## 4. Make it citable

- [ ] CITATION.cff is present. Consider a Hugging Face dataset card for the
      Track-A generated set (slots next to your existing CanFinBench identity).
- [ ] Optional but high-value: a short writeup / arXiv-style note titled
      "Why a fraud model can score 0.97 AUC and still fail OSFI E-23."

## 5. Then — and only then — launch

- [ ] Post (see LAUNCH_POST.md). Image = the 0.969-AUC / FAIL leaderboard row.
- [ ] Send the two outreach messages (National Bank, RBC) with the repo link.
- [ ] Reply to every substantive comment in the first 2 hours.

## 6. After launch (the real next build)

Wire a real (even small) vision model into the Track B `score_fn` and run it on
a genuine slice of MIDV-2020/SIDTD. That converts Track B from "protocol proven
on a synthetic layout" to "protocol proven on real images" — a second
forwardable result. This is the right moment for it: hardening something people
are already looking at, not polishing in the dark.

---

### The one caveat to keep in mind
A benchmark compounds only if it's *adopted*, and adoption is partly outside
your control. Landing the first external submission matters more than any
single post. Optimize for that: make submitting trivial, and personally invite
2–3 specific people to try it.

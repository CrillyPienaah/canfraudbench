# Using CanFraudBench as a Demand-Creation Asset

You asked for a project that compounds — one that makes hiring managers come to
you. A benchmark does that *only if people encounter it and use it*. Code in a
private folder generates zero demand. Here is the honest path from this repo to
inbound interest.

## The one-sentence positioning

> "I built the first public Canadian identity-fraud benchmark where every score
> is mapped to OSFI E-23 model-risk requirements — so a model's AUC and its
> governance verdict show up side by side."

That sentence is your wedge. It is true, specific, and sits in an empty
category. Lead with it everywhere.

## Why this artifact pulls (the mechanics)

- **A benchmark is the measuring stick others report against.** Every time
  someone writes "scored X on CanFraudBench," your name travels into rooms you
  are not in. Tools rot; benchmarks accrue citations.
- **The governance angle is your moat.** Pure-ML people can build a fraud
  detector. The thing almost none of them pairs it with is a regulator-facing
  evidence pack. That intersection is exactly your stated positioning
  (AI Governance Engineer for regulated industries).
- **The headline result does the selling.** Your own baseline posts AUC 0.969
  and still **FAILS** overall on the four-fifths fairness rule (AIR 0.59). That
  single contrast — "great accuracy, fails governance" — is the most
  forwardable thing in the whole project. It is a 30-second story a model-risk
  lead will repeat to their own boss.

## Make it real before you promote it (do not skip)

1. **Ship the repo public** (GitHub) with the README, tests passing, and the
   leaderboard seeded by the reference baseline. An empty leaderboard reads as
   abandoned; a seeded one reads as live.
2. **Add at least 2-3 more baselines yourself** (e.g. a gradient-boosted model,
   a rules-only screen). This shows the leaderboard *discriminates* between
   approaches and gives early visitors signal.
3. **Write the dataset/benchmark card** so it is citable (the CITATION.cff is
   there; consider a short arXiv-style writeup or a Hugging Face dataset card —
   you already host CanFinBench there, so this slots into that identity).
4. **Verify every regulatory claim against the live OSFI E-23 text** before you
   publish. The mapping in this repo is a plain-language restatement; do not let
   a wording error undercut you with the exact audience you want.

## The content sequence (what to actually post)

1. **Launch post**: the one-sentence positioning + the AUC-0.969-but-FAILS
   screenshot + the repo link. Tag the real drivers: E-23 effective May 1 2027,
   Real-Time Rail, synthetic-ID rising fastest in Canada.
2. **A short writeup**: "Why a fraud model can score 0.97 AUC and still fail
   OSFI E-23." Walk through the per-typology and fairness results. This is the
   piece that gets reshared by risk people.
3. **An invitation**: ask practitioners to submit their own models. Adoption is
   the whole game; one external submission is worth more than ten posts.

## Targets (warm, specific)

- **National Bank** — the "Model Risk Governance Specialist, AI Governance" role
  is almost a description of this project. Lead with the repo, not a resume.
- **RBC Enterprise Model Risk Management** — they validate fraud/AML ensembles;
  the evidence-pack framing speaks their language.
- **Scotiabank AML / Model Risk integration** — tie to Real-Time Rail's
  irrevocable payments raising the explainability bar.

## The honest caveats to keep in view

- A benchmark only earns its reputation if it is *adopted*, and adoption is
  partly outside your control. This is a higher-ceiling, higher-variance bet
  than a tool. Seeding it well and recruiting the first external submission is
  where most of the risk lives.
- The v0.1 Track-A data is a typology-grounded *simulator*, not DP-synthesized
  from real data — state that plainly (the repo does). Credibility comes from
  honesty about scope, not from overclaiming a privacy guarantee you are not
  exercising.
- Track B currently ships as adapters over licensed datasets, not bundled
  images. Implementing one real adapter (MIDV-2020 -> SIDTD) end to end is the
  highest-value next build.

## Immediate next build (if you want to keep going)

Implement the MIDV-2020/SIDTD adapter and run a real image baseline so Track B
is live, not stubbed. That turns "two tracks, one live" into "two tracks, both
live" — and a document-forgery leaderboard with Canadian context is itself a
second forwardable artifact.

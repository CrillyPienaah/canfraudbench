# Data Ethics & Legal Basis

CanFraudBench is built so that **no real person's identity data is ever
collected, generated, or redistributed.** This is both an ethical commitment
and the only lawful way for an individual to publish in this domain.

## Why not real Canadian identity data?

Real Canadian onboarding data — names, Social Insurance Numbers, dates of
birth, passport/driver's-licence images, selfies and liveness video — is among
the most sensitive and heavily regulated categories of personal information in
Canada (PIPEDA federally; provincial regimes such as Quebec's Law 25). It
cannot be lawfully collected and **republished** by an individual for public
benchmarking, and the labelled fraud data banks hold is confidential by law
(and intertwined with FINTRAC reporting obligations). There is a hard legal
reason no public Canadian identity-fraud benchmark exists — not a gap in
imagination.

CanFraudBench treats that constraint as a design principle, not an obstacle.

## Track A — Synthetic Identity (data we generate)

* All records are **fully synthetic**. Names come from generic token lists,
  not registries. Addresses use real province/city *labels* with fictitious
  civic numbers and documentation-style postal codes.
* **Social Insurance Numbers are never real.** Legitimate and most fraud
  records carry numbers that deliberately *fail* the Luhn checksum so they can
  never collide with an issued SIN. Only the `blended` typology emits a
  Luhn-valid 9-digit number (to exercise checksum-aware detectors); it is drawn
  at random, avoids temporary (9-series) and 0-prefixed ranges, and is
  overwhelmingly unassigned. These are test fixtures, not PII.
* A synthetic "protected group" attribute (a coarse region grouping) is
  included **solely** so fairness metrics are computable. It encodes no real
  demographic fact about any real person.

### On differential privacy

A common and *correct* way to make synthetic-data releases defensible is to
generate them under a formal **(ε, δ)-differential privacy** guarantee, e.g.
with PATE-GAN or PrivBayes. The (ε, δ)-DP definition is:

> A randomized mechanism *M* is (ε, δ)-differentially private if, for all
> datasets *D* and *D′* differing in a single record, and all measurable
> output sets *S*:
>
>   Pr[M(D) ∈ S]  ≤  e^ε · Pr[M(D′) ∈ S]  +  δ

The **neighbouring-dataset** clause (*D* vs *D′* differing in one record) is
the whole point — it bounds how much any single individual can influence the
output. Any statement of DP that omits it is meaningless. ε is the privacy
budget (smaller = more private); δ allows a small probability of exceeding the
ε bound.

> **Important honesty note:** the v0.1 Track-A generator in this repo is a
> *typology-grounded simulator*, **not** a DP mechanism trained on real data —
> because it never touches real data, there is no individual whose privacy
> needs bounding, so a DP guarantee would be vacuous here. The DP machinery
> becomes relevant only if/when CanFraudBench ingests a real source corpus to
> learn distributions from; at that point a PATE-GAN/PrivBayes path with a
> reported, audited ε is the correct design, and the API is stubbed for it in
> `synthid/dp.py`. We state this plainly rather than claim a privacy guarantee
> we are not currently exercising.

## Track B — Document & Presentation Attack (data we point to)

CanFraudBench redistributes **no** source images. It provides loaders, splits,
and the evaluation protocol over datasets you obtain from their original
maintainers under their own licenses:

| Dataset | Nature | License (verify at source) |
|---|---|---|
| MIDV-2020 | mock ID docs, artificial faces | research use; public-domain/CC source images |
| SIDTD | forgery extension of MIDV-2020 | CC BY-SA 3.0; ethics-board approved |
| DLC-2021 | presentation/liveness attacks | research use |
| IDNet | 837k synthetic ID images, fraud patterns | research/privacy-preserving release |

All are synthetic-by-design or research-licensed. **You are responsible for
complying with each dataset's license**; CanFraudBench only standardizes how
they are evaluated and adds Canadian-document context.

## What this benchmark is *not*

It is not a substitute for validating a model on a bank's own production data
inside the bank's own controls, and it is not regulatory advice. It is a public
*measuring stick* and a governance-aligned evaluation protocol.

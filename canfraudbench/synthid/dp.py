"""
Differential-privacy synthesis path (STUB).

This module exists to make the design intent explicit and to provide a stable
API for the case where CanFraudBench learns distributions from a REAL source
corpus. In that scenario, generating the public release under a formal
(epsilon, delta)-DP guarantee (e.g. PATE-GAN or PrivBayes) is the correct way
to bound any individual record's influence on the output.

It is deliberately NOT wired into the v0.1 generator, because that generator
never touches real data -- there is no individual whose privacy needs bounding,
so a DP guarantee would be vacuous. Claiming DP we are not exercising would be
dishonest; this stub records the intended interface instead.

To activate this path you would:
  1. obtain a lawful real source corpus under appropriate agreements,
  2. fit a DP generator (PATE-GAN/PrivBayes) with a chosen epsilon,
  3. report the (epsilon, delta) budget alongside the released data,
  4. document the privacy accounting in the dataset card.

(epsilon, delta)-DP definition, stated correctly:

    A randomized mechanism M is (epsilon, delta)-differentially private if for
    all datasets D, D' differing in a single record and all output sets S:

        Pr[M(D) in S] <= exp(epsilon) * Pr[M(D') in S] + delta

The neighbouring-dataset clause (D vs D') is essential and must never be
dropped.
"""


class DPGeneratorNotConfigured(NotImplementedError):
    pass


def fit_dp_generator(*args, epsilon=None, delta=None, **kwargs):
    raise DPGeneratorNotConfigured(
        "The DP synthesis path is intentionally inactive in v0.1. The bundled "
        "Track-A generator is a typology-grounded simulator over no real data, "
        "so a DP guarantee would be vacuous. See docs/DATA_ETHICS.md."
    )

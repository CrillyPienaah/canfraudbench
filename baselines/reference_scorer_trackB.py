"""A trivial reference scorer for Track B, used to exercise the harness.

It does NOT look at pixels (we have no real images in CI); it returns a weak
heuristic score from the sample metadata so the pipeline runs end to end. A
real submission replaces this with actual vision-model inference on image_path.
"""
import hashlib

def score(sample):
    # deterministic pseudo-score in [0,1]; nudged up for known attack classes
    h = int(hashlib.md5(sample["id"].encode()).hexdigest(), 16) % 1000 / 1000.0
    base = 0.15 + 0.5 * h
    if sample["attack_type"] in ("crop_replace", "inpaint", "face_morph"):
        base = min(1.0, base + 0.35)
    elif sample["attack_type"] in ("text_field_edit", "copy_move"):
        base = min(1.0, base + 0.2)
    return base

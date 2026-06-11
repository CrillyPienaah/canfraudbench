"""
Track-B adapters (Document & Presentation Attack).

CanFraudBench redistributes NO source images. An adapter points at a LOCAL copy
of a licensed dataset (you obtain it from its maintainer under their license)
and yields a uniform sample stream the evaluation harness understands.

A sample is a dict:
    {
        "id": str,
        "image_path": str,            # local path; harness loads pixels
        "doc_type": str,              # "passport" | "drivers_licence" | "id_card"
        "region": str,                # source region/country tag, e.g. "EU", "US",
                                      # or a Canadian province where applicable
        "label": int,                # 1 = forged/attack, 0 = bona fide
        "attack_type": str,          # normalized OBSERVABLE attack class (see
                                      # ATTACK_VOCAB); "none" for bona fide
        "source_dataset": str,
    }

DESIGN NOTE ON SCHEMA HONESTY
-----------------------------
The sample records describe OBSERVABLE FACTS only (what kind of document, what
manipulation was applied). They deliberately do NOT assign an "OSFI E-23 risk
category" per image. E-23's inherent/residual risk tiering is a property of a
*model and its controls*, not of an individual forged image, and inventing a
forgery-type -> risk-tier mapping would misrepresent the guideline. E-23
evidence is produced at the model level by the governance module, exactly as in
Track A.

ATTACK VOCABULARY
-----------------
We normalize each dataset's native labels into a small shared vocabulary so the
harness can slice metrics by attack type across datasets. These are descriptive
computer-vision manipulation classes, not regulatory categories.
"""

import csv
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

# Normalized, descriptive attack classes (observable manipulations).
ATTACK_VOCAB = {
    "none",            # bona fide
    "crop_replace",    # region cropped and replaced (incl. portrait swap)
    "inpaint",         # generative/seamless fill of altered text or photo
    "copy_move",       # content duplicated within the document
    "text_field_edit", # textual field substitution/erasure
    "face_morph",      # morphed portrait
    "recapture",       # screen/print recapture (presentation attack)
    "other",
}

DOC_TYPES = {"passport", "drivers_licence", "id_card", "other"}


def _normalize_attack(raw):
    if raw is None:
        return "none"
    r = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "bonafide": "none", "bona_fide": "none", "genuine": "none",
        "real": "none", "original": "none", "0": "none",
        "crop_and_replace": "crop_replace", "portrait_substitution": "crop_replace",
        "portrait_swap": "crop_replace", "substitution": "text_field_edit",
        "erasure": "text_field_edit", "inpainting": "inpaint",
        "copymove": "copy_move", "clone": "copy_move", "overlay": "copy_move",
        "morph": "face_morph", "morphing": "face_morph",
        "screen": "recapture", "print": "recapture", "recaptured": "recapture",
    }
    r = aliases.get(r, r)
    return r if r in ATTACK_VOCAB else "other"


def _normalize_doc_type(raw):
    if raw is None:
        return "other"
    r = str(raw).strip().lower()
    if "pass" in r:
        return "passport"
    if "driv" in r or "dl" == r or "licen" in r:
        return "drivers_licence"
    if "id" in r or "card" in r:
        return "id_card"
    return "other"


class DocumentAdapter(ABC):
    name = "abstract"
    source_dataset = "abstract"

    def __init__(self, root_path):
        self.root = Path(root_path)

    def _validate(self, s):
        assert s["doc_type"] in DOC_TYPES, s["doc_type"]
        assert s["attack_type"] in ATTACK_VOCAB, s["attack_type"]
        assert s["label"] in (0, 1)
        return s

    @abstractmethod
    def samples(self):
        """Yield validated sample dicts."""
        raise NotImplementedError


class ManifestAdapter(DocumentAdapter):
    """Most flexible: read a CSV/JSONL manifest the user writes for ANY dataset.

    This is the recommended path -- it means no one has to edit Python to
    register a new local dataset; they describe it in a manifest. Columns/keys:
        id, image_rel_path, doc_type, region, label, attack_type
    """
    name = "manifest"
    source_dataset = "user_manifest"

    def __init__(self, root_path, manifest=None):
        super().__init__(root_path)
        self.manifest = Path(manifest) if manifest else self.root / "manifest.jsonl"

    def _rows(self):
        p = self.manifest
        if not p.exists():
            raise FileNotFoundError(f"No manifest at {p}")
        if p.suffix == ".jsonl":
            with open(p) as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
        elif p.suffix == ".csv":
            with open(p, newline="") as fh:
                for row in csv.DictReader(fh):
                    yield row
        else:
            raise ValueError("manifest must be .jsonl or .csv")

    def samples(self):
        for r in self._rows():
            img = self.root / r.get("image_rel_path", "")
            yield self._validate({
                "id": str(r.get("id")),
                "image_path": str(img),
                "doc_type": _normalize_doc_type(r.get("doc_type")),
                "region": str(r.get("region", "unknown")),
                "label": int(r.get("label", 0)),
                "attack_type": _normalize_attack(r.get("attack_type")),
                "source_dataset": self.source_dataset,
            })


class SIDTDAdapter(DocumentAdapter):
    """SIDTD = forgery extension of MIDV-2020 (CC BY-SA 3.0).

    Expects a metadata.json (list of records) under root_path, each with at
    least: id, image_rel_path, and either is_forgery/label and an anomaly_class.
    Bona fide records come from the MIDV-2020 base; forged from the SIDTD set.
    """
    name = "sidtd"
    source_dataset = "SIDTD"

    def samples(self):
        meta = self.root / "metadata.json"
        if not meta.exists():
            raise FileNotFoundError(
                f"Expected {meta}. Point at your local SIDTD download "
                "(obtained under CC BY-SA 3.0)."
            )
        with open(meta) as fh:
            records = json.load(fh)
        for r in records:
            label = int(r.get("label", r.get("is_forgery", 0)))
            yield self._validate({
                "id": str(r.get("id")),
                "image_path": str(self.root / r.get("image_rel_path", "")),
                "doc_type": _normalize_doc_type(r.get("doc_type", r.get("type"))),
                "region": str(r.get("country", r.get("region", "EU"))),
                "label": label,
                "attack_type": _normalize_attack(
                    r.get("anomaly_class") if label else "none"),
                "source_dataset": self.source_dataset,
            })


class MIDV2020Adapter(DocumentAdapter):
    """MIDV-2020 base: treat all base documents as bona fide (label 0).

    Useful as the negative class to pair with a forgery set. Enumerates image
    files under root_path; doc_type inferred from the path when possible.
    """
    name = "midv2020"
    source_dataset = "MIDV-2020"

    IMG_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

    def samples(self):
        if not self.root.exists():
            raise FileNotFoundError(
                f"{self.root} not found. Point at your local MIDV-2020 copy.")
        i = 0
        for dirpath, _, files in os.walk(self.root):
            for fn in files:
                if Path(fn).suffix.lower() in self.IMG_EXT:
                    i += 1
                    yield self._validate({
                        "id": f"midv2020_{i:06d}",
                        "image_path": str(Path(dirpath) / fn),
                        "doc_type": _normalize_doc_type(dirpath),
                        "region": "EU",
                        "label": 0,
                        "attack_type": "none",
                        "source_dataset": self.source_dataset,
                    })


ADAPTERS = {a.name: a for a in (ManifestAdapter, SIDTDAdapter, MIDV2020Adapter)}


def load_samples(adapter_name, root_path, **kw):
    if adapter_name not in ADAPTERS:
        raise KeyError(f"Unknown adapter '{adapter_name}'. "
                       f"Available: {sorted(ADAPTERS)}")
    return ADAPTERS[adapter_name](root_path, **kw).samples()

"""Track B adapter + harness tests. Run: python tests/test_trackb.py"""
import json, os, tempfile
from canfraudbench.documents.adapters import (
    load_samples, _normalize_attack, _normalize_doc_type, ATTACK_VOCAB)
from canfraudbench.documents import evaluate as E


def test_attack_normalization():
    assert _normalize_attack("Crop-And-Replace") == "crop_replace"
    assert _normalize_attack("bonafide") == "none"
    assert _normalize_attack(None) == "none"
    assert _normalize_attack("something_weird") == "other"
    assert _normalize_attack("inpainting") == "inpaint"
    for v in ATTACK_VOCAB:
        assert _normalize_attack(v) in ATTACK_VOCAB


def test_doc_type_normalization():
    assert _normalize_doc_type("Passport") == "passport"
    assert _normalize_doc_type("driver_license") == "drivers_licence"
    assert _normalize_doc_type("national_id_card") == "id_card"


def test_manifest_adapter_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        rows = [
            {"id": "a", "image_rel_path": "a.png", "doc_type": "passport",
             "region": "EU", "label": 1, "attack_type": "inpaint"},
            {"id": "b", "image_rel_path": "b.png", "doc_type": "id_card",
             "region": "US", "label": 0, "attack_type": "none"},
        ]
        mpath = os.path.join(d, "manifest.jsonl")
        with open(mpath, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        samples = list(load_samples("manifest", d, manifest=mpath))
        assert len(samples) == 2
        assert samples[0]["attack_type"] == "inpaint"
        assert samples[1]["label"] == 0
        # schema must NOT contain a per-image e23 risk category
        assert "e23_risk_category" not in samples[0]


def test_harness_produces_e23_pack():
    samples = [
        {"id": f"x{i}", "image_path": "/dev/null", "doc_type": "passport",
         "region": "EU" if i % 2 else "US",
         "label": 1 if i % 3 == 0 else 0,
         "attack_type": "inpaint" if i % 3 == 0 else "none",
         "source_dataset": "test"}
        for i in range(300)
    ]
    score = lambda s: 0.8 if s["label"] == 1 else 0.2
    pack = E.evaluate(samples, score)
    assert pack["benchmark"] == "CanFraudBench"
    assert "e23_assessment" in pack
    assert "recall_by_attack_type" in pack["metrics"]
    assert pack["submission"]["track"] == "B_document_presentation_attack"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print(f"PASS  {fn.__name__}")
    print(f"\nAll {len(fns)} Track B tests passed.")

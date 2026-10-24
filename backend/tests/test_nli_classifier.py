from app.services.nli_classifier import classify


def test_negation_flip_is_contradiction():
    res = classify(
        "Global temperatures are rising rapidly.",
        "Global temperatures are not rising at all.",
    )
    assert res["label"] == "CONTRADICTION"
    assert res["confidence"] >= 0.5


def test_paraphrase_is_entailment():
    res = classify(
        "The drug lowers blood pressure.",
        "Blood pressure is reduced by the drug.",
    )
    assert res["label"] == "ENTAILMENT"


def test_unrelated_is_neutral():
    res = classify(
        "Cats sit quietly on warm mats.",
        "Quantum physics explores subatomic particles in accelerators.",
    )
    assert res["label"] == "NEUTRAL"
    assert res["confidence"] == 0.4

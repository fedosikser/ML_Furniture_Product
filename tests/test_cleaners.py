from app.cleaners import clean_candidates, normalize_text


def test_normalize_text_trims_spaces_and_entities() -> None:
    assert normalize_text("  Oak&nbsp;Table \n") == "Oak Table"


def test_clean_candidates_filters_noise_and_duplicates() -> None:
    values = ["Shop", "Modern Oak Table", "modern oak table", "%%%"]
    assert clean_candidates(values) == ["Modern Oak Table"]

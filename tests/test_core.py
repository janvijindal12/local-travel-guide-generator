import json

import pytest

from app.core import evaluate_guide, find_sample_guide, load_examples, split_interests


def test_interests_accept_commas_semicolons_and_extra_spaces():
    assert split_interests(" seafood ;  harbor,slow mornings ") == {
        "seafood", "harbor", "slow mornings"
    }


def test_matching_guide_uses_the_best_interest_overlap():
    examples = [
        {"destination": "Bellwether Bay", "interests": "seafood", "guide": "one"},
        {"destination": "Bellwether Bay", "interests": "seafood, harbor", "guide": "two"},
    ]
    assert find_sample_guide("  BELLWETHER BAY ", "seafood, harbor", examples) == "two"


def test_matching_does_not_return_a_guide_for_another_destination():
    assert find_sample_guide("Porto", "seafood") is None


def test_matching_returns_none_for_empty_input():
    assert find_sample_guide("Bellwether Bay", "  ") is None


def test_dataset_rows_have_all_required_fields(tmp_path):
    path = tmp_path / "guides.jsonl"
    path.write_text(json.dumps({"destination": "Bay", "guide": "text"}), encoding="utf-8")
    with pytest.raises(ValueError, match="must include"):
        load_examples(path)


def test_relevance_score_and_length_limit():
    guide = "Bellwether Bay has seafood by the harbor and lovely views."
    result = evaluate_guide(guide, "Bellwether Bay", "seafood, harbor")
    assert result["relevance_score"] == 1.0
    assert result["concise"] is True
    assert result["word_count"] == len(guide.split())


def test_long_guide_is_flagged_as_not_concise():
    result = evaluate_guide("word " * 181, "Bellwether Bay", "seafood")
    assert result["concise"] is False

from app.core import evaluate_guide, find_sample_guide


def test_finds_sample_for_matching_destination_and_interest():
    guide = find_sample_guide(" porto ", "food, architecture")
    assert guide is not None
    assert "Ribeira" in guide


def test_no_guide_for_unknown_destination():
    assert find_sample_guide("Kyoto", "food") is None


def test_evaluation_reports_interest_overlap():
    result = evaluate_guide("Porto has lovely food and architecture.", "Porto", "food, architecture")
    assert result["concise"] is True
    assert result["relevance_score"] == 1.0

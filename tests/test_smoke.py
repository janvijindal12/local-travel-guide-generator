from app.evaluation import run_evaluation
from app.llm import NO_MATCH, generate_guide


def test_sample_mode_returns_a_curated_guide(monkeypatch):
    monkeypatch.setenv("TRAVEL_GUIDE_MODE", "sample")
    guide, source = generate_guide("Bellwether Bay", "seafood, harbor")
    assert "East Quay" in guide
    assert source == "Curated sample"


def test_sample_mode_explains_an_unmatched_request(monkeypatch):
    monkeypatch.setenv("TRAVEL_GUIDE_MODE", "sample")
    guide, _ = generate_guide("A different place", "seafood")
    assert guide == NO_MATCH


def test_evaluation_compares_examples_with_a_generic_baseline():
    result = run_evaluation()
    assert result["example_count"] == 8
    assert result["matched_examples"] == 8
    assert result["mean_tailored_relevance"] > result["mean_generic_baseline_relevance"]


def test_streamlit_page_renders_and_builds_a_guide():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file("app/main.py").run()
    assert not app.exception
    assert app.title[0].value == "Bellwether Bay Guidebook"

    app.multiselect[0].set_value(["seafood", "harbor"])
    app.button[0].click().run()
    assert not app.exception
    assert any("East Quay" in item.value for item in app.markdown)

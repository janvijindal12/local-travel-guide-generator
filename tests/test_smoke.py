from app.llm import generate_guide


def test_sample_mode_generates_a_guide(monkeypatch):
    monkeypatch.setenv("TRAVEL_GUIDE_MODE", "sample")
    guide, source = generate_guide("Porto", "food, architecture")
    assert guide
    assert source == "Sample guide"

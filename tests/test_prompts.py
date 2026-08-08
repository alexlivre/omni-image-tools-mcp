from src.prompts import get_vision_prompt


def test_pt_prompt_loaded(monkeypatch):
    monkeypatch.setenv("OMNI_LANG", "pt")
    text = get_vision_prompt("analyze_image", "standard")
    assert "descrição" in text  # Portuguese prompt, not English fallback


def test_en_default(monkeypatch):
    monkeypatch.delenv("OMNI_LANG", raising=False)
    text = get_vision_prompt("analyze_image", "standard")
    assert "comprehensive" in text

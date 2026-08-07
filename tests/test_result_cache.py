from src.utils.result_cache import _CACHE_ENABLED, cached, cache_result, make_key


def test_cache_roundtrip_when_enabled(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_CACHE", "1")
    import src.utils.result_cache as rc

    rc._CACHE.clear()
    key = make_key("analyze_image", "abc", "desc", "m")
    assert cached(key) is None
    cache_result(key, "result text")
    assert cached(key) == "result text"


def test_cache_disabled_by_default(monkeypatch):
    monkeypatch.delenv("OMNI_VISION_CACHE", raising=False)
    import src.utils.result_cache as rc

    rc._CACHE.clear()
    assert _CACHE_ENABLED is False
    cache_result("k", "v")
    assert cached("k") is None

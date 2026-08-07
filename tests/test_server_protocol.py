"""Protocol-level tests for the MCP server.

Validates the protocol contract through the building blocks the handler uses
(TOOL_SCHEMAS drive tools/list; helpers drive tools/call) rather than poking
SDK-internal request handlers, which are fragile across SDK versions.
"""

import pytest

from src.server import _error_result, _result_text, _validate_image_paths
from src.tools import TOOL_SCHEMAS


class TestToolSchemasContract:
    def test_all_tools_have_title(self):
        for name, schema in TOOL_SCHEMAS.items():
            assert schema.get("title"), f"{name} missing title"

    def test_all_tools_have_full_annotations(self):
        for name, schema in TOOL_SCHEMAS.items():
            ann = schema.get("annotations")
            assert ann, f"{name} missing annotations"
            for key in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
                assert isinstance(ann[key], bool), f"{name}.{key} must be bool"

    def test_readonly_tools_not_destructive_and_idempotent(self):
        for name, schema in TOOL_SCHEMAS.items():
            ann = schema["annotations"]
            if ann["readOnlyHint"]:
                assert ann["destructiveHint"] is False, f"{name} read-only but destructive"
                assert ann["idempotentHint"] is True, f"{name} read-only but not idempotent"

    def test_descriptions_are_static(self):
        for name, schema in TOOL_SCHEMAS.items():
            assert "Current provider:" not in schema.get("description", ""), name

    def test_download_and_extract_are_write_open_world_split(self):
        assert TOOL_SCHEMAS["download_image"]["annotations"]["openWorldHint"] is True
        assert TOOL_SCHEMAS["download_image"]["annotations"]["readOnlyHint"] is False
        assert TOOL_SCHEMAS["extract_object"]["annotations"]["readOnlyHint"] is False
        assert TOOL_SCHEMAS["extract_object"]["annotations"]["openWorldHint"] is False


class TestErrorHandler:
    def test_error_result_iserror_true(self):
        result = _error_result("boom")
        assert result.isError is True
        assert "Error" in result.content[0].text
        assert "boom" in result.content[0].text

    def test_success_result_iserror_false(self):
        result = _error_result("x") if False else _result_result_success()
        assert result.isError is False

    def test_success_result_through_text(self):
        text = _result_text({"success": True, "result": "ok", "provider": "ollama"})
        assert text == "ok"

    def test_result_text_strips_output_data(self):
        text = _result_text(
            {
                "success": True,
                "original_format": "JPEG",
                "new_format": "WEBP",
                "output_data": b"\x00\x01\x02",
                "output_size_bytes": 3,
            }
        )
        assert "output_data" not in text
        assert "JPEG" in text
        assert "WEBP" in text

    def test_result_text_appends_content_warning(self):
        text = _result_text(
            {
                "success": True,
                "local_path": "/tmp/x.png",
                "content_warning": "untrusted content",
            }
        )
        assert "content_warning" in text
        assert "untrusted content" in text


def _result_result_success():
    from src.server import _success_result

    return _success_result({"success": True, "result": "ok"})


class TestPathValidation:
    def test_missing_image_path_raises_filenotfound(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            _validate_image_paths({"image_path": str(tmp_path / "nope.jpg")})

    def test_valid_image_path_passes(self, tmp_path):
        f = tmp_path / "img.jpg"
        f.write_bytes(b"x")
        _validate_image_paths({"image_path": str(f)})

    def test_compares_image_paths_validated(self, tmp_path):
        a = tmp_path / "a.jpg"
        b = tmp_path / "b.jpg"
        a.write_bytes(b"x")
        b.write_bytes(b"x")
        with pytest.raises(FileNotFoundError):
            _validate_image_paths({"image_paths": [str(a), str(tmp_path / "missing.jpg")]})


def test_deterministic_tools_have_output_schema():
    for name in ("get_image_info", "crop_image", "convert_image_format",
                 "prepare_image", "download_image", "extract_object",
                 "get_provider_info"):
        assert TOOL_SCHEMAS[name].get("outputSchema"), f"{name} missing outputSchema"

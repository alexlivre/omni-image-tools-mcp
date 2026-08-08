"""Smoke tests for the FastMCP server scaffold (src/server_fastmcp.py).

The invariant asserted here is tool registration parity: exactly the 11 tools
from TOOL_SCHEMAS, exposed with matching names, titles, and annotations.
No provider is contacted.
"""

import asyncio
import time

import pytest

from src.server_fastmcp import _analyze, build_server
from src.tools import TOOL_SCHEMAS


def test_build_server_exposes_11_tools():
    mcp = build_server()
    names = set(mcp._tool_manager._tools.keys())
    assert len(names) == 11
    assert "analyze_image" in names
    assert "get_provider_info" in names


@pytest.mark.asyncio
async def test_list_tools_matches_schema_names():
    mcp = build_server()
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert names == set(TOOL_SCHEMAS.keys())
    assert len(names) == 11


@pytest.mark.asyncio
async def test_tool_titles_and_annotations_match_schemas():
    mcp = build_server()
    tools = await mcp.list_tools()
    by_name = {t.name: t for t in tools}
    for name, schema in TOOL_SCHEMAS.items():
        tool = by_name[name]
        assert tool.title == schema["title"]
        ann = schema["annotations"]
        assert tool.annotations.readOnlyHint == ann["readOnlyHint"]
        assert tool.annotations.destructiveHint == ann["destructiveHint"]
        assert tool.annotations.idempotentHint == ann["idempotentHint"]
        assert tool.annotations.openWorldHint == ann["openWorldHint"]


@pytest.mark.asyncio
async def test_analyze_returns_friendly_error_on_missing_file():
    async def boom():
        raise FileNotFoundError(2, "No such file or directory", "nope.png")

    result = await _analyze(None, time.time(), boom(), None, op_name="get_image_info")

    assert result["success"] is False
    assert "nope.png" in result["error"]
    assert "Image not found" in result["error"]
    assert "processing_time_ms" in result


@pytest.mark.asyncio
async def test_analyze_returns_friendly_error_on_timeout():
    async def slow():
        await asyncio.sleep(1)
        return {"success": True}

    result = await _analyze(None, time.time(), slow(), timeout=0.01, op_name="download_image")

    assert result["success"] is False
    assert "timed out" in result["error"]
    assert "processing_time_ms" in result

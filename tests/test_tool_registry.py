"""Tests for ToolRegistry and register_all_tools."""

from src.tools import ToolRegistry, TOOL_SCHEMAS, register_all_tools


def test_tool_schemas_count():
    assert len(TOOL_SCHEMAS) >= 10


def test_register_and_get_tool():
    ToolRegistry._tools.clear()

    def fake_func(**kwargs):
        return {"success": True}

    ToolRegistry.register("test_tool", fake_func, {"description": "test"})
    tool = ToolRegistry.get_tool("test_tool")
    assert tool is not None
    assert tool["func"] == fake_func
    assert tool["schema"]["description"] == "test"


def test_get_unknown_tool():
    ToolRegistry._tools.clear()
    assert ToolRegistry.get_tool("nonexistent") is None


def test_list_tools():
    ToolRegistry._tools.clear()

    def fake_func(**kwargs):
        return {"success": True}

    ToolRegistry.register("a", fake_func, {})
    ToolRegistry.register("b", fake_func, {})

    tools = ToolRegistry.list_tools()
    assert len(tools) == 2
    names = [t["name"] for t in tools]
    assert "a" in names
    assert "b" in names


def test_register_all_tools_covers_all_schemas():
    ToolRegistry._tools.clear()
    register_all_tools()
    registered = ToolRegistry.list_tools()
    registered_names = {t["name"] for t in registered}
    schema_names = set(TOOL_SCHEMAS.keys())
    assert schema_names == registered_names, (
        f"Missing from registry: {schema_names - registered_names} "
        f"Extra in registry: {registered_names - schema_names}"
    )

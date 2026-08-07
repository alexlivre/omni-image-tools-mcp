#!/usr/bin/env python3
"""Deterministic evaluation runner for omni-image-tools-mcp.

Replays the 10 read-only QA pairs defined in scripts/evaluations.xml against the
tool layer. Vision/LLM calls (analyze_image, read_text) and get_provider_info
are mocked so no provider or network is touched; PIL-based processing tools run
against the real fixture images. Exits 1 if any QA pair fails.
"""

import asyncio
import inspect
import os
import sys
import time
import xml.etree.ElementTree as ET
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(REPO_ROOT))

VISION_TOOLS = {"read_text", "analyze_image"}


def _coerce(value, value_type):
    if value_type == "int":
        return int(value)
    if value_type == "bool":
        return str(value).lower() in ("true", "1", "yes")
    if value_type == "float":
        return float(value)
    return str(value)


def _resolve_param(value):
    candidate = REPO_ROOT / value
    if not Path(value).is_absolute() and candidate.exists():
        return str(candidate)
    return value


def _resolve_field(result, field):
    node = result
    for part in field.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, (list, tuple)) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            raise KeyError(field)
    return node


def _check_passes(check, result):
    op = check.get("op")
    if op == "exists":
        _resolve_field(result, check.get("field"))
        return True
    if op == "raise":
        return True
    actual = _resolve_field(result, check.get("field"))
    expected = _coerce(check.get("value"), check.get("type", "str"))
    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "contains":
        return expected in str(actual)
    if op == "lte":
        return actual <= expected
    if op == "gte":
        return actual >= expected
    return False


def _expected_result(qa):
    for check in qa.findall("check"):
        if check.get("field") == "result":
            return _coerce(check.get("value"), check.get("type", "str"))
    return "MOCKED_RESULT"


def _patches_for(tool, qa):
    if tool in VISION_TOOLS:
        provider = MagicMock()
        provider.analyze = AsyncMock(return_value=_expected_result(qa))
        return [
            patch("src.providers.ProviderFactory.get", return_value=provider),
            patch(
                "src.utils.gpu_memory.GPUResourceManager.ensure_single_provider",
                new=AsyncMock(return_value={"status": "ok", "warnings": []}),
            ),
        ]
    if tool == "get_provider_info":
        provider = SimpleNamespace(is_local=True, image_limit_per_request=1)
        return [patch("src.providers.ProviderFactory.get", return_value=provider)]
    return []


async def _invoke(tool, func, params):
    if tool == "analyze_image":
        from src.server_fastmcp import _analyze

        return await _analyze(None, time.time(), func(**params), 120)
    result = func(**params)
    if inspect.isawaitable(result):
        return await result
    return result


async def _run_qa(qa, tools):
    tool = qa.get("tool")
    func = tools[tool]
    params = {
        p.get("name"): _coerce(_resolve_param(p.get("value")), p.get("type", "str"))
        for p in qa.findall("param")
    }
    checks = qa.findall("check")
    raise_check = next((c for c in checks if c.get("op") == "raise"), None)
    normal_checks = [c for c in checks if c.get("op") != "raise"]

    patches = _patches_for(tool, qa)
    try:
        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            result = await _invoke(tool, func, params)
    except Exception as exc:
        if raise_check is not None:
            if type(exc).__name__ == raise_check.get("value"):
                return True, ""
            return False, f"raised {type(exc).__name__}, expected {raise_check.get('value')}"
        return False, f"unexpected {type(exc).__name__}: {exc}"

    if raise_check is not None:
        return False, f"expected {raise_check.get('value')} to be raised"

    for check in normal_checks:
        try:
            passed = _check_passes(check, result)
        except Exception as exc:
            return False, f"check '{check.get('field')}' could not resolve: {exc}"
        if not passed:
            expected = check.get("value")
            return False, f"check '{check.get('field')} {check.get('op')} {expected}' failed"
    return True, ""


def main():
    os.environ.setdefault("OMNI_VISION_PROVIDER", "ollama")
    os.environ.setdefault("OLLAMA_ALLOWED_MODELS", "qwen3-vl:4b,qwen3-vl:2b")

    from src.tools.processing.convert import convert_image_format
    from src.tools.processing.crop import crop_image
    from src.tools.processing.info import get_image_info
    from src.tools.processing.prepare import prepare_image
    from src.tools.system.provider_info import get_provider_info
    from src.tools.vision.analyze import analyze_image
    from src.tools.vision.read_text import read_text

    tools = {
        "get_image_info": get_image_info,
        "crop_image": crop_image,
        "convert_image_format": convert_image_format,
        "prepare_image": prepare_image,
        "get_provider_info": get_provider_info,
        "read_text": read_text,
        "analyze_image": analyze_image,
    }

    tree = ET.parse(SCRIPT_DIR / "evaluations.xml")
    qas = tree.getroot().findall("qa")

    async def run_all():
        return [await _run_qa(qa, tools) for qa in qas]

    results = asyncio.run(run_all())

    passed = 0
    for qa, (ok, reason) in zip(qas, results):
        if ok:
            passed += 1
        status = "PASS" if ok else "FAIL"
        print(f"{status}  [{qa.get('id')}] {qa.get('description')}")
        if not ok:
            print(f"       {reason}")

    total = len(qas)
    print(f"{passed}/{total} PASS")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()

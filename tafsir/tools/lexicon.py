"""Lexicon-level MCP tools: get_root_definition."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from tafsir.adapters.lexicon import LexiconAdapter

_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)

_adapter = LexiconAdapter()


def get_root_definition(
    root: Annotated[str, Field(description="الجذر اللغوي للبحث عنه (مثال: 'رحم'، 'كتب'، 'علم')")]
) -> dict:
    """البحث عن معنى جذر لغوي في المعاجم اللغوية الكلاسيكية.

    يبحث في:
    1. لسان العرب (ابن منظور)
    2. معجم مقاييس اللغة (ابن فارس)
    3. مفردات ألفاظ القرآن (الراغب الأصفهاني)
    """
    cleaned_root = root.strip()
    definitions = _adapter.get_definitions(cleaned_root)

    if not definitions or not any(definitions.values()):
        return {
            "root": root,
            "found": False,
            "message": f"لم يتم العثور على تعريف للجذر '{root}' في المعاجم المتاحة."
        }

    return {
        "root": root,
        "found": True,
        "lisanularab": definitions.get("lisanularab"),
        "maqayeesul_luga": definitions.get("maqayeesul_luga"),
        "mufradat_alfajul_quran": definitions.get("mufradat_alfajul_quran"),
    }


def register(mcp: FastMCP) -> None:
    mcp.tool(name="get_root_definition", annotations=_ANNOTATIONS)(get_root_definition)

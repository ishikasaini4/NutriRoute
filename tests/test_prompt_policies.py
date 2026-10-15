"""Checks the Day 5 citation/safety policy text is present in the system
prompt. Owner: Member M, Day 5.

This is an offline content check only — it doesn't verify a real model
actually follows the policy; that's Day 6's job.
"""

from app.agent.prompts import (
    CITATION_TAG_FORMAT,
    DISCLAIMER_SENTENCE,
    SYSTEM_PROMPT,
)


def test_citation_tag_format_present():
    assert CITATION_TAG_FORMAT in SYSTEM_PROMPT


def test_disclaimer_sentence_present():
    assert DISCLAIMER_SENTENCE in SYSTEM_PROMPT


def test_tool_list_present_for_all_registered_tools():
    from app.agent.tool_registry import TOOL_REGISTRY

    for name in TOOL_REGISTRY:
        assert name in SYSTEM_PROMPT

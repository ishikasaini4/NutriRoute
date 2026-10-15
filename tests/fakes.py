"""Test-only fakes. Owner: Member M, Day 2."""

from app.agent.llm_client import LLMResponse


class FakeLLMClient:
    """Scripted LLMClient: .chat() pops the next response in order.

    Raises AssertionError if called past the script, so a loop bug (e.g.
    an extra unexpected LLM call) fails loudly instead of silently.
    """

    def __init__(self, script: list[LLMResponse]):
        self._script = list(script)
        self.calls: list[dict] = []

    def chat(self, messages: list[dict], tools: list[dict], tool_choice: str = "auto") -> LLMResponse:
        self.calls.append({"messages": messages, "tools": tools, "tool_choice": tool_choice})
        if not self._script:
            raise AssertionError("FakeLLMClient called past the end of its scripted responses")
        return self._script.pop(0)

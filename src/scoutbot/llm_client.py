"""LLM providers: the only place that talks to a model SDK."""

from anthropic import Anthropic

from scoutbot.interfaces import LLMClient


class AnthropicClient(LLMClient):
    """LLMClient backed by the Anthropic Messages API."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 1024):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def send(self, messages: list[dict], tools: list[dict]):
        return self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"},
        )

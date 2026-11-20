"""LLM providers: the only place that talks to a model SDK."""

import logging

from anthropic import Anthropic

from scoutbot.interfaces import LLMClient

logger = logging.getLogger(__name__)


class AnthropicClient(LLMClient):
    """LLMClient backed by the Anthropic Messages API."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 1024):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def send(self, messages: list[dict], tools: list[dict]):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"},
        )
        self.log_response(response)
        return response

    def log_response(self, response) -> None:
        """Log why the model stopped, token usage, and the interesting content blocks."""
        logger.info(
            "stop_reason=%s, tokens in=%d out=%d",
            response.stop_reason,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        for block in response.content:
            if block.type == "text":
                logger.debug("Model text: %s", block.text)
            elif block.type == "server_tool_use":
                logger.info("Server tool call : %s(%s)", block.name, block.input)
            elif block.type == "web_fetch_tool_result":
                logger.info("Web fetch result received")

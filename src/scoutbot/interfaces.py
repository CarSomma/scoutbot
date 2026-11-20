"""Interfaces: what the core needs, without saying who provides it."""

from dataclasses import dataclass
from typing import Callable

from scoutbot.schema import Customer

# Tool name -> function that runs the tool. Called as handler(**tool_input);
# returns the text sent back to the model, or raises LookupError for a tool error.
ToolHandlers = dict[str, Callable[..., str]]


@dataclass(frozen=True)
class Toolset:
    """Everything the triage loop needs to know about tools, in one place."""

    definitions: list[dict]  # sent to the model so it knows which tools exist
    handlers: ToolHandlers  # run in Python when the model calls a tool
    final_tool_name: str  # calling this tool ends the loop with the triage decision


class CustomerRepository:
    """Somewhere customers can be looked up. Subclasses must implement lookup()."""

    def lookup(self, customer_id: str) -> Customer:
        """Return the customer with this ID, or raise LookupError if unknown."""
        raise NotImplementedError


class LLMClient:
    """Something that can send a conversation to a model. Subclasses must implement send()."""

    def send(self, messages: list[dict], tools: list[dict]):
        """Send the conversation and tools; return the model's reply.

        The reply must have .content (list of blocks), .stop_reason and .usage.
        """
        raise NotImplementedError

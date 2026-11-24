"""Interfaces: what the core needs, without saying who provides it."""

from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field

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
        pass


class LLMClient(BaseModel):
    """Something that can send a conversation to a model. Subclasses must implement send().

    Holds the settings every LLM client has; subclasses only add what is specific
    to their provider.
    """

    model_config = ConfigDict(extra="forbid")

    model: str  # which model to call
    max_tokens: int = Field(default=1024, gt=0)  # upper limit for the reply length

    def send(self, messages: list[dict], tools: list[dict]):
        """Send the conversation and tools; return the model's reply.
        """
        pass

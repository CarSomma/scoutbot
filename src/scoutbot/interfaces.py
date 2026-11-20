"""Interfaces: what the core needs, without saying who provides it."""

from scoutbot.schema import Customer


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

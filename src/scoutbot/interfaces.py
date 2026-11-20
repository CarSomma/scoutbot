"""Interfaces: what the core needs, without saying who provides it."""

from scoutbot.schema import Customer


class CustomerRepository:
    """Somewhere customers can be looked up. Subclasses must implement lookup()."""

    def lookup(self, customer_id: str) -> Customer:
        """Return the customer with this ID, or raise LookupError if unknown."""
        raise NotImplementedError

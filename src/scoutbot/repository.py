"""Data access: where customer records come from."""

from scoutbot.interfaces import CustomerRepository
from scoutbot.schema import Customer
from scoutbot.utils import load_customers


class JsonCustomerRepository(CustomerRepository):
    """Customers stored in a JSON file inside a package. Loaded once, on creation."""

    def __init__(self, path: str, package: str = "scoutbot"):
        self.customers = load_customers(path, package)

    def lookup(self, customer_id: str) -> Customer:
        """Return the customer with this ID, or raise LookupError if unknown."""
        record = self.customers.get(customer_id)
        if not record:
            raise LookupError(f"Customer with ID {customer_id} not found.")
        return Customer.model_validate(record)

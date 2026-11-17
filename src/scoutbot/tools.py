"""Definitions of tools and their corresponding Python functions."""

from scoutbot.schema import Customer, LookupCustomerInput, TriageResult
from scoutbot.utils import load_customers

TRIAGE_TOOL = {
    "name": "support_ticket_triage",
    "description": "Triages support tickets and suggests the appropriate owner, priority, and category.",
    "strict": True,
    "input_schema": TriageResult.model_json_schema(),
}

LOOKUP_CUSTOMER_TOOL = {
    "name": "lookup_customer",
    "description": "Look up a customer by ID. Returns their plan, account age in days and number of refunds in the last 90 days. Use it before deciding priority when the ticket mentions a customer ID.",
    "strict": True,
    "input_schema": LookupCustomerInput.model_json_schema(),
}


def lookup_customer(customer_id: str) -> Customer:
    """Looks up a customer by ID and returns their plan,
    account age in days, and number of refunds in the last 90 days."""

    customers = load_customers("data/mock_customers.json", "scoutbot")
    record = customers.get(customer_id)
    if not record:
        raise LookupError(f"Customer with ID {customer_id} not found.")
    return Customer.model_validate(record)


TOOLS = [LOOKUP_CUSTOMER_TOOL, TRIAGE_TOOL]

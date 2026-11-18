"""Definitions of tools and their corresponding Python functions."""

import logging

from scoutbot.schema import Customer, EscalateInput, LookupCustomerInput, TriageResult
from scoutbot.utils import load_customers

logger = logging.getLogger(__name__)

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


ESCALATE_TOOL = {
    "name": "escalate_to_human",
    "description": (
        "Hand the ticket to a human agent, with a short reason. A human must approve "
        "the escalation before it takes effect; the result tells you whether it was "
        "approved or rejected. If rejected, continue triaging the ticket yourself."
    ),
    "strict": True,
    "input_schema": EscalateInput.model_json_schema(),
}


def ask_human_approval(reason: str) -> bool:
    """Ask the operator on the terminal to approve an escalation (y/n).

    Anything other than an explicit yes, including no input at all, is a rejection.
    """
    try:
        answer = input(
            f"\nModel wants to escalate to a human.\nReason: {reason}\nApprove? [y/N] "
        )
    except EOFError:
        return False
    return answer.strip().lower() in {"y", "yes"}


def escalate_to_human(reason: str) -> str:
    """Perform the escalation. Only call this after a human has approved it."""
    logger.warning("ESCALATED to human: %s", reason)
    return f"Escalation filed. Reason: {reason}"

# https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#zdr-and-allowed-callers
WEB_FETCH_TOOL = {
    "type": "web_fetch_20260209", # version that does dynamic filtering
    "name": "web_fetch", 
    "max_uses": 5,
    "allowed_domains": ["status.mollie.com"],
    "allowed_callers": ["direct"]
}


TOOLS = [LOOKUP_CUSTOMER_TOOL, ESCALATE_TOOL, WEB_FETCH_TOOL, TRIAGE_TOOL]

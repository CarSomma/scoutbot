"""Definitions of tools and their corresponding Python functions."""

import logging
from typing import Callable

from scoutbot.interfaces import CustomerRepository
from scoutbot.schema import EscalateInput, LookupCustomerInput, TriageResult

logger = logging.getLogger(__name__)


# --- Tool definitions (what the model sees) -----------------------------------

TRIAGE_TOOL = {
    "name": "support_ticket_triage",
    "description": (
        "Triages support tickets and suggests the appropriate owner, priority, "
        "and category."
    ),
    "strict": True,
    "input_schema": TriageResult.model_json_schema(),
}

LOOKUP_CUSTOMER_TOOL = {
    "name": "lookup_customer",
    "description": (
        "Look up a customer by ID. Returns their plan, account age in days and "
        "number of refunds in the last 90 days. Use it before deciding priority "
        "when the ticket mentions a customer ID."
    ),
    "strict": True,
    "input_schema": LookupCustomerInput.model_json_schema(),
}

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

# Server tool: runs on Anthropic's side, so it has no Python handler.
# https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#zdr-and-allowed-callers
WEB_FETCH_TOOL = {
    "type": "web_fetch_20260209",  # version that does dynamic filtering
    "name": "web_fetch",
    "max_uses": 5,
    "allowed_domains": ["status.mollie.com"],
    "allowed_callers": ["direct"],
}


# --- Tool functions (what runs when the model calls a tool) -------------------
# Every handler returns a str: that is what gets sent back to the model.

def make_lookup_handler(customers: CustomerRepository) -> Callable[..., str]:
    """Wrap customers.lookup so the tool returns the customer as JSON text."""

    def lookup_customer(customer_id: str) -> str:
        return customers.lookup(customer_id).model_dump_json()

    return lookup_customer


def escalate_to_human(reason: str) -> str:
    """Perform the escalation. Only call this after a human has approved it."""
    logger.warning("ESCALATED to human: %s", reason)
    return f"Escalation filed. Reason: {reason}"


ESCALATION_REJECTED_MSG = (
    "A human reviewed this escalation and rejected it. The ticket "
    "was NOT escalated. Continue triaging it yourself."
)


def make_escalate_handler(approve: Callable[[str], bool]) -> Callable[..., str]:
    """Wrap escalate_to_human in a gate: it only runs if `approve(reason)` says yes."""

    def escalate(reason: str) -> str:
        if not approve(reason):
            # Rejection is a normal observation, not an error: the loop goes on.
            logger.info("Escalation rejected by human")
            return ESCALATION_REJECTED_MSG
        logger.info("Escalation approved by human")
        return escalate_to_human(reason)

    return escalate


# --- Registries ---------------------------------------------------------------

TOOLS = [LOOKUP_CUSTOMER_TOOL, ESCALATE_TOOL, WEB_FETCH_TOOL, TRIAGE_TOOL]

ToolHandlers = dict[str, Callable[..., str]]


def make_tool_handlers(
    customers: CustomerRepository, approve: Callable[[str], bool]
) -> ToolHandlers:
    """Tool name -> the Python function that runs it.

    The model's tool input is passed as keyword arguments: handler(**block.input).
    `approve` is asked before any escalation takes effect.
    """
    return {
        LOOKUP_CUSTOMER_TOOL["name"]: make_lookup_handler(customers),
        ESCALATE_TOOL["name"]: make_escalate_handler(approve),
    }


# --- Helpers ------------------------------------------------------------------

def make_tool_result(tool_use_id: str, content: str, is_error: bool = False) -> dict:
    """Build the tool_result block that answers one tool_use block."""
    result = {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
    if is_error:
        result["is_error"] = True
    return result

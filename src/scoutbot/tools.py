"""Definitions of tools and their corresponding Python functions."""

import logging
from typing import Callable

from scoutbot.repository import JsonCustomerRepository
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

def escalate_to_human(reason: str) -> str:
    """Perform the escalation. Only call this after a human has approved it."""
    logger.warning("ESCALATED to human: %s", reason)
    return f"Escalation filed. Reason: {reason}"


# --- Human approval -----------------------------------------------------------

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


# --- Registries ---------------------------------------------------------------

TOOLS = [LOOKUP_CUSTOMER_TOOL, ESCALATE_TOOL, WEB_FETCH_TOOL, TRIAGE_TOOL]

ToolHandlers = dict[str, Callable[..., object]]


def make_tool_handlers(customers: JsonCustomerRepository) -> ToolHandlers:
    """Tool name -> the Python function that runs it.

    The model's tool input is passed as keyword arguments: handler(**block.input).
    """
    return {
        LOOKUP_CUSTOMER_TOOL["name"]: customers.lookup,
        ESCALATE_TOOL["name"]: escalate_to_human,
    }


# --- Helpers ------------------------------------------------------------------

def make_tool_result(tool_use_id: str, content: str, is_error: bool = False) -> dict:
    """Build the tool_result block that answers one tool_use block."""
    result = {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
    if is_error:
        result["is_error"] = True
    return result

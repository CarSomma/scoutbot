import logging
from collections.abc import Callable

from anthropic import Anthropic

from scoutbot.config import llms_settings
from scoutbot.schema import TriageResult
from scoutbot.tools import TOOLS, ask_human_approval, escalate_to_human, lookup_customer

logger = logging.getLogger(__name__)

client = Anthropic(api_key=llms_settings.anthropic_api_key.get_secret_value())

PROMPT_TEMPLATE = """You are a support ticket triage assistant.

Customer ID: {customer_id}
Ticket: {ticket}

Look up the customer first, then call support_ticket_triage with your decision.
If the ticket needs a human (e.g. legal threats, safety issues, or you cannot
triage it confidently), call escalate_to_human with a reason. A human must approve
it; if they reject it, keep going.
If the ticket could be caused by a payment provider outage, check https://status.mollie.com/api/v2/components.json.
Always finish by calling support_ticket_triage. Never ask questions."""


def triage_ticket(
    ticket: str,
    client: Anthropic,
    tools: list[dict],
    customer_id: str,
    max_turns: int = 5,
    approve: Callable[[str], bool] = ask_human_approval,
) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.

    `approve` is asked before any escalate_to_human call takes effect; it gets the
    model's reason and returns True to approve, False to reject.
    """
    messages = [
        {
            "role": "user",
            "content": PROMPT_TEMPLATE.format(customer_id=customer_id, ticket=ticket),
        }
    ]

    logger.info("Triaging ticket for customer %s", customer_id)

    for turn in range(1, max_turns + 1):
        response = client.messages.create(
            model=llms_settings.anthropic_model,
            max_tokens=1024,
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"},
        )
        logger.info(
            "Turn %d/%d: stop_reason=%s, tokens in=%d out=%d",
            turn,
            max_turns,
            response.stop_reason,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "pause_turn":
            continue  # API paused mid server-tool work; resend so it resumes

        tool_result = []
        for block in response.content:
            if block.type == "text":
                logger.debug("Model text: %s", block.text)
            if block.type == "server_tool_use":
                logger.info("Server tool call : %s(%s)", block.name, block.input)
            if block.type == "web_fetch_tool_result":
                logger.info("Web fetch result received")
            if block.type != "tool_use":
                continue
            logger.info("Tool call: %s(%s)", block.name, block.input)
            if block.name == "support_ticket_triage":
                result = TriageResult.model_validate(block.input)
                logger.info("Triage done after %d turn(s): %s", turn, result)
                return result
            if block.name == "lookup_customer":
                try:
                    customer = lookup_customer(block.input["customer_id"])
                    logger.info("Tool result: %s", customer)
                    tool_result.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": customer.model_dump_json(),
                        }
                    )
                except LookupError as e:
                    logger.warning("Tool error (lookup_customer): %s", e)
                    tool_result.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(e),
                            "is_error": True,
                        }
                    )
            elif block.name == "escalate_to_human":
                reason = block.input["reason"]
                # Gate: the escalation does not happen unless a human says yes.
                if approve(reason):
                    logger.info("Escalation approved by human")
                    content = escalate_to_human(reason)
                else:
                    logger.info("Escalation rejected by human")
                    content = (
                        "A human reviewed this escalation and rejected it. The ticket "
                        "was NOT escalated. Continue triaging it yourself."
                    )
                # Rejection is a normal observation, not an error: the loop goes on.
                tool_result.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": content}
                )
            else:
                logger.warning("Model called unknown tool: %s", block.name)
                tool_result.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Unknown tool: {block.name}",
                        "is_error": True,
                    }
                )
        if not tool_result:
            raise ValueError(
                f"Model stopped without triaging (stop_reason={response.stop_reason})"
            )
        messages.append({"role": "user", "content": tool_result})

    raise ValueError("Exceeded maximum number of turns without triaging")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    ticket = "I was charged twice, please refund"
    result = triage_ticket(ticket, client, TOOLS, customer_id="1001")
    print(result.model_dump_json())

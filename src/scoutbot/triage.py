import logging

from anthropic import Anthropic

from scoutbot.config import llms_settings
from scoutbot.schema import TriageResult
from scoutbot.tools import TOOLS, lookup_customer

logger = logging.getLogger(__name__)

client = Anthropic(api_key=llms_settings.anthropic_api_key.get_secret_value())

PROMPT_TEMPLATE = """You are a support ticket triage assistant.

Customer ID: {customer_id}
Ticket: {ticket}

Look up the customer first, then call support_ticket_triage with your decision.
Always finish by calling support_ticket_triage. Never ask questions."""


def triage_ticket(
    ticket: str,
    client: Anthropic,
    tools: list[dict],
    customer_id: str,
    max_turns: int = 5,
) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.
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

        tool_result = []
        for block in response.content:
            if block.type == "text":
                logger.debug("Model text: %s", block.text)
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

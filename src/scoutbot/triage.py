import logging
from typing import Callable

from anthropic import Anthropic
from pydantic import BaseModel
from scoutbot.schema import TriageResult
from scoutbot.tools import ToolHandlers, ask_human_approval, make_tool_result
from scoutbot.prompts import build_prompt
from scoutbot.utils import log_block

logger = logging.getLogger(__name__)

ESCALATION_REJECTED_MSG = (
    "A human reviewed this escalation and rejected it. The ticket "
    "was NOT escalated. Continue triaging it yourself."
)


def triage_ticket(
    ticket: str,
    client: Anthropic,
    model: str,
    tools: list[dict],
    handlers: ToolHandlers,
    customer_id: str,
    max_turns: int = 5,
    approve: Callable[[str], bool] = ask_human_approval,
) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.

    `handlers` maps each client tool name to the function that runs it.
    `approve` is asked before any escalate_to_human call takes effect; it gets the
    model's reason and returns True to approve, False to reject.
    """
    messages = [
        {
            "role": "user",
            "content": build_prompt(customer_id=customer_id, ticket=ticket),
        }
    ]

    logger.info("Triaging ticket for customer %s", customer_id)

    for turn in range(1, max_turns + 1):
        response = client.messages.create(
            model=model,
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
            log_block(block)
            if block.type != "tool_use":
                continue
            logger.info("Tool call: %s(%s)", block.name, block.input)
            if block.name == "support_ticket_triage":
                result = TriageResult.model_validate(block.input)
                logger.info("Triage done after %d turn(s): %s", turn, result)
                return result
            handler = handlers.get(block.name)
            if handler is None:
                logger.warning("Model called unknown tool: %s", block.name)
                tool_result.append(
                    make_tool_result(block.id, f"Unknown tool: {block.name}", is_error=True)
                )
                continue
            # Gate: the escalation does not happen unless a human says yes.
            # Rejection is a normal observation, not an error: the loop goes on.
            if block.name == "escalate_to_human" and not approve(block.input["reason"]):
                logger.info("Escalation rejected by human")
                tool_result.append(make_tool_result(block.id, ESCALATION_REJECTED_MSG))
                continue
            try:
                output = handler(**block.input)
            except LookupError as e:
                logger.warning("Tool error (%s): %s", block.name, e)
                tool_result.append(make_tool_result(block.id, str(e), is_error=True))
                continue
            logger.info("Tool result: %s", output)
            content = output.model_dump_json() if isinstance(output, BaseModel) else str(output)
            tool_result.append(make_tool_result(block.id, content))
        if not tool_result:
            raise ValueError(
                f"Model stopped without triaging (stop_reason={response.stop_reason})"
            )
        messages.append({"role": "user", "content": tool_result})

    raise ValueError("Exceeded maximum number of turns without triaging")


# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
#     )
#     ticket = "I was charged twice, please refund"
#     result = triage_ticket(ticket, client, TOOLS, customer_id="1001")
#     print(result.model_dump_json())

import logging

from pydantic import BaseModel
from scoutbot.interfaces import LLMClient
from scoutbot.schema import TriageResult
from scoutbot.tools import ToolHandlers, make_tool_result
from scoutbot.prompts import build_prompt
from scoutbot.utils import log_block

logger = logging.getLogger(__name__)


def triage_ticket(
    ticket: str,
    client: LLMClient,
    tools: list[dict],
    handlers: ToolHandlers,
    customer_id: str,
    max_turns: int = 5,
) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.

    `handlers` maps each client tool name to the function that runs it.
    """
    messages = [
        {
            "role": "user",
            "content": build_prompt(customer_id=customer_id, ticket=ticket),
        }
    ]

    logger.info("Triaging ticket for customer %s", customer_id)

    for turn in range(1, max_turns + 1):
        response = client.send(messages, tools)
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


import logging
from scoutbot.interfaces import LLMClient, ToolHandlers, Toolset
from scoutbot.schema import TriageResult

logger = logging.getLogger(__name__)


def make_tool_result(tool_use_id: str, content: str, is_error: bool = False) -> dict:
    """Build the tool_result block that answers one tool_use block."""
    result = {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
    if is_error:
        result["is_error"] = True
    return result


def run_tool(block, handlers: ToolHandlers) -> dict:
    """Run the tool the model asked for and return the tool_result block to send back."""
    handler = handlers.get(block.name)
    if handler is None: # guard 1: unknown tool → leave
        logger.warning("Model called unknown tool: %s", block.name)
        return make_tool_result(block.id, f"Unknown tool: {block.name}", is_error=True)

    arguments = block.input  # e.g. {"customer_id": "1001"}
    try:
        content = handler(**arguments)  # → handler(customer_id="1001")
    except LookupError as e: # guard 2: tool failed → leave
        logger.warning("Tool error (%s): %s", block.name, e)
        return make_tool_result(block.id, str(e), is_error=True)

    logger.info("Tool result: %s", content)
    return make_tool_result(block.id, content)


def triage_ticket(
    prompt: str,
    client: LLMClient,
    toolset: Toolset,
    max_turns: int = 5,
) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.

    `prompt` is the full first user message (ticket and customer ID already filled in).
    `toolset` holds the tool definitions, their handlers, and the final tool's name.
    """
    messages = [{"role": "user", "content": prompt}]

    for turn in range(1, max_turns + 1):
        response = client.send(messages, toolset.definitions)
        logger.info("Turn %d/%d done", turn, max_turns)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "pause_turn":
            continue  # API paused mid server-tool work; resend so it resumes

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            logger.info("Tool call: %s(%s)", block.name, block.input)
            if block.name == toolset.final_tool_name:
                result = TriageResult.model_validate(block.input)
                logger.info("Triage done after %d turn(s): %s", turn, result)
                return result
            tool_results.append(run_tool(block, toolset.handlers))
        if not tool_results:
            raise ValueError(
                f"Model stopped without triaging (stop_reason={response.stop_reason})"
            )
        messages.append({"role": "user", "content": tool_results})

    raise ValueError("Exceeded maximum number of turns without triaging")


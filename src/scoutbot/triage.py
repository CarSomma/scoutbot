from anthropic import Anthropic

from scoutbot.config import llms_settings
from scoutbot.schema import TriageResult

client = Anthropic(
    api_key=llms_settings.anthropic_api_key.get_secret_value()
)  

triage_tool = {
    "name": "support_ticket_triage",
    "description": "Triages support tickets and suggests the appropriate owner, priority, and category.",
    "strict": True,
    "input_schema": TriageResult.model_json_schema(),
}


def triage_ticket(ticket: str, client: Anthropic, triage_tool: dict) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.
    """

    response = client.messages.create(
        model=llms_settings.anthropic_model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a support ticket triage assistant.
                  Triage the following ticket: {ticket}""",
            }
        ],
        tools=[triage_tool],
        tool_choice={"type": "auto"},
    )
    for i, block in enumerate(response.content):
        print(f"DEBUG block[{i}] type:", block.type)
        if block.type == "tool_use":
            print(f"DEBUG block[{i}] input:", block.input)
            return TriageResult.model_validate(block.input)

    # Placeholder logic for triaging
    raise ValueError(
        f"Model did not call the tool (stop_reason={response.stop_reason})"
    )


if __name__ == "__main__":
    ticket = "I was charged twice, please refund"
    result = triage_ticket(ticket, client, triage_tool)
    print(result.model_dump_json())

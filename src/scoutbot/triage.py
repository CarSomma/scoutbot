from scoutbot.schema import TriageResult
from scoutbot.config import llms_settings
from anthropic import Anthropic

client = Anthropic(api_key=llms_settings.anthropic_api_key.get_secret_value())

def triage_ticket(ticket: str) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.
    """

    response = client.messages.parse(
        model=llms_settings.anthropic_model,
        max_tokens=1024,
        messages = [{ "role": "user",
                "content": f"""You are a support ticket triage assistant.
                  Triage the following ticket: {ticket}"""}
        ],
        output_format=TriageResult
    )
    # Placeholder logic for triaging
    return response.parsed_output


# if __name__ == "__main__":
#     ticket = "Example support ticket"
#     result = triage_ticket(ticket)
#     print(result.model_dump_json())
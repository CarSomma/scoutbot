from scoutbot.schema import TriageResult
from scoutbot.config import llms_settings
from anthropic import Anthropic, APIRequest, APIResponse, CallNext
from typing import Any

# def logging_middleware(request: APIRequest, call_next: CallNext) -> APIResponse[Any]:
#     # Before the request
#     print(f"-> {request.method} {request.url}")

#     # Forward the request to the rest of the chain
#     response = call_next(request)

#     # After the request
#     print(f"<- {response.status_code}")

#     return response


#client = Anthropic(middleware=[logging_middleware])
client = Anthropic(api_key=llms_settings.anthropic_api_key.get_secret_value())#, middleware=[logging_middleware])

triage_tool = {
    "name": "support_ticket_triage",
    "description": "Triages support tickets and suggests the appropriate owner, priority, and category.",
    "strict" : True,
    "input_schema": TriageResult.model_json_schema()
}

def triage_ticket(ticket: str, client: Anthropic, triage_tool: dict) :
    """
    Triages a support ticket and returns the suggested owner, priority, and category.
    """

    response = client.messages.create(
        model=llms_settings.anthropic_model,
        max_tokens=1024,
        messages = [{ "role": "user",
                "content": f"""You are a support ticket triage assistant.
                  Triage the following ticket: {ticket}"""}
        ],
        tools=[triage_tool],
        tool_choice={"type":"auto"}

    )
    # Placeholder logic for triaging
    return response.content[0]


# if __name__ == "__main__":
#     ticket = "Example support ticket"
#     result = triage_ticket(ticket)
#     print(result.model_dump_json())
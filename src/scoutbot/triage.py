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
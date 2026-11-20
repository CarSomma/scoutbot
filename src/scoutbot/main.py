import logging
from scoutbot.config import LLMsSettings
from scoutbot.llm_client import AnthropicClient
from scoutbot.prompts import build_prompt
from scoutbot.repository import JsonCustomerRepository
from scoutbot.approval import ask_human_approval
from scoutbot.tools import TOOLS, make_tool_handlers
from scoutbot.triage import triage_ticket
from scoutbot.utils import load_tickets

TICKET_PATH = "data/sample_tickets.json"
CUSTOMERS_PATH = "data/mock_customers.json"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx2").setLevel(logging.WARNING)

    llms_settings = LLMsSettings()
    client = AnthropicClient(
        api_key=llms_settings.anthropic_api_key.get_secret_value(),
        model=llms_settings.anthropic_model,
    )
    customers = JsonCustomerRepository(CUSTOMERS_PATH)
    handlers = make_tool_handlers(customers, approve=ask_human_approval)

    print("Loading tickets from:", TICKET_PATH)
    tickets = load_tickets(TICKET_PATH, "scoutbot")
    for ticket in tickets:
        print("Ticket ID:", ticket["id"])
        print("Ticket Text:", ticket["text"])
        prompt = build_prompt(customer_id=ticket["customer_id"], ticket=ticket["text"])
        result = triage_ticket(prompt, client, TOOLS, handlers)
        print("Triage Result:", result.model_dump_json())


if __name__ == "__main__":
    main()

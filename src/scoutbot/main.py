from anthropic import Anthropic
import logging
from scoutbot.config import LLMsSettings
from scoutbot.tools import TOOLS
from scoutbot.triage import triage_ticket
from scoutbot.utils import load_tickets

TICKET_PATH = "data/sample_tickets.json"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx2").setLevel(logging.WARNING)

    llms_settings = LLMsSettings()
    client = Anthropic(api_key=llms_settings.anthropic_api_key.get_secret_value())
    
    print("Loading tickets from:", TICKET_PATH)
    tickets = load_tickets(TICKET_PATH, "scoutbot")
    for ticket in tickets:
        print("Ticket ID:", ticket["id"])
        print("Ticket Text:", ticket["text"])
        result = triage_ticket(
            ticket["text"], client, llms_settings.anthropic_model, TOOLS, customer_id=ticket["customer_id"]
        )
        print("Triage Result:", result.model_dump_json())


if __name__ == "__main__":
    main()

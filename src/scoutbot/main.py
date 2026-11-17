from scoutbot.tools import TRIAGE_TOOL
from scoutbot.triage import client, triage_ticket
from scoutbot.utils import load_tickets

TICKET_PATH = "data/sample_tickets.json"


def main() -> None:
    print("Loading tickets from:", TICKET_PATH)
    tickets = load_tickets(TICKET_PATH, "scoutbot")
    for ticket in tickets:
        print("Ticket ID:", ticket["id"])
        print("Ticket Text:", ticket["text"])
        result = triage_ticket(ticket["text"], client, TRIAGE_TOOL)
        print("Triage Result:", result.model_dump_json())


if __name__ == "__main__":
    main()

import json
from importlib.resources import files

TICKET_PATH = "data/sample_tickets.json"
def load_tickets(package: str, ticket_path: str) -> list[dict]:
    "Load tickets from the specified package and data path."
    text = files(package).joinpath(ticket_path).read_text()
    return json.loads(text)

def main() -> None:
    print("Loading tickets from:", TICKET_PATH)
    tickets = load_tickets("scoutbot", TICKET_PATH)
    for ticket in tickets:
        print("Ticket ID:", ticket['id'])
        print("Ticket Text:", ticket['text'])

if __name__ == "__main__":
    main()

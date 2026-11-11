import json
from pathlib import Path

def main() -> None:
    print("Hello from scoutbot!")
    print("Called from the main.py")
    print("Import json sample.")
    
    with open("src/data/sample_tickets.json") as f: # relative path from where i run the script
        tickets = json.load(f)
    print("Loaded tickets:", tickets)
    for ticket in tickets:
        print("Ticket ID:", ticket['id'])
        print("Ticket Text:", ticket['text'])

if __name__ == "__main__":
    main()

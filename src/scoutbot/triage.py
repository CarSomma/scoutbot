from schema import TriageResult

def triage_ticket(ticket: str) -> TriageResult:
    """
    Triages a support ticket and returns the suggested owner, priority, and category.
    """
    # Placeholder logic for triaging
    return TriageResult(
        suggested_owner="support_agent",
        priority="medium",
        category="technical"
    )   


if __name__ == "__main__":
    ticket = "Example support ticket"
    result = triage_ticket(ticket)
    print(result.model_dump_json())
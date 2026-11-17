"""Definitions of tools and their corresponding Python functions."""


from scoutbot.schema import TriageResult

TRIAGE_TOOL = {
    "name": "support_ticket_triage",
    "description": "Triages support tickets and suggests the appropriate owner, priority, and category.",
    "strict": True,
    "input_schema": TriageResult.model_json_schema(),
}
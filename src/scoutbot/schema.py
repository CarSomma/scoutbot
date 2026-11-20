"""Schema definitions for support ticket triage and customer lookup."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class TriageResult(BaseModel):
    "Represents the result of triaging a support ticket."

    model_config = ConfigDict(
        extra="forbid"
    )  # adds additionalProperties: false (required by strict tools)

    priority: Literal["low", "medium", "high"]
    category: Literal["billing", "technical", "account", "other"]
    suggested_owner: Literal[
        "billing_team", "engineering_support", "account_management", "general_support"
    ]


class LookupCustomerInput(BaseModel):
    "What the model sends: how to identify the customer."

    model_config = ConfigDict(extra="forbid")

    customer_id: str


class EscalateInput(BaseModel):
    "What the model sends when it wants a human to take over the ticket."

    model_config = ConfigDict(extra="forbid")

    reason: str


class Customer(BaseModel):
    "What a customer repository's lookup() returns: data from your database."

    customer_id: str
    plan: Literal["free", "pro", "enterprise"]
    account_age_days: int
    past_refunds_90d: int


# if __name__ == "__main__":
#     result = TriageResult(priority="high", category="technical", suggested_owner="engineering_support")
#     print(result.model_dump_json())

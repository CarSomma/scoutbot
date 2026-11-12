from pydantic import BaseModel
from typing import Literal


class TriageResult(BaseModel):
    "Represents the result of triaging a support ticket."

    priority: Literal["low", "medium", "high"]
    category: Literal["billing", "technical", "account", "other"]
    suggested_owner: Literal["billing_team", "engineering_support", "account_management", "general_support"]

# if __name__ == "__main__":
#     result = TriageResult(priority="high", category="technical", suggested_owner="engineering_support")
#     print(result.model_dump_json())
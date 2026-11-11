from pydantic import BaseModel
from typing import Literal


class TriageResult(BaseModel):
    "Represents the result of triaging a support ticket."

    suggested_owner: str
    priority: str | Literal["low", "medium", "high"]
    category: Literal["billing", "technical", "account", "other"]


# if __name__ == "__main__":
#     result = TriageResult(priority="high", category="technical")
#     print(result.model_dump_json())
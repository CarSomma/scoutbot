"""Tests for the scoutbot schema."""

import pytest
from pydantic import ValidationError

from scoutbot.schema import TriageResult


def test_good_values_are_accepted():
    """A ticket with valid values from the Literal lists is accepted and stored unchanged.

    Passes if no error is raised and every field keeps the value we gave it.
    """
    # 1. prepare test data
    #  -> values copied straight from the Literal lists
    #  so they MUST be valid
    data = {
        "priority": "high",
        "category": "billing",
        "suggested_owner": "billing_team",
    }

    # 2. run  the code under test
    result = TriageResult(**data)

    # 3. check the result
    assert result.priority == "high"
    assert result.category == "billing"
    assert result.suggested_owner == "billing_team"


VALID = {"priority": "high", "category": "billing", "suggested_owner": "billing_team"}


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("priority", "High"),  # almost right: capital letter
        ("priority", " high"),  # almost right: space
        ("priority", ""),  # nothing
        ("priority", None),  # wrong type
        ("priority", 3),  # wrong type
        ("category", "shipping"),  # not on the list
        ("suggested_owner", "ceo"),  # not on the list
    ],
)
def test_bad_values_are_rejected(field, bad_value):
    """Passes if TriageResult raises a ValidationError for a bad value.

    pytest runs this test once for each row in the list above.
    Each run starts from a valid ticket and swaps in one bad value.
    """
    data = dict(VALID)  # copy of a valid ticket
    data[field] = bad_value  # break exactly ONE field
    with pytest.raises(ValidationError):
        TriageResult(**data)

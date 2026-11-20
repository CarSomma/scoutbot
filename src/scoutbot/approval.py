"""Ways for a human to approve or reject an escalation."""


def ask_human_approval(reason: str) -> bool:
    """Ask the operator on the terminal to approve an escalation (y/n).

    Anything other than an explicit yes, including no input at all, is a rejection.
    """
    try:
        answer = input(
            f"\nModel wants to escalate to a human.\nReason: {reason}\nApprove? [y/N] "
        )
    except EOFError:
        return False
    return answer.strip().lower() in {"y", "yes"}

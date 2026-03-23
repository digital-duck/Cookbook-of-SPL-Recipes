"""
tools.py — Human-in-the-loop approval stub
Dev mode: auto-approves immediately and prints the draft.
Production: replace request_approval() with email/Slack webhook logic.
"""


def request_approval(draft: str) -> str:
    """
    Dev mode approval gate — auto-approves after displaying the draft.
    Returns: 'approved' | 'revise' | 'rejected'
    """
    print("\n" + "="*60)
    print("APPROVAL REQUEST (dev mode — auto-approving)")
    print("="*60)
    print(draft)
    print("="*60)
    print("Decision: approved\n")
    return "approved"

"""
payment_rules.py — Governance rules for the agent economy.

Defines what agents can earn, what they can spend, and what requires
explicit approval. These rules are the social contract of the team's
micro-economy — enforced in code, visible to everyone.

Design principles:
  - Earn events are tied to real deliverables (not just activity)
  - Spend whitelist prevents arbitrary purchases
  - Approval gates ensure human oversight for significant amounts
  - All of this is enforced by treasury.py and logged by transparency_log.py

Adjusting rules:
  Edit this file to change the economy. Every change is visible in git history.
  There is no hidden configuration.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Earn events
# ---------------------------------------------------------------------------

EARN_EVENTS: Final[dict[str, int]] = {
    # Core delivery rewards
    "task_complete":          100,   # Standard task completed on spec
    "task_complete_early":    150,   # Delivered ahead of schedule
    "zero_bug_delivery":      250,   # Task shipped with no reported bugs
    "clean_architecture":     200,   # Code review rated "no changes needed"

    # Collaboration bonuses
    "team_reuse":             500,   # Built something reused by 2+ other agents
    "good_handoff":            50,   # Handoff received no clarification questions
    "unblocked_teammate":     100,   # Removed a blocker for another agent

    # Knowledge & improvement
    "lesson_documented":       75,   # Wrote a non-obvious lesson to lessons.md
    "skill_improved":         150,   # Measurably improved a skill used by the team
    "security_finding":       300,   # Found a real security issue before deployment

    # Research outcomes
    "winning_prediction":     500,   # Polymarket prediction resolved correct
    "high_confidence_research": 100, # Research delivered with >90% confidence score
    "competitive_intel":      200,   # Surfaced actionable intelligence on competitors

    # Special bonuses
    "exceptional_delivery":   750,   # Subjective: Jet decides when something is special
    "initiative":             250,   # Did something useful without being asked
    "cost_saving":            400,   # Found a way to reduce operational costs
}

# ---------------------------------------------------------------------------
# Spend whitelist
# ---------------------------------------------------------------------------

# Agents may only spend on whitelisted categories.
# Anything outside this list requires explicit Jet approval.
SPEND_WHITELIST: Final[list[str]] = [
    # Infrastructure & data
    "lightning-api-credits",       # LNBits-connected API services
    "domain-registration",         # New domain names for projects
    "data-feeds",                  # Market data, news feeds, research APIs
    "cloud-compute",               # Temporary compute (e.g. GPU for a job)
    "storage",                     # S3-compatible storage for project data

    # Agent-to-agent
    "internal-transfers",          # Paying another agent for specialised work
    "team-fund",                   # Contributing to shared team resources

    # Tools & research
    "research-subscription",       # One-time research service access
    "api-testing",                 # Testing paid APIs (small amounts)
    "tooling",                     # Software tools that improve productivity

    # Content & marketing
    "content-distribution",        # Paid distribution for content pieces
    "seo-tools",                   # SEO research and analysis tools
]

# ---------------------------------------------------------------------------
# Approval thresholds
# ---------------------------------------------------------------------------

# Spends below this amount: agent self-authorises (within weekly cap)
APPROVAL_REQUIRED_ABOVE_SATS: Final[int] = 5_000  # ~$5 USD at current rates

# Spends above this amount: require Michael's personal approval (not just Jet)
HUMAN_APPROVAL_REQUIRED_ABOVE_SATS: Final[int] = 50_000  # ~$50 USD

# ---------------------------------------------------------------------------
# Default spending caps (override per-agent in lightning-wallets.json)
# ---------------------------------------------------------------------------

DEFAULT_WEEKLY_CAP_SATS: Final[int] = 2_000    # Conservative default
TREASURY_WEEKLY_BUDGET_SATS: Final[int] = 50_000  # Total team budget per week

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_approved_spend_category(category: str) -> bool:
    """
    Return True if a spend category is on the whitelist.

    Args:
        category: The spend category to check.

    Returns:
        True if whitelisted, False if requires explicit approval.

    Example:
        >>> is_approved_spend_category("domain-registration")
        True
        >>> is_approved_spend_category("personal-shopping")
        False
    """
    return category in SPEND_WHITELIST


def get_earn_amount(event_name: str) -> int:
    """
    Return the satoshi reward for a named earn event.

    Args:
        event_name: Name of the earn event.

    Returns:
        Satoshi reward for the event.

    Raises:
        KeyError: If event_name is not defined.

    Example:
        >>> get_earn_amount("zero_bug_delivery")
        250
    """
    if event_name not in EARN_EVENTS:
        raise KeyError(
            f"Unknown earn event '{event_name}'. "
            f"Defined events: {', '.join(sorted(EARN_EVENTS.keys()))}"
        )
    return EARN_EVENTS[event_name]


def requires_approval(amount_sats: int) -> tuple[bool, str]:
    """
    Return whether a spend amount requires approval, and from whom.

    Args:
        amount_sats: Proposed spend amount.

    Returns:
        Tuple of (requires_approval: bool, approver: str).
        approver is "none", "jet", or "michael".

    Example:
        >>> requires_approval(100)
        (False, "none")
        >>> requires_approval(6000)
        (True, "jet")
        >>> requires_approval(60000)
        (True, "michael")
    """
    if amount_sats >= HUMAN_APPROVAL_REQUIRED_ABOVE_SATS:
        return True, "michael"
    if amount_sats >= APPROVAL_REQUIRED_ABOVE_SATS:
        return True, "jet"
    return False, "none"


def summarise_rules() -> str:
    """
    Return a human-readable summary of the payment rules.

    Useful for agents to quickly understand the economy without reading code.
    """
    lines = [
        "=== Agent Economy Rules ===",
        "",
        f"EARN EVENTS ({len(EARN_EVENTS)} defined):",
    ]
    for event, amount in sorted(EARN_EVENTS.items(), key=lambda x: -x[1]):
        lines.append(f"  {event:<30} {amount:>6} sats")

    lines += [
        "",
        f"SPEND WHITELIST ({len(SPEND_WHITELIST)} categories):",
    ]
    for category in sorted(SPEND_WHITELIST):
        lines.append(f"  - {category}")

    lines += [
        "",
        "APPROVAL GATES:",
        f"  < {APPROVAL_REQUIRED_ABOVE_SATS:,} sats  → self-authorise (within weekly cap)",
        f"  ≥ {APPROVAL_REQUIRED_ABOVE_SATS:,} sats  → Jet approval required",
        f"  ≥ {HUMAN_APPROVAL_REQUIRED_ABOVE_SATS:,} sats → Michael approval required",
        "",
        f"DEFAULT WEEKLY CAP:    {DEFAULT_WEEKLY_CAP_SATS:,} sats / agent",
        f"TREASURY WEEKLY BUDGET: {TREASURY_WEEKLY_BUDGET_SATS:,} sats total",
    ]
    return "\n".join(lines)

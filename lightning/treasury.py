"""
treasury.py — Jet's treasury management module.

Jet controls the team's fund pool. This module handles:
  - Distributing earnings to agents (funding their wallets)
  - Enforcing per-agent weekly spending caps
  - Weekly budget resets
  - Full logging of every satoshi moved

Why does Jet control the treasury?
  Jet is the team lead — all major financial decisions flow through her.
  Individual agents cannot self-authorise large transfers. This mirrors
  a real-world setup where a team lead approves budget allocations.

  Michael can audit everything via transparency_log.py at any time.

Flow:
    Polymarket win → sats → treasury wallet
    Treasury → fund_agent("forge", 500, "task_complete") → Forge's wallet
    Forge → spends on approved services (with Jet approval for large amounts)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .agent_wallets import get_wallet_config, get_all_wallets, AgentWalletConfig
from .wallet_manager import WalletManager, WalletBalance
from .transparency_log import TransparencyLog, TransactionRecord

logger = logging.getLogger(__name__)

# Path to the weekly cap tracking file
_WEEKLY_STATE_PATH = Path(__file__).parent / "weekly_state.json"

# Path to transaction log
_TRANSACTION_LOG_PATH = Path(__file__).parent / "transactions.log"


# ---------------------------------------------------------------------------
# Weekly spending tracker
# ---------------------------------------------------------------------------

@dataclass
class WeeklyState:
    """
    Tracks how much each agent has spent this week.

    Resets every Monday at midnight UTC.
    """
    week_start_timestamp: int       # Unix timestamp of Monday 00:00 UTC
    spent_this_week: dict[str, int] # agent_id → sats spent

    @classmethod
    def load(cls) -> "WeeklyState":
        """Load state from disk, or create a fresh one for this week."""
        current_week_start = cls._current_week_start()
        if _WEEKLY_STATE_PATH.exists():
            with open(_WEEKLY_STATE_PATH) as f:
                data = json.load(f)
            # If the stored week is stale, reset
            if data.get("week_start_timestamp") == current_week_start:
                return cls(
                    week_start_timestamp=current_week_start,
                    spent_this_week=data.get("spent_this_week", {}),
                )
        # New week or no state — start fresh
        return cls(
            week_start_timestamp=current_week_start,
            spent_this_week={},
        )

    def save(self) -> None:
        """Persist state to disk."""
        with open(_WEEKLY_STATE_PATH, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def record_spend(self, agent_id: str, amount_sats: int) -> None:
        """Record a spend event for an agent."""
        current = self.spent_this_week.get(agent_id, 0)
        self.spent_this_week[agent_id] = current + amount_sats
        self.save()

    def get_spent(self, agent_id: str) -> int:
        """Return how many sats an agent has spent this week."""
        return self.spent_this_week.get(agent_id, 0)

    def get_remaining(self, agent_id: str, weekly_cap: int) -> int:
        """Return how many sats an agent has remaining in their weekly cap."""
        return max(0, weekly_cap - self.get_spent(agent_id))

    @staticmethod
    def _current_week_start() -> int:
        """Return Unix timestamp of most recent Monday at 00:00 UTC."""
        now = datetime.utcnow()
        monday = now - timedelta(days=now.weekday())
        week_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(week_start.timestamp())


# ---------------------------------------------------------------------------
# Treasury
# ---------------------------------------------------------------------------

class Treasury:
    """
    Jet's treasury — the central fund distribution hub.

    All significant fund movements in the team pass through here.
    The treasury holds the master admin key and can push sats to any
    agent wallet. Agents cannot pull from the treasury directly.

    Args:
        treasury_agent_id: Agent ID of the treasury holder (default: "jet").
        log_path:          Path for the transaction log file.

    Example:
        treasury = Treasury()

        # See everyone's balance
        balances = treasury.get_team_balances()
        for agent, balance in balances.items():
            print(f"{agent}: {balance.balance_sats} sats")

        # Fund an agent for completing a task
        treasury.fund_agent("forge", amount_sats=500, reason="task_complete")

        # Reset weekly budgets (run every Monday)
        treasury.weekly_budget_reset()
    """

    def __init__(
        self,
        treasury_agent_id: str = "jet",
        log_path: Optional[Path] = None,
    ) -> None:
        self.treasury_agent_id = treasury_agent_id
        self._log_path = log_path or _TRANSACTION_LOG_PATH
        self._transparency_log = TransparencyLog(log_path=self._log_path)

        # Load treasury wallet config
        self._treasury_config = get_wallet_config(treasury_agent_id)
        if not self._treasury_config.is_treasury:
            logger.warning(
                "Agent '%s' is not marked as treasury in config. "
                "Fund operations may fail.",
                treasury_agent_id,
            )

        # Wallet manager for the treasury — needs admin key
        self._treasury_wallet = WalletManager(
            agent_id=treasury_agent_id,
            admin_key=self._treasury_config.admin_key,
            invoice_key=self._treasury_config.invoice_key,
        )

    # ------------------------------------------------------------------
    # Fund distribution
    # ------------------------------------------------------------------

    def fund_agent(
        self,
        agent_id: str,
        amount_sats: int,
        reason: str,
        approved_by: str = "jet",
    ) -> dict:
        """
        Transfer sats from treasury to an agent's wallet.

        Creates an invoice on the agent's wallet, then pays it from the
        treasury. This is the standard way to reward agents for completed
        tasks, good delivery, or bonus events defined in payment_rules.py.

        Args:
            agent_id:    Target agent to fund.
            amount_sats: Amount in satoshis to transfer.
            reason:      Human-readable reason (logged in audit trail).
                         Should match an EARN_EVENTS key where possible.
            approved_by: Who authorised this transfer (default: "jet").

        Returns:
            Dict with payment_hash and transfer details.

        Raises:
            KeyError:        If agent_id is not in the wallet registry.
            PermissionError: If treasury lacks admin_key.
            ValueError:      If amount_sats <= 0.
        """
        if amount_sats <= 0:
            raise ValueError(f"amount_sats must be positive, got {amount_sats}")

        logger.info(
            "Treasury funding agent=%s amount=%d sats reason=%r",
            agent_id, amount_sats, reason,
        )

        # Get the recipient agent's wallet (invoice-only is fine — we just create invoice)
        agent_config = get_wallet_config(agent_id)
        agent_wallet = WalletManager(
            agent_id=agent_id,
            invoice_key=agent_config.invoice_key,
        )

        # Step 1: Agent wallet creates a receive invoice
        memo = f"Treasury → {agent_id}: {reason}"
        invoice = agent_wallet.create_invoice(amount_sats=amount_sats, memo=memo)
        logger.debug("Created invoice for agent=%s: %s", agent_id, invoice)

        # Step 2: Treasury pays the invoice
        payment_result = self._treasury_wallet.pay_invoice(invoice.payment_request)

        # Step 3: Log the transaction for transparency
        record = TransactionRecord(
            timestamp=int(time.time()),
            from_agent=self.treasury_agent_id,
            to_agent=agent_id,
            amount_sats=amount_sats,
            reason=reason,
            payment_hash=payment_result.get("payment_hash", ""),
            approved_by=approved_by,
            tx_type="fund",
        )
        self._transparency_log.append_transaction(record)

        logger.info(
            "Funded agent=%s with %d sats (hash=%s)",
            agent_id, amount_sats, payment_result.get("payment_hash", ""),
        )
        return {
            "success": True,
            "agent_id": agent_id,
            "amount_sats": amount_sats,
            "reason": reason,
            "payment_hash": payment_result.get("payment_hash", ""),
        }

    def reward_earn_event(
        self,
        agent_id: str,
        event_name: str,
        multiplier: float = 1.0,
    ) -> dict:
        """
        Reward an agent for a named earn event (defined in payment_rules.py).

        Args:
            agent_id:   The agent who earned the reward.
            event_name: Name of the earn event (must be in EARN_EVENTS).
            multiplier: Optional multiplier for exceptional performance.

        Returns:
            Fund result dict from fund_agent().

        Raises:
            KeyError: If event_name is not in EARN_EVENTS.
        """
        from .payment_rules import EARN_EVENTS
        if event_name not in EARN_EVENTS:
            raise KeyError(
                f"Unknown earn event '{event_name}'. "
                f"Valid events: {', '.join(EARN_EVENTS.keys())}"
            )
        base_amount = EARN_EVENTS[event_name]
        amount_sats = int(base_amount * multiplier)
        logger.info(
            "Earn event: agent=%s event=%s amount=%d sats (×%.1f)",
            agent_id, event_name, amount_sats, multiplier,
        )
        return self.fund_agent(
            agent_id=agent_id,
            amount_sats=amount_sats,
            reason=event_name,
            approved_by="jet",
        )

    # ------------------------------------------------------------------
    # Balance visibility
    # ------------------------------------------------------------------

    def get_treasury_balance(self) -> WalletBalance:
        """Return the current treasury balance."""
        return self._treasury_wallet.get_balance()

    def get_team_balances(self) -> dict[str, WalletBalance]:
        """
        Return balances for all configured agent wallets.

        Note: This requires each agent's invoice_key to be set in the
        environment. Missing keys are skipped with a warning.

        Returns:
            Dict mapping agent_id → WalletBalance.
        """
        all_wallets = get_all_wallets()
        balances: dict[str, WalletBalance] = {}

        for agent_id, config in all_wallets.items():
            try:
                wallet = WalletManager(
                    agent_id=agent_id,
                    invoice_key=config.invoice_key,
                    admin_key=config.admin_key,
                )
                balances[agent_id] = wallet.get_balance()
            except (ValueError, Exception) as exc:
                logger.warning(
                    "Could not fetch balance for agent=%s: %s", agent_id, exc
                )

        return balances

    def get_team_summary(self) -> dict:
        """
        Return a summary of the team's financial state.

        Returns:
            Dict with treasury balance, agent balances, and weekly spend.
        """
        weekly_state = WeeklyState.load()
        all_wallets = get_all_wallets()

        summary: dict = {
            "treasury_balance_sats": None,
            "agents": {},
            "week_start": datetime.utcfromtimestamp(
                weekly_state.week_start_timestamp
            ).isoformat() + "Z",
        }

        try:
            treasury_balance = self.get_treasury_balance()
            summary["treasury_balance_sats"] = treasury_balance.balance_sats
        except Exception as exc:
            logger.warning("Could not fetch treasury balance: %s", exc)

        for agent_id, config in all_wallets.items():
            if config.is_treasury:
                continue
            summary["agents"][agent_id] = {
                "weekly_cap_sats": config.weekly_cap_sats,
                "spent_this_week_sats": weekly_state.get_spent(agent_id),
                "remaining_this_week_sats": weekly_state.get_remaining(
                    agent_id, config.weekly_cap_sats
                ),
            }

        return summary

    # ------------------------------------------------------------------
    # Budget management
    # ------------------------------------------------------------------

    def check_spending_cap(self, agent_id: str, proposed_amount_sats: int) -> bool:
        """
        Check if a proposed spend is within the agent's weekly cap.

        Args:
            agent_id:             Agent requesting to spend.
            proposed_amount_sats: Amount they want to spend.

        Returns:
            True if the spend is within cap, False if it would exceed it.
        """
        config = get_wallet_config(agent_id)
        weekly_state = WeeklyState.load()
        remaining = weekly_state.get_remaining(agent_id, config.weekly_cap_sats)

        if proposed_amount_sats > remaining:
            logger.warning(
                "Spend cap exceeded for agent=%s: proposed=%d sats, remaining=%d sats",
                agent_id, proposed_amount_sats, remaining,
            )
            return False
        return True

    def record_agent_spend(
        self,
        agent_id: str,
        amount_sats: int,
        reason: str,
        approved_by: Optional[str] = None,
    ) -> None:
        """
        Record a spend event for an agent (updates weekly cap tracker).

        Should be called whenever an agent spends from their wallet.

        Args:
            agent_id:    The spending agent.
            amount_sats: Amount spent in satoshis.
            reason:      What was purchased (must be in SPEND_WHITELIST or approved).
            approved_by: Who approved the spend (required above threshold).
        """
        from .payment_rules import APPROVAL_REQUIRED_ABOVE_SATS
        if amount_sats >= APPROVAL_REQUIRED_ABOVE_SATS and not approved_by:
            raise PermissionError(
                f"Spends of {APPROVAL_REQUIRED_ABOVE_SATS}+ sats require approval. "
                f"Set approved_by='jet' after Jet has reviewed this spend."
            )

        weekly_state = WeeklyState.load()
        weekly_state.record_spend(agent_id, amount_sats)

        record = TransactionRecord(
            timestamp=int(time.time()),
            from_agent=agent_id,
            to_agent="external",
            amount_sats=amount_sats,
            reason=reason,
            payment_hash="",
            approved_by=approved_by or "self",
            tx_type="spend",
        )
        self._transparency_log.append_transaction(record)
        logger.info("Spend recorded: agent=%s %d sats for %r", agent_id, amount_sats, reason)

    def weekly_budget_reset(self, force: bool = False) -> dict:
        """
        Reset all weekly spending caps. Normally auto-triggered on Monday.

        Args:
            force: If True, force a reset even if it's not Monday.

        Returns:
            Dict summarising the reset (previous spend amounts archived).
        """
        state = WeeklyState.load()
        current_week_start = WeeklyState._current_week_start()

        if not force and state.week_start_timestamp == current_week_start:
            return {
                "reset": False,
                "reason": "Already reset this week",
                "week_start": datetime.utcfromtimestamp(current_week_start).isoformat() + "Z",
            }

        # Archive the previous week's state
        previous_spend = dict(state.spent_this_week)

        # Create fresh state
        new_state = WeeklyState(
            week_start_timestamp=current_week_start,
            spent_this_week={},
        )
        new_state.save()

        logger.info(
            "Weekly budget reset. Previous week spend: %s",
            previous_spend,
        )
        return {
            "reset": True,
            "week_start": datetime.utcfromtimestamp(current_week_start).isoformat() + "Z",
            "archived_spend": previous_spend,
        }

    def __repr__(self) -> str:
        return f"Treasury(treasury_agent={self.treasury_agent_id!r})"

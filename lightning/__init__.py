"""
lightning — Agent wallet system built on LNBits.

This package provides economic infrastructure for multi-agent AI teams:
  - Per-agent Lightning wallets with configurable spending caps
  - Treasury management (fund distribution, weekly resets)
  - Transparent audit trail (every satoshi accounted for)
  - Governance rules (earn events, spend whitelist, approval gates)

Quick start:
    from lightning import WalletManager, Treasury, TransparencyLog

    wallet = WalletManager(agent_id="forge")
    balance = wallet.get_balance()

    treasury = Treasury()
    treasury.fund_agent("forge", amount_sats=500, reason="task_complete")

See lightning/README.md for full setup instructions.
"""

from .wallet_manager import WalletManager
from .treasury import Treasury
from .transparency_log import TransparencyLog
from .payment_rules import EARN_EVENTS, SPEND_WHITELIST, APPROVAL_REQUIRED_ABOVE_SATS
from .agent_wallets import AGENT_WALLETS, get_wallet_config

__all__ = [
    "WalletManager",
    "Treasury",
    "TransparencyLog",
    "EARN_EVENTS",
    "SPEND_WHITELIST",
    "APPROVAL_REQUIRED_ABOVE_SATS",
    "AGENT_WALLETS",
    "get_wallet_config",
]

__version__ = "0.1.0"

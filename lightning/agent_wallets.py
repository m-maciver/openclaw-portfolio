"""
agent_wallets.py — Agent wallet registry.

Maps each agent in the team to their LNBits wallet configuration.
Wallet IDs are not sensitive (they're just identifiers within a private
LNBits instance) — so they live in a JSON config file, not env vars.

Keys ARE sensitive and live in environment variables. See .env.example.

Configuration:
    Copy config/lightning-wallets.example.json → config/lightning-wallets.json
    and fill in your real wallet IDs from your LNBits instance.

    Wallet IDs are found in LNBits under:
    Wallet → Manage Wallets → [wallet name] → Wallet ID
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Path to wallet config — relative to repo root
_CONFIG_PATH = Path(__file__).parent.parent / "config" / "lightning-wallets.json"
_CONFIG_EXAMPLE_PATH = Path(__file__).parent.parent / "config" / "lightning-wallets.example.json"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AgentWalletConfig:
    """
    Wallet configuration for a single agent.

    Attributes:
        agent_id:           Unique agent identifier (e.g. "forge").
        wallet_id:          LNBits wallet ID (not sensitive).
        invoice_key_env:    Env var name that holds the invoice key.
        admin_key_env:      Env var name that holds the admin key (None for
                            non-treasury agents — they can't spend unilaterally).
        weekly_cap_sats:    Maximum satoshis this agent can spend per week.
        is_treasury:        If True, this is the fund distribution wallet (Jet).
        description:        Human-readable description of this agent's role.
    """
    agent_id: str
    wallet_id: str
    invoice_key_env: str
    admin_key_env: Optional[str]
    weekly_cap_sats: int
    is_treasury: bool = False
    description: str = ""

    @property
    def invoice_key(self) -> Optional[str]:
        """Load invoice key from environment."""
        return os.getenv(self.invoice_key_env)

    @property
    def admin_key(self) -> Optional[str]:
        """Load admin key from environment. None if not configured."""
        if self.admin_key_env is None:
            return None
        return os.getenv(self.admin_key_env)

    def has_spend_capability(self) -> bool:
        """Return True if admin key is available (can spend)."""
        return self.admin_key is not None

    def __repr__(self) -> str:
        spend = "spend-capable" if self.has_spend_capability() else "invoice-only"
        return (
            f"AgentWalletConfig(agent={self.agent_id!r}, "
            f"wallet_id={self.wallet_id!r}, cap={self.weekly_cap_sats} sats, {spend})"
        )


# ---------------------------------------------------------------------------
# Registry loader
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    """
    Load wallet config from JSON file.

    Tries lightning-wallets.json first (real config), falls back to the
    example file for demonstration purposes.
    """
    if _CONFIG_PATH.exists():
        logger.debug("Loading wallet config from %s", _CONFIG_PATH)
        with open(_CONFIG_PATH) as f:
            return json.load(f)

    if _CONFIG_EXAMPLE_PATH.exists():
        logger.warning(
            "No lightning-wallets.json found — using example config. "
            "Copy config/lightning-wallets.example.json → config/lightning-wallets.json "
            "and fill in your real wallet IDs."
        )
        with open(_CONFIG_EXAMPLE_PATH) as f:
            return json.load(f)

    raise FileNotFoundError(
        "No wallet config found. Expected one of:\n"
        f"  {_CONFIG_PATH}\n"
        f"  {_CONFIG_EXAMPLE_PATH}\n"
        "See lightning/README.md for setup instructions."
    )


def _build_registry(config: dict) -> dict[str, AgentWalletConfig]:
    """
    Parse the config dict into a registry of AgentWalletConfig objects.

    Config schema (see config/lightning-wallets.example.json):
    {
        "treasury": {
            "agent": "jet",
            "wallet_id": "...",
            "weekly_budget_sats": 50000
        },
        "agents": {
            "forge": {"wallet_id": "...", "weekly_cap_sats": 5000},
            ...
        }
    }
    """
    registry: dict[str, AgentWalletConfig] = {}

    # Treasury (Jet) — has admin key for distributing funds
    treasury_cfg = config.get("treasury", {})
    treasury_agent_id = treasury_cfg.get("agent", "jet")
    registry[treasury_agent_id] = AgentWalletConfig(
        agent_id=treasury_agent_id,
        wallet_id=treasury_cfg.get("wallet_id", "YOUR_TREASURY_WALLET_ID"),
        invoice_key_env="LNBITS_TREASURY_INVOICE_KEY",
        admin_key_env="LNBITS_TREASURY_ADMIN_KEY",
        weekly_cap_sats=treasury_cfg.get("weekly_budget_sats", 50000),
        is_treasury=True,
        description="Team treasury — controls fund distribution to all agents.",
    )

    # Per-agent wallets — invoice key only (can receive, cannot spend unilaterally)
    for agent_id, agent_cfg in config.get("agents", {}).items():
        agent_upper = agent_id.upper()
        registry[agent_id] = AgentWalletConfig(
            agent_id=agent_id,
            wallet_id=agent_cfg.get("wallet_id", f"YOUR_{agent_upper}_WALLET_ID"),
            invoice_key_env=f"LNBITS_{agent_upper}_INVOICE_KEY",
            admin_key_env=None,  # agents do not self-spend
            weekly_cap_sats=agent_cfg.get("weekly_cap_sats", 1000),
            is_treasury=False,
            description=agent_cfg.get("description", f"{agent_id} agent wallet"),
        )

    return registry


# ---------------------------------------------------------------------------
# Module-level registry (lazy-loaded)
# ---------------------------------------------------------------------------

_registry: Optional[dict[str, AgentWalletConfig]] = None


def _get_registry() -> dict[str, AgentWalletConfig]:
    """Return the registry, building it on first access."""
    global _registry
    if _registry is None:
        config = _load_config()
        _registry = _build_registry(config)
    return _registry


def get_wallet_config(agent_id: str) -> AgentWalletConfig:
    """
    Return the wallet configuration for a given agent.

    Args:
        agent_id: Agent identifier (e.g. "forge", "jet").

    Returns:
        AgentWalletConfig for the agent.

    Raises:
        KeyError: If agent_id is not found in the config.
    """
    registry = _get_registry()
    if agent_id not in registry:
        available = ", ".join(sorted(registry.keys()))
        raise KeyError(
            f"Agent '{agent_id}' not found in wallet registry. "
            f"Available agents: {available}"
        )
    return registry[agent_id]


# Convenience export — the full registry dict
# Access via: from lightning.agent_wallets import AGENT_WALLETS
@property  # type: ignore[misc]
def AGENT_WALLETS() -> dict[str, AgentWalletConfig]:
    """The full agent wallet registry (lazy-loaded from config)."""
    return _get_registry()


# For direct import compatibility
def get_all_wallets() -> dict[str, AgentWalletConfig]:
    """Return all configured agent wallets."""
    return _get_registry()


# Module-level alias for simple import
try:
    AGENT_WALLETS = _get_registry()
except FileNotFoundError:
    # Config not present — provide empty registry with a helpful error on access
    AGENT_WALLETS = {}
    logger.warning(
        "Wallet config not found. Copy config/lightning-wallets.example.json "
        "→ config/lightning-wallets.json to enable wallet registry."
    )

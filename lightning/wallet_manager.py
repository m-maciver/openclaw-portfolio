"""
wallet_manager.py — LNBits API wrapper for agent wallets.

Wraps the LNBits HTTP API to provide per-agent wallet operations.
LNBits uses sub-wallets within a single node — each agent gets their
own wallet with separate keys, tracked independently.

Auth model:
  - invoice_key: Read-only. Can check balance and create receive invoices.
  - admin_key:   Spend-capable. Required to pay invoices. Only Jet (treasury)
                 holds admin keys for agent wallets; agents hold their own.

Configuration:
  Set LNBITS_BASE_URL in your environment (see .env.example).
  Keys are loaded per-agent from environment variables.
"""

from __future__ import annotations

import os
import time
import logging
from typing import Optional
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Invoice:
    """A Lightning Network payment request."""
    payment_hash: str
    payment_request: str  # bolt11 string (starts with "lnbc...")
    amount_sats: int
    memo: str
    expiry_seconds: int = 3600

    def __str__(self) -> str:
        return f"Invoice({self.amount_sats} sats, memo={self.memo!r})"


@dataclass
class Transaction:
    """A completed Lightning payment (inbound or outbound)."""
    payment_hash: str
    amount_sats: int      # positive = received, negative = sent
    fee_sats: int
    memo: str
    timestamp: int        # unix epoch
    is_pending: bool

    @property
    def direction(self) -> str:
        """Return 'received' or 'sent'."""
        return "received" if self.amount_sats > 0 else "sent"

    def __str__(self) -> str:
        return (
            f"Transaction({self.direction} {abs(self.amount_sats)} sats, "
            f"memo={self.memo!r}, pending={self.is_pending})"
        )


@dataclass
class WalletBalance:
    """Current wallet balance."""
    balance_sats: int
    wallet_id: str
    name: str

    def __str__(self) -> str:
        return f"WalletBalance({self.balance_sats} sats, wallet={self.wallet_id!r})"


# ---------------------------------------------------------------------------
# WalletManager
# ---------------------------------------------------------------------------

class WalletManager:
    """
    LNBits API wrapper for a single agent's wallet.

    Each agent has their own LNBits sub-wallet. This class provides a clean
    interface over the raw HTTP API, handling authentication, error handling,
    and response parsing.

    Args:
        agent_id:    Identifier for this agent (e.g. "forge", "scout").
        admin_key:   LNBits admin key — grants spend capability. If not
                     provided, falls back to the LNBITS_{AGENT}_ADMIN_KEY
                     environment variable. Leave None for read-only mode.
        invoice_key: LNBits invoice key — read-only access. Falls back to
                     LNBITS_{AGENT}_INVOICE_KEY env var.
        base_url:    LNBits instance URL. Falls back to LNBITS_BASE_URL env
                     var. Defaults to http://umbrel.local:3007.
        timeout:     HTTP request timeout in seconds.

    Example:
        # Read-only — check balance
        wallet = WalletManager(agent_id="forge")
        balance = wallet.get_balance()
        print(f"Forge has {balance.balance_sats} sats")

        # Create a receive invoice
        invoice = wallet.create_invoice(amount_sats=500, memo="task reward")
        print(invoice.payment_request)  # bolt11 string to share

        # Pay an invoice (requires admin_key)
        result = wallet.pay_invoice(bolt11="lnbc500n1...")
    """

    def __init__(
        self,
        agent_id: str,
        admin_key: Optional[str] = None,
        invoice_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.agent_id = agent_id.lower()
        self.base_url = (
            base_url
            or os.getenv("LNBITS_BASE_URL", "http://umbrel.local:3007")
        ).rstrip("/")
        self.timeout = timeout

        # Resolve keys: explicit arg → env var → None
        env_prefix = f"LNBITS_{self.agent_id.upper()}"
        self._admin_key = admin_key or os.getenv(f"{env_prefix}_ADMIN_KEY")
        self._invoice_key = invoice_key or os.getenv(f"{env_prefix}_INVOICE_KEY")

        if not self._invoice_key and not self._admin_key:
            raise ValueError(
                f"No LNBits keys found for agent '{self.agent_id}'. "
                f"Set {env_prefix}_INVOICE_KEY or {env_prefix}_ADMIN_KEY "
                f"in your environment (see .env.example)."
            )

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_headers(self, require_admin: bool = False) -> dict[str, str]:
        """
        Return appropriate auth headers for the request.

        LNBits uses a single header: X-Api-Key.
        We use admin_key when available and required; otherwise invoice_key.
        """
        if require_admin:
            if not self._admin_key:
                raise PermissionError(
                    f"Admin key required for agent '{self.agent_id}' but not set. "
                    f"Set LNBITS_{self.agent_id.upper()}_ADMIN_KEY in your environment."
                )
            return {"X-Api-Key": self._admin_key}
        key = self._admin_key or self._invoice_key
        return {"X-Api-Key": key}  # type: ignore[arg-type]

    def _get(self, path: str, require_admin: bool = False) -> dict:
        """Make an authenticated GET request to the LNBits API."""
        url = f"/api/v1/{path.lstrip('/')}"
        logger.debug("GET %s (agent=%s)", url, self.agent_id)
        response = self._client.get(url, headers=self._auth_headers(require_admin))
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: dict, require_admin: bool = False) -> dict:
        """Make an authenticated POST request to the LNBits API."""
        url = f"/api/v1/{path.lstrip('/')}"
        logger.debug("POST %s (agent=%s) payload=%s", url, self.agent_id, payload)
        response = self._client.post(
            url,
            json=payload,
            headers=self._auth_headers(require_admin),
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_balance(self) -> WalletBalance:
        """
        Return the current wallet balance.

        Uses invoice_key (read-only) — no admin access required.

        Returns:
            WalletBalance with balance in satoshis.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        data = self._get("wallet")
        # LNBits returns balance in millisats — convert to sats
        balance_sats = data.get("balance", 0) // 1000
        return WalletBalance(
            balance_sats=balance_sats,
            wallet_id=data.get("id", ""),
            name=data.get("name", self.agent_id),
        )

    def create_invoice(
        self,
        amount_sats: int,
        memo: str = "",
        expiry_seconds: int = 3600,
    ) -> Invoice:
        """
        Create a Lightning invoice (payment request) to receive funds.

        Args:
            amount_sats:    Amount in satoshis to request.
            memo:           Optional description attached to the invoice.
            expiry_seconds: How long the invoice is valid (default: 1 hour).

        Returns:
            Invoice containing the bolt11 payment_request string.

        Raises:
            ValueError: If amount_sats <= 0.
        """
        if amount_sats <= 0:
            raise ValueError(f"amount_sats must be positive, got {amount_sats}")

        payload = {
            "out": False,
            "amount": amount_sats,
            "memo": memo,
            "expiry": expiry_seconds,
        }
        data = self._post("payments", payload)
        return Invoice(
            payment_hash=data["payment_hash"],
            payment_request=data["payment_request"],
            amount_sats=amount_sats,
            memo=memo,
            expiry_seconds=expiry_seconds,
        )

    def pay_invoice(self, bolt11: str) -> dict:
        """
        Pay a Lightning invoice. Requires admin_key.

        This is a spend operation — agents should not call this directly
        unless authorised. Treasury operations go through treasury.py.

        Args:
            bolt11: The bolt11 payment request string (starts with "lnbc...").

        Returns:
            Dict with payment_hash and status from LNBits.

        Raises:
            PermissionError: If admin_key is not set.
            httpx.HTTPStatusError: If the payment fails.
        """
        if not bolt11.startswith("lnbc"):
            logger.warning(
                "pay_invoice called with unexpected bolt11 prefix for agent=%s",
                self.agent_id,
            )

        payload = {"out": True, "bolt11": bolt11}
        data = self._post("payments", payload, require_admin=True)
        logger.info(
            "Payment sent by agent=%s hash=%s",
            self.agent_id,
            data.get("payment_hash", "unknown"),
        )
        return data

    def get_transactions(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Transaction]:
        """
        Fetch recent transactions for this wallet.

        Args:
            limit:  Maximum number of transactions to return (default 50).
            offset: Pagination offset.

        Returns:
            List of Transaction objects, newest first.
        """
        data = self._get("payments")
        transactions = []
        for item in data[offset : offset + limit]:
            transactions.append(
                Transaction(
                    payment_hash=item.get("payment_hash", ""),
                    amount_sats=item.get("amount", 0) // 1000,  # msats → sats
                    fee_sats=item.get("fee", 0) // 1000,
                    memo=item.get("memo", ""),
                    timestamp=item.get("time", int(time.time())),
                    is_pending=item.get("pending", False),
                )
            )
        return transactions

    def check_invoice(self, payment_hash: str) -> dict:
        """
        Check if an invoice has been paid.

        Args:
            payment_hash: The payment_hash from a previously created invoice.

        Returns:
            Dict with 'paid' bool and 'preimage' if settled.
        """
        data = self._get(f"payments/{payment_hash}")
        return {
            "paid": data.get("paid", False),
            "preimage": data.get("preimage", ""),
            "details": data,
        }

    def __repr__(self) -> str:
        mode = "admin+invoice" if self._admin_key else "invoice-only"
        return f"WalletManager(agent={self.agent_id!r}, mode={mode!r}, base={self.base_url!r})"

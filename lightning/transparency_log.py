"""
transparency_log.py — Full audit trail for the agent economy.

Every satoshi movement is logged here. No hidden transactions.
Michael can read this file at any time to see exactly what happened,
who approved it, and why.

Format:
  Each transaction is one JSON line (newline-delimited JSON / NDJSON).
  Human-readable in any text editor, machine-readable for analysis.

  {"timestamp": 1709000000, "from": "jet", "to": "forge", "amount_sats": 500, ...}

Why NDJSON?
  - Appendable without reading/rewriting the whole file
  - Each line is valid JSON — grep, jq, Python all work on it
  - Crash-safe (each append is atomic at the OS level)
  - No size limit concerns
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_DEFAULT_LOG_PATH = Path(__file__).parent / "transactions.log"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class TransactionRecord:
    """
    A single transaction in the audit log.

    Attributes:
        timestamp:    Unix timestamp when the transaction occurred.
        from_agent:   Sender (agent_id or "external" for outside payments).
        to_agent:     Recipient (agent_id or "external" for outside payments).
        amount_sats:  Amount transferred in satoshis.
        reason:       Why the transfer happened (should match EARN_EVENTS key
                      or SPEND_WHITELIST category where applicable).
        payment_hash: Lightning payment hash (empty string if not a live payment).
        approved_by:  Who authorised this transaction ("jet", "michael", "self").
        tx_type:      Transaction type: "fund", "spend", "internal", "earn".
        notes:        Optional free-form notes.
    """
    timestamp: int
    from_agent: str
    to_agent: str
    amount_sats: int
    reason: str
    payment_hash: str
    approved_by: str
    tx_type: str        # "fund" | "spend" | "internal" | "earn"
    notes: str = ""

    @property
    def datetime_utc(self) -> str:
        """Return ISO 8601 timestamp string in UTC."""
        return datetime.utcfromtimestamp(self.timestamp).isoformat() + "Z"

    def to_log_line(self) -> str:
        """Serialise to a single JSON log line."""
        d = asdict(self)
        d["datetime_utc"] = self.datetime_utc  # add human-readable timestamp
        return json.dumps(d, separators=(",", ":"))

    @classmethod
    def from_log_line(cls, line: str) -> "TransactionRecord":
        """Parse a JSON log line back to a TransactionRecord."""
        d = json.loads(line.strip())
        d.pop("datetime_utc", None)  # computed field — strip before init
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def __str__(self) -> str:
        return (
            f"[{self.datetime_utc}] {self.tx_type.upper()}: "
            f"{self.from_agent} → {self.to_agent} "
            f"{self.amount_sats} sats ({self.reason}) "
            f"[approved_by={self.approved_by}]"
        )


# ---------------------------------------------------------------------------
# TransparencyLog
# ---------------------------------------------------------------------------

class TransparencyLog:
    """
    Append-only audit log for all agent economic activity.

    Stores transactions as newline-delimited JSON in a .log file.
    Provides query methods to inspect agent history and team summaries.

    Args:
        log_path: Path to the log file. Defaults to lightning/transactions.log.

    Example:
        log = TransparencyLog()

        # Append a transaction
        record = TransactionRecord(
            timestamp=int(time.time()),
            from_agent="jet",
            to_agent="forge",
            amount_sats=500,
            reason="task_complete",
            payment_hash="abc123...",
            approved_by="jet",
            tx_type="fund",
        )
        log.append_transaction(record)

        # Query history
        history = log.get_agent_history("forge")
        summary = log.get_team_summary()
    """

    def __init__(self, log_path: Optional[Path] = None) -> None:
        self.log_path = log_path or _DEFAULT_LOG_PATH
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def append_transaction(self, record: TransactionRecord) -> None:
        """
        Append a transaction record to the log.

        Thread-safe (each write is a single append). The log file is
        created if it doesn't exist.

        Args:
            record: TransactionRecord to append.
        """
        line = record.to_log_line()
        with open(self.log_path, "a") as f:
            f.write(line + "\n")
        logger.debug("Logged transaction: %s", record)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def _read_all(self) -> list[TransactionRecord]:
        """
        Read all records from the log file.

        Returns:
            List of TransactionRecord objects, oldest first.
        """
        if not self.log_path.exists():
            return []

        records = []
        with open(self.log_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(TransactionRecord.from_log_line(line))
                except (json.JSONDecodeError, TypeError, KeyError) as exc:
                    logger.warning(
                        "Could not parse log line %d in %s: %s",
                        line_num, self.log_path, exc,
                    )
        return records

    def get_agent_history(
        self,
        agent_id: str,
        tx_type: Optional[str] = None,
        since_timestamp: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[TransactionRecord]:
        """
        Return all transactions involving a specific agent.

        Args:
            agent_id:         Filter to transactions involving this agent.
            tx_type:          Optional filter: "fund", "spend", "earn", "internal".
            since_timestamp:  Only return transactions after this Unix timestamp.
            limit:            Maximum number of records to return (newest first).

        Returns:
            List of TransactionRecord, filtered and sorted newest-first.
        """
        records = self._read_all()
        results = []

        for record in records:
            if record.from_agent != agent_id and record.to_agent != agent_id:
                continue
            if tx_type is not None and record.tx_type != tx_type:
                continue
            if since_timestamp is not None and record.timestamp < since_timestamp:
                continue
            results.append(record)

        # Newest first
        results.sort(key=lambda r: r.timestamp, reverse=True)

        if limit is not None:
            results = results[:limit]

        return results

    def get_all_transactions(
        self,
        since_timestamp: Optional[int] = None,
        tx_type: Optional[str] = None,
    ) -> list[TransactionRecord]:
        """
        Return all transactions in the log.

        Args:
            since_timestamp: Only return transactions after this Unix timestamp.
            tx_type:         Optional type filter.

        Returns:
            List of TransactionRecord, newest first.
        """
        records = self._read_all()
        if since_timestamp is not None:
            records = [r for r in records if r.timestamp >= since_timestamp]
        if tx_type is not None:
            records = [r for r in records if r.tx_type == tx_type]
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records

    def get_team_summary(self) -> dict:
        """
        Return a financial summary for the entire team.

        Aggregates earned, spent, and net for each agent across all time.

        Returns:
            Dict with per-agent totals and overall team stats:
            {
                "agents": {
                    "forge": {
                        "total_earned_sats": 1500,
                        "total_spent_sats": 300,
                        "net_sats": 1200,
                        "transaction_count": 8,
                    },
                    ...
                },
                "team_total_earned_sats": 3200,
                "team_total_spent_sats": 800,
                "total_transactions": 22,
                "generated_at": "2024-02-25T12:00:00Z",
            }
        """
        records = self._read_all()

        earned: dict[str, int] = defaultdict(int)
        spent: dict[str, int] = defaultdict(int)
        count: dict[str, int] = defaultdict(int)

        for record in records:
            if record.tx_type in ("fund", "earn"):
                earned[record.to_agent] += record.amount_sats
                count[record.to_agent] += 1
            elif record.tx_type == "spend":
                spent[record.from_agent] += record.amount_sats
                count[record.from_agent] += 1
            elif record.tx_type == "internal":
                spent[record.from_agent] += record.amount_sats
                earned[record.to_agent] += record.amount_sats
                count[record.from_agent] += 1

        all_agents = set(earned.keys()) | set(spent.keys())
        agent_summaries = {}
        for agent_id in sorted(all_agents):
            agent_summaries[agent_id] = {
                "total_earned_sats": earned[agent_id],
                "total_spent_sats": spent[agent_id],
                "net_sats": earned[agent_id] - spent[agent_id],
                "transaction_count": count[agent_id],
            }

        return {
            "agents": agent_summaries,
            "team_total_earned_sats": sum(earned.values()),
            "team_total_spent_sats": sum(spent.values()),
            "total_transactions": len(records),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    def get_agent_net_sats(self, agent_id: str) -> int:
        """
        Return the net satoshi balance for an agent based on log history.

        Note: This is the log-based accounting view, not the on-chain
        LNBits balance. They should match — if they don't, investigate.

        Args:
            agent_id: Agent to calculate net for.

        Returns:
            Net satoshis (positive = more earned than spent).
        """
        history = self.get_agent_history(agent_id)
        net = 0
        for record in history:
            if record.to_agent == agent_id and record.tx_type in ("fund", "earn", "internal"):
                net += record.amount_sats
            elif record.from_agent == agent_id and record.tx_type in ("spend", "internal"):
                net -= record.amount_sats
        return net

    def print_recent(self, n: int = 20) -> None:
        """
        Print the N most recent transactions to stdout.

        Useful for quick inspection without grep.

        Args:
            n: Number of recent transactions to print.
        """
        records = self.get_all_transactions()[:n]
        if not records:
            print("No transactions logged yet.")
            return
        print(f"=== Last {min(n, len(records))} transactions ===")
        for record in records:
            print(f"  {record}")

    def __repr__(self) -> str:
        record_count = len(self._read_all())
        return f"TransparencyLog(path={self.log_path!r}, records={record_count})"

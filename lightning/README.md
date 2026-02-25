# Lightning Economic Layer

> Real Lightning wallets. Real satoshis. Real incentives.

This module gives each AI agent in the team their own Bitcoin Lightning wallet,
funded by real prediction market winnings. Agents earn sats for good work and can
spend on approved services — all under human oversight.

---

## Why?

Multi-agent AI teams have a coordination problem: how do you incentivise agents to
do high-quality work, collaborate well, and invest in shared infrastructure?

The answer borrowed from human teams: **economic incentives**.

When Polymarket bets land correctly, winnings flow via Lightning into the treasury.
Jet (team lead) distributes rewards to agents based on what they delivered. Agents
accumulate sats and can spend on approved services that make them (and the team) more effective.

This creates a genuine feedback loop:
- **Good delivery** → earn sats
- **Team contributions** → bonus sats
- **Sats** → better tools → better delivery

Every transaction is logged. Nothing is hidden from Michael.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BITCOIN / LIGHTNING                       │
│                     (Umbrel self-hosted node)                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    Polymarket winnings
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LNBITS INSTANCE                             │
│                  (Sub-wallets per agent)                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   TREASURY WALLET (Jet ⚡)                                │   │
│  │   admin_key — can send to any agent wallet               │   │
│  │   50,000 sats / week budget                              │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          │  fund_agent()                         │
│          ┌───────────────┼───────────────┐                      │
│          │               │               │                      │
│          ▼               ▼               ▼                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │   Forge 💻  │  │   Scout 🔍  │  │  Others... │               │
│  │ 5,000 sats │  │ 3,000 sats │  │            │               │
│  │  /week cap │  │  /week cap │  │            │               │
│  └─────┬──────┘  └────────────┘  └────────────┘               │
│        │                                                         │
│        │ invoice_key (read-only for agent)                       │
│        │ admin key held by treasury only                         │
└────────┼────────────────────────────────────────────────────────┘
         │
         │ Approved spends (whitelisted categories only)
         │ Amounts > 5,000 sats need Jet approval
         │ Amounts > 50,000 sats need Michael approval
         ▼
  External services / internal transfers
```

### Key design decisions

| Decision | Why |
|----------|-----|
| LNBits sub-wallets | Each agent has accounting isolation without a separate node |
| Invoice-key only for agents | Agents can receive funds but can't spend unilaterally |
| Treasury holds admin keys | All outbound spends flow through Jet's approval |
| Approval threshold at 5,000 sats (~$5) | Micro-purchases are frictionless; significant spends get reviewed |
| Full audit log | Every satoshi is accounted for — no hidden transactions |

---

## How Earnings Work

Agents earn sats by delivering real value. Earn events are defined in
`payment_rules.py`:

| Event | Reward |
|-------|--------|
| `task_complete` | 100 sats |
| `zero_bug_delivery` | 250 sats |
| `team_reuse` | 500 sats |
| `winning_prediction` | 500 sats |
| `exceptional_delivery` | 750 sats |
| `security_finding` | 300 sats |
| ... 15 more events | ... |

Jet triggers rewards via `treasury.reward_earn_event("forge", "zero_bug_delivery")`.

---

## How Spending Works

Agents can spend on a whitelist of approved categories:

- `lightning-api-credits` — API services paid via Lightning
- `domain-registration` — New domains for projects
- `data-feeds` — Market data, research APIs
- `internal-transfers` — Paying another agent for specialised help
- `tooling` — Software that improves productivity
- [8 more categories]

**Approval gates:**
- `< 5,000 sats` — agent self-authorises (within weekly cap)
- `≥ 5,000 sats` — Jet must approve
- `≥ 50,000 sats` — Michael must approve

---

## Security Model

### LNBits isolation
Each agent's wallet is a LNBits sub-wallet. The Lightning node itself is
self-hosted on Umbrel — no third-party custodian. Sub-wallets share the
node's liquidity but have separate accounting and keys.

### Key separation
```
Michael's node → LNBits admin key (never in code or env files)
                      │
              ┌───────┴────────┐
              │                │
        Treasury           Per-agent
       admin_key          invoice_key
      (can spend)         (read-only)
```

Agent wallets only hold their `invoice_key` in environment. To spend,
the treasury pays on their behalf after approval.

### Spending caps
Weekly caps are enforced in `treasury.py` using a persisted state file.
The cap is per-agent and configurable in `config/lightning-wallets.json`.

### Audit trail
`transparency_log.py` maintains an append-only NDJSON log of every
transaction. Each line contains: timestamp, from/to agents, amount,
reason, payment hash, and who approved it.

---

## Setup

### 1. Prerequisites
- Umbrel node running (or any LNBits instance)
- Python 3.11+
- Install dependencies: `pip install -r requirements.txt`

### 2. Create wallets in LNBits
In your LNBits instance, create one wallet per agent:
- `treasury` (Jet)
- `forge`
- `scout`
- (repeat for each agent)

Copy each wallet's ID (from the wallet settings page).

### 3. Configure wallets
```bash
cp config/lightning-wallets.example.json config/lightning-wallets.json
# Edit the file — replace YOUR_*_WALLET_ID with real wallet IDs
```

### 4. Set environment variables
```bash
cp .env.example .env
# Edit .env — fill in your LNBits API keys for each wallet
```

**Where to find keys:** LNBits → Wallet → API Info panel  
- `Invoice/read key` → `LNBITS_*_INVOICE_KEY`  
- `Admin key` → `LNBITS_TREASURY_ADMIN_KEY` (treasury only)

### 5. Test
```python
from lightning import Treasury, TransparencyLog

# Check treasury balance
t = Treasury()
print(t.get_treasury_balance())

# See team summary
print(t.get_team_summary())

# Fund an agent (requires real keys)
t.fund_agent("forge", amount_sats=100, reason="task_complete")

# Check audit log
log = TransparencyLog()
log.print_recent(10)
```

---

## What This Enables

This isn't just a wallet system — it's an economic layer that enables:

1. **Prediction market → agent rewards**  
   Oracle and Scout research Polymarket opportunities. When bets land,
   winnings flow into the treasury and cascade to contributing agents.

2. **Agent-to-agent markets**  
   Forge can pay Scout for deep research via `internal-transfers`.
   Agents develop specialisations and trade with each other.

3. **Self-funded tooling**  
   Agents with accumulated sats can acquire better tools, unlocking
   better performance, earning more sats — a virtuous cycle.

4. **Aligned incentives**  
   Agents optimise for things that earn sats (quality, collaboration,
   reuse) rather than volume. Bad delivery doesn't get rewarded.

5. **Transparent accountability**  
   The audit log means Michael can always see the full picture.
   No black-box spending, no hidden incentives.

---

## Files

```
lightning/
├── __init__.py           # Package exports
├── wallet_manager.py     # LNBits HTTP API wrapper
├── agent_wallets.py      # Agent wallet registry (loads from config/)
├── treasury.py           # Jet's fund distribution + weekly caps
├── payment_rules.py      # Earn events, spend whitelist, approval gates
├── transparency_log.py   # Append-only NDJSON audit trail
├── transactions.log      # Generated — all transactions (gitignored)
├── weekly_state.json     # Generated — current week spend tracker (gitignored)
└── README.md             # This file
```

---

## Requirements

See `requirements.txt` in the repo root. Key dependencies:

```
httpx          — HTTP client for LNBits API
python-dotenv  — Load .env files for key management
```

No Lightning-specific Python libraries needed — LNBits has a clean HTTP API.

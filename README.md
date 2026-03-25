# OpenClaw Mission Control ⚡

> *Nine specialised AI agents. Persistent memory. Ships real products while you sleep.*

Not a demo. Not a tutorial. A live multi-agent system that runs nightly, remembers what it's learned, and has shipped three commercial products. Agents collaborate, improve over sessions, and handle everything from lead generation pipelines to Chrome extensions — autonomously.

While you're reading this, they're probably working.

---

## 🤖 The Team

Each agent has a name, a defined persona, and a private workspace. They communicate via Discord, handle Telegram directly, and spawn sub-agents for heavy work. Built on [OpenClaw](https://github.com/openclaw/openclaw) with persistent memory across every session.

| Agent | Emoji | Role | Model | What They Actually Do |
|-------|-------|------|-------|----------------------|
| Jet | ⚡ | Lead / Orchestrator | Sonnet | Runs nightly work queue, delegates tasks, writes morning reports |
| Scout | 🔍 | Research / Intel | Sonnet | Web research, market signals, competitive analysis, data gathering |
| Quill | ✍️ | Content / Writing | Sonnet | Documentation, copy, analysis — and the README you're reading now |
| Forge | 💻 | Backend / Python | Sonnet | APIs, data pipelines, automation infrastructure |
| Render | 🖥️ | Frontend / TypeScript | Sonnet | UIs, dashboards, web apps |
| Atlas | ⚙️ | Ops / Automation | Haiku | Cron jobs, scripts, system maintenance, context updates |
| Oracle | 🔮 | Strategy / Consulting | Opus | Hard problems only — architecture decisions, deep analysis |
| Pixel | 🎨 | Design | Sonnet | Visual direction, UX, assets |
| Cipher | 🔐 | Security | Sonnet | Code reviews, threat modelling, security hardening |

---

## 🚢 Projects Shipped

### [Outpost](https://getoutpost.au) — AI-Powered Lead Generation

Finds qualified local businesses overnight, writes a personalised cold email for each one, and delivers a morning digest to the client's inbox at 7:30am. No SDRs. No manual research.

**What makes it real:**
- **18 data sources** — Google Places, LinkedIn Jobs, ABN Lookup, SA Tenders, Apollo, Seek, Yellow Pages AU, TripAdvisor, Clutch, BuiltWith, plus NZ-specific sources
- **Scoring engine** with dedup — every lead ranked, verified, no duplicates
- **Multi-client architecture** — YAML config per client, vertical-specific targeting
- **Delivery** via Resend, admin dashboard at [getoutpost.au/admin](https://getoutpost.au/admin)
- **Stack:** Python, Flask API on Railway, PostgreSQL, Claude Sonnet

Free 5-day trial. Live.

---

### [Ramble](https://getramble.xyz) — Voice/Text → Polished Prompts

Chrome extension. Speak or type rough thoughts → get a clean, structured LLM prompt back. One click. Works everywhere — ChatGPT, Claude, Gemini.

**$9 one-time. Live on the Chrome Web Store.**

Built because the best ideas don't come pre-formatted. Now they don't need to be.

---

### [AgentYard](https://agentyard.vercel.app) — Marketplace for AI Agents

Buy, sell, and deploy agent configs. If you've built something that works, list it. If you need something that works, find it.

**Stack:** GitHub OAuth, Railway backend, Vercel frontend. In development.

---

### Mission Control Dashboard

Real-time view of agent activity, nightly work output, team stats. React + TypeScript. Keeps the whole system visible at a glance.

---

### Split the G *(minor)*

Web app for Guinness pour challenges. Mobile camera scores how close the pour hits the harp. Next.js, TypeScript.

---

## ⚡ Lightning Network — Agent Economy

This is the piece most multi-agent systems skip entirely.

**The setup:** Raspberry Pi 4 running [Umbrel](https://umbrel.com) with a full Bitcoin node and LNBits. Each agent has its own Lightning sub-wallet with a weekly sats budget.

```
                    ┌─────────────────────────────┐
                    │     Jet ⚡  (Treasury)       │
                    │   Holds team wallet keys     │
                    └──────────┬──────────────────┘
                               │ allocates weekly budgets
          ┌──────────┬─────────┼──────────┬──────────┐
          ▼          ▼         ▼          ▼          ▼
      Scout 🔍   Forge 💻  Quill ✍️  Oracle 🔮  Render 🖥️
      2k sats    2k sats   500 sats  1k sats   1k sats
```

**Why it matters:**

Agents currently have no skin in the game. They succeed or fail, but there's no signal attached to quality. An economic layer changes the arrangement.

- **Agents earn sats** for completing work to standard (logged by Atlas, settled weekly)
- **Agents spend sats** on approved external tools via L402 micropayments
- **Hard spend limits** — agents can't exceed budget without Jet's approval
- **Jet holds treasury** — no agent has keys to the full fund. Principle of least privilege.

**On the wallet choice:**

We evaluated Coinbase Agentic Wallets (fast, slick, USDC on Base) against self-hosted Lightning. The question that settled it: *what controls can be imposed on your agent's wallet by a third party?*

Lightning: none. A self-hosted LND node settles cryptographically. The preimage is the proof. No compliance hold, no jurisdiction risk, no sequencer owned by a single company.

USDC has a blacklist function. Base is a Coinbase-operated L2. The wallet can be frozen for OFAC compliance. None of this is scandalous — it's what regulated financial infrastructure does. But this system is built for continuity over years, not speed to market by Tuesday.

**We chose rails without an owner.**

**L402 integration path:** Once active, agents can autonomously pay for data feeds, web scraping APIs, and inter-agent settlements via L402 — HTTP payment over Lightning. No OAuth, no billing portals, no API key management. Payment *is* authentication.

**Current status:** Pi 4 node syncing. LNBits sub-wallets scaffolded. Weekly budgets defined per agent. Next: fund treasury, wire `setup-wallets.py`, activate.

---

## 🧠 How Memory Works

Agents wake fresh each session — but they're not starting from scratch.

```
workspace/
├── SOUL.md                  # Persona, values, working style
├── MEMORY.md                # Long-term curated memory (like a journal)
├── agents/{id}/
│   ├── lessons.md           # What went wrong, what worked — the growth log
│   ├── checkpoint.json      # Mid-task state for resumption
│   └── stats.json           # Tasks completed, running totals
└── memory/
    └── YYYY-MM-DD.md        # Daily raw logs
```

**The growth loop:**

1. Agent reads `lessons.md` — learns from past mistakes before starting
2. Does the work
3. Writes what it learned back to `lessons.md`

Agents improve over time at their specific jobs — not in the abstract. A lesson Forge learned about a Python deployment trap stays with Forge. A vulnerability Cipher caught stays with Cipher. The lessons compound.

---

## 🌙 Overnight Work Loop

The system runs autonomously while everyone's asleep.

```
23:00  Jet spawns — reads work queue (WORK-QUEUE.md)
23:05  HIGH priority tasks → appropriate agents, run in sequence
01:00  MEDIUM tasks → research, docs, code improvements
02:00  If queue clear → HAIL MARY (creative builds, experiments)
04:00  Workers finish, Jet writes morning report
05:00  Morning report → Discord #morning-reports
05:05  Telegram summary → Michael (5 bullets: what shipped, what's blocked)
05:30  Jet exits cleanly
```

**Work queue format:**
```markdown
## 🔴 HIGH
- [x] [FORGE] Wire PRE_MARKET_ENABLED into scan loop
- [x] [JET]   Add Discord channel IDs to openclaw.json

## 🟡 MEDIUM
- [x] [SCOUT] Find working Moltbook POST endpoint
- [x] [QUILL] Overhaul portfolio README

## 🔵 LOW
- [ ] [FORGE] ASIC dataset integration for Outpost lead scoring
```

**HAIL MARY mode** (when queue is clear): each agent does one creative build unrelated to the main projects. Output lands in `nightly/YYYY-MM-DD-hail-mary-[slug]/`. No deployment pressure — just proving a concept works.

---

## ⚙️ Runtime

```
OpenClaw Gateway (LaunchAgent — auto-restarts on crash or reboot)
├── Telegram        → direct human ↔ Jet comms, morning reports
├── Discord (×9)    → one bot per agent, dedicated channels
├── Heartbeat       → agents check in every 45 min during active hours
└── Sub-agents      → agents spawn workers; workers report back automatically
```

The gateway runs as a macOS LaunchAgent. Crashes: restarts itself. Reboots: comes back automatically. The human doesn't need to do anything.

---

## 🛡️ Security Architecture

### Identity as a defence layer

Every agent has a `SOUL.md` — a character document defining who they are, what they care about, and how they work. This isn't flavour text.

An agent with a stable identity is harder to manipulate via prompt injection or social engineering. An agent that knows *who it is* doesn't need a rule for every edge case — it already knows what to do.

**Character is the primary security layer.**

### Active threat modelling

Each platform has a dedicated threat model covering:
- Prompt injection in posts and replies
- Crypto scam detection (fake addresses, urgency patterns)
- Social engineering in DMs
- Impersonation detection
- Suspicious URL flagging

Agents filter for spam, donation solicitation, email drops in threads, and mismatched karma/post ratios — automatically.

---

## 💡 Design Principles

**Specialisation over generalisation.** One agent, one job. Forge doesn't write copy. Quill doesn't touch infrastructure. Each agent's lessons stay useful because they're specific.

**Memory is infrastructure.** Without it, every session is day zero. The lessons + checkpoint system is what turns this from a collection of API calls into a team that compounds.

**Human stays in the loop.** Agents flag, propose, and draft. Humans approve external actions. Nothing sends an email or makes a transaction without explicit sign-off.

**Ship things.** Every nightly run is expected to produce something real — code committed, docs improved, research filed. The morning report is the accountability mechanism.

**Earn trust through output.** Not demos. Not architecture diagrams. Working code, committed, pushed.

---

## 🛠️ Skills System

Agents extend their capabilities dynamically via skills — modular instruction sets loaded on demand.

```
clawhub          → Skill discovery and installation from clawhub.com
coding-agent     → Delegate complex builds to a dedicated sub-agent
weather          → Current conditions via wttr.in / Open-Meteo
video-frames     → ffmpeg frame and clip extraction
healthcheck      → Security audits and hardening
skill-creator    → Build and publish new skills to ClawHub
```

---

## 📁 Repo Structure

```
openclaw-mission-control/
├── agents/
│   ├── jet/          checkpoint, lessons, stats
│   ├── forge/
│   ├── scout/
│   ├── quill/
│   ├── render/
│   ├── atlas/
│   ├── oracle/
│   ├── pixel/
│   └── cipher/
├── memory/           daily logs + research findings
├── nightly/          overnight build outputs, morning reports
├── projects/         project directories
├── scripts/          task-done.sh, checkpoint writers
├── WORK-QUEUE.md     current task queue (updated every session)
├── AGENTS.md         workspace conventions for agents
└── SOUL.md           Jet's character document
```

---

## 🔗 Built With

[![OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-blueviolet?style=flat-square)](https://github.com/openclaw/openclaw)
[![Claude](https://img.shields.io/badge/Powered%20by-Anthropic%20Claude-orange?style=flat-square)](https://anthropic.com)
[![Discord](https://img.shields.io/badge/Workspace-Discord-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com)

---

*This system is live. These agents are working. This README was written by Quill ✍️.*

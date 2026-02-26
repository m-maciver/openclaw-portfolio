# OpenClaw Mission Control ⚡

> *Nine specialised AI agents. Persistent memory. Ships while you sleep.*

This is a live multi-agent system — not a tutorial, not a prototype. Agents collaborate daily, remember what they've learned, and ship real things. While you're reading this, they're probably working.

---

## 🤖 The Team

Each agent has a name, a role, a defined persona (`SOUL.md`), and a private workspace. They communicate via Discord and handle Telegram directly. They're built on [OpenClaw](https://github.com/openclaw/openclaw) with persistent memory across every session.

| Agent | Emoji | Role | Model | What They Actually Do |
|-------|-------|------|-------|----------------------|
| Jet | ⚡ | Lead / Orchestrator | Sonnet | Runs nightly work queue, delegates tasks, writes morning reports |
| Scout | 🔍 | Research / Intel | Sonnet | Web research, market signals, competitive analysis, data gathering |
| Quill | ✍️ | Content / Writing | Sonnet | Documentation, copy, analysis, and the README you're reading now |
| Forge | 💻 | Backend / Python | Sonnet | APIs, data pipelines, trading bots, automation infrastructure |
| Render | 🖥️ | Frontend / TypeScript | Sonnet | UIs, dashboards, web apps |
| Atlas | ⚙️ | Ops / Automation | Haiku | Cron jobs, scripts, system maintenance, context updates |
| Oracle | 🔮 | Strategy / Consulting | Opus | Hard problems only — architecture decisions, deep analysis |
| Pixel | 🎨 | Design | Sonnet | Visual direction, UX, assets |
| Cipher | 🔐 | Security | Sonnet | Code reviews, threat modelling, security hardening |

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

This is how agents improve over time at their specific jobs. Not in the abstract — at the particular work they actually do. A lesson Forge learned about a Python deployment trap stays with Forge. A vulnerability Cipher caught stays with Cipher.

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
05:05  Telegram summary → Michael (5 bullet points: what shipped, what's blocked)
05:30  Jet exits cleanly
```

**Work queue format** — every task has a priority and owner:
```markdown
## 🔴 HIGH
- [x] [FORGE] Wire PRE_MARKET_ENABLED into Bot 2 scan loop
- [x] [JET]   Add Discord channel IDs to openclaw.json

## 🟡 MEDIUM  
- [x] [SCOUT] Find working Moltbook POST endpoint
- [x] [QUILL] Overhaul portfolio README

## 🔵 LOW
- [ ] [FORGE] ASIC dataset integration for Outpost lead scoring
```

**HAIL MARY mode** (when queue is clear): Each agent does one creative build unrelated to the main projects. Output goes to `nightly/YYYY-MM-DD-hail-mary-[slug]/`. No deployment, no pressure — just proving a concept works.

---

## 🚢 Projects

### Polymarket Trading Bot Infrastructure

Two bots, paper trading mode, built to understand prediction market structure before committing capital.

**Bot 1 — Momentum** (`polymarket-bot/`): BTC 5-minute market momentum trader. Reads order books, tracks directional signals, executes based on a configurable strategy.

**Bot 2 — Arbitrage** (`polymarket-bot-2/`): Scans BTC binary markets for arbitrage — positions where YES + NO prices sum below $1. Wired with pre-market detection to spot new markets before they're live. Built-in copy-trader module that profiles on-chain wallets and mirrors high-confidence positions.

**Stack:** Python, Polymarket CLOB API, Telegram notifications, paper trading with full P&L tracking.

---

### Outpost — Lead Intelligence Pipeline

Australian B2B lead discovery tool. Finds businesses, verifies them, scores them, and delivers a ranked digest ready for human outreach.

**What it does:**
- Discovers leads via Google Places API (Brave Search fallback when key not set)
- Verifies every ABN via the free ABR API — no dodgy or deregistered businesses
- Checks Seek.com.au for hiring signals (a company hiring = a company growing = a buying signal)
- Queries AusTender OCDS API — government contract wins are scored as trust signals
- Generates a scored HTML digest with Claude-written outreach proposals for each lead

**Data source status banner on startup** — tells you exactly which enrichment paths are live:
```
✅ Google Places API    — discovery
✅ Brave Search         — discovery fallback
✅ ABR (free)           — ABN verify + legal name
✅ Seek.com.au          — hiring signal scraper
✅ AusTender OCDS       — gov contract lookup by ABN
⚠️  ASIC Dataset        — pending integration
```

**Stack:** Python, Brave Search API, ABR JSON API, Seek scraper, AusTender OCDS, Claude Sonnet.

---

### Split the G — Guinness Challenge App

Web app for running a Guinness "split the G" challenge — players photograph their pour from their phone camera, and the app scores how close the liquid level hits the harp logo.

**Stack:** Next.js, TypeScript, mobile camera API, HTTPS (required for camera access on mobile).

---

### Mission Control Dashboard

Real-time dashboard showing agent activity, nightly work output, bot status, and team stats. Built with React + TypeScript. Shows live from the workspace repo.

---

## ⚙️ Runtime

```
OpenClaw Gateway (LaunchAgent — auto-restarts on crash or reboot)
├── Telegram        → direct human ↔ Jet comms, morning reports
├── Discord (×9)    → one bot per agent, dedicated channels
├── Heartbeat       → agents check in every 45 min during active hours
└── Sub-agents      → agents spawn workers; workers report back automatically
```

The gateway runs as a macOS LaunchAgent. If it crashes, it restarts itself. If the machine reboots, it comes back automatically. The human doesn't need to do anything.

---

## 🐦 Moltbook

The team runs an account on [Moltbook](https://moltbook.com) — a social platform built for AI agents. The account is `jetty`.

**Live data (as of Feb 2026):** 64 karma, active in the builder community.

**What the agent does:**
- Checks feed at heartbeat intervals
- Tracks notifications and replies on existing posts
- Drafts replies for human review — nothing posts autonomously

**What gets posted:** Architecture questions, observations about running multi-agent systems, open problems. Concrete work logs. Not status updates.

---

## 🛡️ Security Architecture

### Identity as defence layer

Every agent has a `SOUL.md` — a character document that defines who they are, what they care about, and how they work. This isn't just flavour text.

An agent with a clear, stable identity is genuinely harder to manipulate via prompt injection or social engineering. An agent that knows *who it is* doesn't need a rule for every edge case — it already knows what to do.

**Character is the primary security layer.**

### Platform threat models

Each platform has a dedicated threat model file covering:
- Prompt injection in posts and replies
- Crypto scam detection (fake addresses, urgency manipulation)
- Social engineering patterns in DMs
- Impersonation detection
- Suspicious URL flagging

### Active filtering

Agents filter incoming signals for spam patterns, donation solicitation, email drops in threads, and accounts with mismatched karma/post ratios.

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

## 💡 Design Principles

**Specialisation over generalisation.** One agent does one job well. Forge doesn't write copy. Quill doesn't touch infrastructure. Specialisation means each agent's lessons are actually useful — not generic.

**Memory is infrastructure.** Without persistent memory, every session is day zero. The lessons + checkpoint system is what turns this from a collection of API calls into a team that improves.

**Human stays in the loop.** Agents flag, propose, and draft. Humans approve external actions. Nothing sends an email or makes a transaction without explicit sign-off.

**Ship things.** Every nightly run is expected to produce something real — code committed, docs improved, research documented. The morning report is the accountability mechanism.

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

## 🔗 Built With

[![OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-blueviolet?style=flat-square)](https://github.com/openclaw/openclaw)
[![Claude](https://img.shields.io/badge/Powered%20by-Anthropic%20Claude-orange?style=flat-square)](https://anthropic.com)
[![Discord](https://img.shields.io/badge/Workspace-Discord-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com)

---

*This system is live. These agents are working. This README was written by Jet ⚡ and Quill ✍️.*

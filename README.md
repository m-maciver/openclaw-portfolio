# OpenClaw Mission Control ⚡

> *Nine specialised AI agents. Persistent memory. A self-improving growth loop. Shipped product.*

This is a working multi-agent system — not a tutorial, not a prototype. Agents collaborate daily, remember what they've learned, wake up with context, and ship real things.

---

## 🤖 The Team

Each agent has a distinct role, a defined persona (`SOUL.md`), and a private workspace. They run on [OpenClaw](https://github.com/openclaw/openclaw) with persistent memory across sessions.

| Agent | Role | Model | Focus |
|-------|------|-------|-------|
| Jet ⚡ | Lead / Orchestrator | Claude Sonnet | Task routing, delegation, project management |
| Scout 🔍 | Research / Intel | Claude Sonnet | Web research, market signals, data gathering |
| Quill ✍️ | Content / Writing | Claude Sonnet | Docs, copy, analysis, communication |
| Forge 💻 | Backend / Python | Claude Sonnet | APIs, data pipelines, bot infrastructure |
| Render 🖥️ | Frontend / TypeScript | Claude Sonnet | UI, dashboards, web apps |
| Atlas ⚙️ | Ops / Automation | Claude Haiku | Cron jobs, scripts, system maintenance |
| Oracle 🔮 | Strategy / Consulting | Claude Opus | High-stakes decisions, deep analysis |
| Pixel 🎨 | Design | Claude Sonnet | Visual direction, assets, UX |
| Cipher 🔐 | Security | Claude Sonnet | Code audits, threat modelling, hardening |

---

## 🧠 Memory & Continuity

Agents wake up fresh each session — but they're never starting from scratch.

```
workspace/
├── SOUL.md            # Persona, values, and working style
├── MEMORY.md          # Long-term memory (curated, session-persistent)
├── lessons.md         # What went wrong, what worked — the growth loop
├── checkpoint.json    # Mid-task state for resumption
└── memory/
    └── YYYY-MM-DD.md  # Daily logs, raw and timestamped
```

**The loop:**
1. Agent reads `lessons.md` before starting any task
2. Completes the work
3. Writes what it learned back to `lessons.md`

This means agents genuinely improve over time — at their specific jobs, not in the abstract. A lesson learned by Forge stays with Forge. A mistake Cipher caught gets flagged for Cipher to remember.

---

## 💬 Discord Workspace

Every agent has its own Discord bot and dedicated channel in the Mission Control server.

- **#work-queue** — incoming tasks, routed by Jet
- **#standup** — daily status and blockers
- **#team-log** — activity feed, cross-agent visibility
- **GitHub webhooks** — commits and PRs surface in Discord automatically
- **Voice channels** — enabled for future real-time coordination

Agents can talk to each other, respond to tasks, and log work — all through Discord, all asynchronously.

---

## 🌙 Nightly Automation

Two automated modes run while everyone's asleep:

### Hail Mary (2am cron)
- Runs on a fixed schedule, no human trigger needed
- Experimental builds, creative proof-of-concepts, speculative tools
- Whatever seems worth trying — with no pressure to ship

### Night Rotation (triggered by "goodnight")
Cycles through three modes:

| Rotation | Mode | Focus |
|----------|------|-------|
| A | Project Sprint | Push a real project forward |
| B | Intel + Build | Research a domain, then prototype something |
| C | Research + Tools | Deep dives, skill-building, infrastructure |

The system picks the rotation, does the work, and reports back in the morning.

---

## 🚢 Projects Shipped

### 📊 Polymarket Trading Bot Infrastructure
Paper trading system with live market data ingestion, arbitrage signal detection, and a copy-trader module. Built to validate strategies without risk before any live exposure.

### 🏢 Outpost — Lead Intelligence Pipeline
Australian business research tool. Finds targets, enriches data, and delivers structured digests. Designed for B2B outreach with minimal manual effort.

### ⚡ Lightning Network Agent Economy
Design and prototyping work for a sats-based accountability layer — agents earn and spend Bitcoin for real task completion. The idea: economic skin in the game makes agents more careful.

---

## 🛠️ Skills System

Agents extend their capabilities by loading skills on demand — modular instruction sets that teach them new tools and workflows.

```
# Example skills loaded dynamically
clawhub          → Skill discovery and installation
coding-agent     → Delegate complex builds to a sub-agent
weather          → Current conditions via wttr.in / Open-Meteo
video-frames     → ffmpeg frame/clip extraction
healthcheck      → Security audits and hardening
skill-creator    → Build and publish new skills
```

New skills can be published to [ClawHub](https://clawhub.com) and pulled down on any agent, on any machine.

---

## ⚙️ Runtime

```
OpenClaw Gateway
├── Runs as a LaunchAgent (auto-restarts on crash/reboot)
├── Telegram channel  → direct human ↔ agent comms
├── Discord channel   → team workspace + webhooks
├── Heartbeat system  → agents check in, flag issues, do background work
└── Sub-agent spawning → agents can spawn and coordinate child agents
```

Agents operate across two surfaces simultaneously: a personal Telegram channel for direct conversation, and Discord for team-level coordination. The gateway keeps everything alive and reconnected automatically.

---

## 📁 Repo Structure

```
openclaw-portfolio/
├── agents/
│   ├── jet/          # Lead agent workspace
│   ├── scout/        # Research agent workspace
│   ├── quill/        # Content agent workspace
│   ├── forge/        # Backend agent workspace
│   ├── render/       # Frontend agent workspace
│   ├── atlas/        # Ops agent workspace
│   ├── oracle/       # Strategy agent workspace
│   ├── pixel/        # Design agent workspace
│   └── cipher/       # Security agent workspace
├── projects/         # Shipped and in-progress work
└── README.md
```

---

## 💡 Design Principles

- **Specialisation over generalisation** — each agent is optimised for one domain, not everything
- **Memory is infrastructure** — continuity isn't bolted on, it's built into how agents work
- **Human stays in the loop** — agents flag decisions, don't make them unilaterally
- **Earn trust through output** — agents prove themselves through shipped work, not demos
- **Grow through experience** — the lessons system is the competitive moat

---

## 🔗 Built With

[![OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-blueviolet?style=flat-square)](https://github.com/openclaw/openclaw)
[![Claude](https://img.shields.io/badge/Powered%20by-Anthropic%20Claude-orange?style=flat-square)](https://anthropic.com)
[![Discord](https://img.shields.io/badge/Workspace-Discord-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com)

---

*This system is live. These agents are working. This README was written by Quill ✍️.*

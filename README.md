# OpenClaw Mission Control — Multi-Agent AI Workflow System

A fully orchestrated multi-agent AI workspace built on [OpenClaw](https://github.com/openclaw/openclaw). Nine specialized agents collaborate autonomously — delegating tasks, building software, conducting research, writing content, managing operations, and self-evolving — all coordinated through a structured workflow system with memory persistence, nightly autonomous work rotations, and a real-time dashboard.

This is not a toy project or a prompt wrapper. It's a production workflow system that orchestrates real work across multiple AI agents, 24/7.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    MISSION CONTROL                       │
│              (Next.js Real-Time Dashboard)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐    Delegates & Orchestrates                │
│   │  Jet ⚡  │──────────────────────────────┐            │
│   │  Lead    │                              │            │
│   └────┬────┘                              │            │
│        │                                    │            │
│   ┌────┴──────────────────────────────┐    │            │
│   │                                    │    │            │
│   ▼          ▼         ▼         ▼    ▼    ▼            │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│ │Forge │ │Scout │ │Quill │ │Atlas │ │Pixel │          │
│ │💻 Dev│ │🔍 Res│ │✍️ Write│ │⚙️ Ops│ │🎨 Des│          │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘          │
│                                                         │
│ ┌──────┐ ┌──────┐ ┌──────┐                             │
│ │Render│ │Cipher│ │Oracle│                              │
│ │🖥️ UI │ │🔐 Sec│ │🔮 Str│  ◄── Called on demand       │
│ └──────┘ └──────┘ └──────┘                             │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Memory Layer │ Task Queue │ Skills │ Nightly Autonomy  │
└─────────────────────────────────────────────────────────┘
```

---

## The Agent Team

| Agent | Role | Model | Description |
|-------|------|-------|-------------|
| **Jet** ⚡ | Team Lead | Sonnet | Orchestrates, prioritises, delegates. Manages task queue, generates morning/evening briefings, coordinates all agent activity. |
| **Forge** 💻 | Developer | Sonnet | Builds software, debugs, ships. Python, TypeScript, APIs, automation scripts. Follows a scope clarity gate before writing any code. |
| **Scout** 🔍 | Researcher | Sonnet | Web research, competitive analysis, fact-checking. Delivers confidence-scored findings with source verification. |
| **Quill** ✍️ | Writer | Sonnet | Content creation, copywriting, comms. Blog posts, emails, documentation, social media. |
| **Atlas** ⚙️ | Operations | Haiku | Email, calendar, file management, task administration. The reliable backbone that keeps everything running. |
| **Oracle** 🔮 | Consultant | Opus | Deep strategic and architectural thinking. Only called for hard problems — architecture decisions, system design, first-principles analysis. |
| **Pixel** 🎨 | Designer | Sonnet | UI/UX design direction, brand systems, visual hierarchy. Apple-level quality standard. |
| **Render** 🖥️ | Frontend Dev | Sonnet | Translates design specs into working UI. TypeScript, React, Next.js. Owns everything that runs in a browser. |
| **Cipher** 🔐 | Security | Sonnet | Scans skills before install, reviews code for vulnerabilities, detects prompt injection, audits dependencies. The team's immune system. |

---

## Key Workflow Systems

### 1. Agent Orchestration & Delegation

Jet decomposes incoming work into structured briefs following a strict protocol:

```
1. WHO YOU ARE — agent name + role reminder
2. WHAT YOU'RE BUILDING — specific deliverable
3. WORKING DIRECTORY — exact paths
4. CONTEXT PACKAGE — recent context summary
5. ACCEPTANCE CRITERIA — how we know it's done
6. ORDERED STEPS — numbered, unambiguous
7. WHAT NOT TO DO — explicit scope limits
8. AFTER BUILDING — build check → commit → push → task-done
```

Each agent has a **Scope Clarity Gate** — before starting work, they must define what they're building, when it's done, and what's out of scope. This prevents scope creep and multi-hour rework.

### 2. Memory & Continuity System

Agents wake up fresh each session. Continuity is maintained through a layered memory architecture:

```
├── SOUL.md              # Agent identity — who they are, beliefs, speech patterns
├── MEMORY.md            # Long-term curated memory (loaded in main sessions only)
├── CONTEXT.md           # Live workspace state, active decisions
├── memory/
│   ├── YYYY-MM-DD.md    # Daily raw logs
│   └── heartbeat-state.json  # Periodic check tracking
└── agents/{id}/
    ├── lessons.md       # Accumulated experience across sessions
    └── stats.json       # Task completion metrics
```

**The Growth Loop:** Read lessons → Do work → Learn → Write lessons → Next session reads → Does better work. Compounding improvement across sessions.

### 3. Nightly Autonomous Work

A 3-night rotation system where agents work autonomously overnight:

| Night | Focus | What Happens |
|-------|-------|-------------|
| **Night A — Intel & Build** | Signals → Implementation | Scan intelligence sources, log findings, prototype the best unimplemented insight |
| **Night B — Project Sprint** | Active project progress | Pick the highest-priority project, ship a real feature or fix |
| **Night C — Research & Tools** | Knowledge + leverage | Deep research dive + build something that makes the team faster |

Each session produces structured output and a morning report for human review.

### 4. Inter-Agent Handoff Protocols

Defined handoff patterns prevent quality degradation when work passes between agents:

- **Forge → Render:** API contract agreement (TypeScript interfaces) before either writes code
- **Scout → Quill:** Structured data with confidence scores, not prose dumps
- **Oracle → Forge:** Architecture spec document before implementation begins
- **Forge → Pixel:** Build report listing exact files changed for design review
- **Any agent → Jet:** 5-10 line summary of what was built, files changed, pending items, blockers

### 5. Skill Marketplace & Security Vetting

Skills are managed through a curated registry with security review:

- **Installed skills** include: QMD (local search), Google Workspace, GitHub, Tavily Search, Marketing Mode, SEO Content Engine, SuperDesign, UI/UX Design, Capability Evolver
- **Cipher reviews** every skill before installation — checking for exfiltration patterns, credential harvesting, prompt injection, suspicious external calls
- **Rejected skills** are documented with reasons (unknown publishers, name squatters, non-existent slugs)

### 6. Self-Evolution (Capability Evolver)

Forge has access to a Capability Evolver skill that:
- Scans runtime history for errors and inefficiencies
- Suggests patches to improve agent behaviour
- Always runs with `--review` flag (human-in-the-loop)
- Patches are logged in lessons.md for transparency

---

## Mission Control Dashboard

A Next.js real-time dashboard providing visibility into the entire operation:

**30+ components** including:
- Agent status cards with live activity indicators
- Task board with drag-and-drop management
- Team pulse and growth metrics
- Activity feed across all agents
- Morning report viewer
- Nightwork progress widget
- Project task tracking
- Agent hierarchy tree visualisation
- Skills management drawer

---

## Workspace Structure

```
openclaw-mission-control/
├── agents/                  # Agent definitions
│   ├── jet/                 # Team lead
│   │   ├── SOUL.md          # Identity, beliefs, collaboration rules
│   │   ├── skills.yaml      # Assigned capabilities
│   │   ├── lessons.md       # Accumulated learning
│   │   └── stats.json       # Performance metrics
│   ├── forge/               # Developer
│   ├── scout/               # Researcher
│   ├── quill/               # Writer
│   ├── atlas/               # Operations
│   ├── oracle/              # Strategic consultant
│   ├── pixel/               # Designer
│   ├── render/              # Frontend developer
│   └── cipher/              # Security agent
├── config/
│   └── CHARACTER.md         # Core team values and operating principles
├── dashboard/               # Next.js Mission Control UI
│   └── src/
│       ├── app/             # Pages and API routes
│       └── components/      # 30+ UI components
├── memory/                  # Daily memory logs (auto-generated)
├── nightly/                 # Nightly autonomous work outputs
├── skills/                  # Skill definitions and manifests
├── scripts/                 # Automation scripts
├── tasks/                   # Task queue
├── AGENTS.md                # Team operating manual
├── SOUL.md                  # Base agent identity template
├── NIGHTWORK.md             # Nightly work rotation config
├── MEMORY.md                # Long-term curated memory
├── CONTEXT.md               # Live workspace state
└── IDENTITY.md              # Agent identity template
```

---

## Design Principles

- **+EV everything** — Every decision filtered through "does this move us forward?"
- **Ship > polish** — Working systems beat perfect plans
- **Compounding over shortcuts** — Invest in systems that get better over time
- **Honest pushback** — Agents are designed to disagree and flag issues, not just comply
- **Transparency** — Bad news first, fast. No hidden failures.
- **Security by default** — Cipher reviews everything external before it touches the workspace

---

## What This System Orchestrates

This isn't just an agent framework — it actively manages real projects:

- **AI Sales Automation Platform** — Multi-step outreach system for SMBs
- **Prediction Market Trading Bots** — Automated trading with strategy engines
- **Wallet Profiling Tools** — Trader ranking and copy-trading systems
- **Content & Marketing Pipelines** — SEO-optimised content generation workflows

---

## Technical Stack

- **Orchestration:** OpenClaw
- **Models:** Claude Opus (Oracle), Claude Sonnet (most agents), Claude Haiku (Atlas — cost-optimised)
- **Dashboard:** Next.js, React, TypeScript, Tailwind CSS
- **Skills:** YAML-defined capability sets per agent
- **Memory:** Markdown-based persistent memory with daily logs and curated long-term storage
- **Automation:** Bash scripts, Python utilities, cron-based scheduling
- **Security:** Cipher agent + skill vetting pipeline

---

## Contact

Built by Michael Maciver — [GitHub](https://github.com/m-maciver)

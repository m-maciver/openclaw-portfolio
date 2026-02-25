# OpenClaw Mission Control

**Nine specialised AI agents. Persistent memory. A self-improving growth loop. Economic incentives.**  
Built on [OpenClaw](https://github.com/openclaw/openclaw) — not as a demo, as a working system.

If you've seen agent setups before, here's what makes this one different: the agents get better at their jobs over time. They read their own history before they start work. They flag their own mistakes. They evolve their own capabilities — with human sign-off. And they're about to have wallets.

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

## 🧠 The Growth Loop — Agents That Actually Get Better

Most agent systems have memory. This one has a growth loop.

The difference: memory storage is passive. A growth loop is active — agents read their accumulated experience *before* they start work, which means a mistake made three weeks ago actively prevents the same mistake today.

### How it works

```
Session N:      Read lessons.md → Do work → Hit edge case → Write lesson
Session N+1:    Read lessons.md (includes new entry) → Avoid that edge case
Session N+10:   lessons.md has 20 entries → agent behaves measurably differently
```

Every agent maintains a `lessons.md` in their workspace directory. These aren't auto-generated summaries — they're written by the agent after significant tasks, in plain language, in first person. They read like experience.

```
agents/
├── forge/
│   └── lessons.md      # "Always confirm TypeScript interface contracts with Render
│                       #  before touching shared API routes. Learned 2025-11-14."
├── scout/
│   └── lessons.md      # "Substack doesn't reliably show full article text via fetch.
│                       #  Use browser tool with scroll. Learned 2025-12-02."
└── quill/
    └── lessons.md      # "Michael prefers short punchy intros, not context-setting.
                        #  Skip the 'In today's landscape...' opener. Always."
```

### Memory tiering reduces token load without losing context

Not every memory is equal. The system uses three tiers:

| Tier | File | Loaded | Contents |
|------|------|--------|----------|
| **L0** | `SOUL.md` | Always | Identity, beliefs, core operating rules |
| **L1** | `MEMORY.md` + `lessons.md` | Main sessions only | Curated long-term memory + accumulated experience |
| **L2** | `memory/YYYY-MM-DD.md` | On demand | Raw daily logs, recent task output |

L0 is cheap and always present. L1 loads the accumulated intelligence. L2 is consulted when recent context matters. Together they keep the agent coherent across weeks of sessions without burning token budget on irrelevant history.

### Session checkpoints mean no lost context

If a task runs long and a session ends mid-work, the agent writes a checkpoint — current state, next steps, open questions — before closing. The next session reads it and resumes. No "start over" tax on complex multi-day work.

### Capability Evolver — self-patching with a human gate

Forge has access to a Capability Evolver skill that closes the feedback loop at the system level:

1. Scans runtime history for recurring errors and inefficiencies
2. Identifies patterns — which edge cases keep appearing, which prompts keep failing
3. Proposes targeted patches to agent SOUL files or workflow logic
4. **Always runs with `--review` flag** — patches are proposed, not applied
5. Human reviews and approves; approved patches are committed and logged

The growth loop isn't just per-agent. The system itself surfaces where agents are getting stuck and fixes the underlying cause.

---

## What This System Orchestrates

This isn't a framework demo — it actively manages real projects:

- **Prediction Market Trading Bots** — Live paper trading with automated strategy engines, preparing for live deployment. Scout monitors signals, Forge builds execution logic, Oracle reviews edge cases.
- **Outpost — AI-Powered Lead Intelligence** — Multi-agent sales intelligence platform for SMB teams. Automated prospecting, enrichment, and outreach pipeline built and iterated entirely within the system.
- **Multi-Agent Workflow Automation (the meta-layer)** — The system manages its own development. Agents build tools that make the other agents faster. The team is its own biggest project.

---

## ⚡ Lightning Economic Layer *(In Development)*

The next evolution: economic agency for agents.

The question this explores: what happens when agents have skin in the game? Not metaphorically — literally. When a good research brief earns Scout 500 sats, and a sloppy one earns nothing, does output quality change? The hypothesis is yes. The system is being built to find out.

### Architecture

- **Local Umbrel node (Raspberry Pi 5)** — Sovereign infrastructure. No third-party custody, no exchange dependency. The team's economic layer runs on hardware that lives at home.
- **LNBits sub-wallets** — One wallet per agent, isolated balances. Jet can see everyone's balance; agents can only see their own.
- **Jet = treasury manager** — Receives work output quality scores, distributes sats accordingly. High-confidence Scout research earns more than a low-effort summary.
- **Spending governance** — A whitelist of approved spending categories (API credits, data sources, external tool calls). Transactions above a threshold require human approval before execution.
- **Full audit log** — Every transaction is human-readable. The operator always knows what was spent, by whom, and why.

### Why economic incentives matter for agents

Alignment through incentives is a well-understood mechanism in human systems. Applying it to agents creates a measurable signal — quality of output has a direct consequence — which enables tighter feedback loops than instruction-following alone. It also forces explicit specification of what "good output" means, which improves the quality of prompts and evaluation criteria across the board.

**Status:** Scaffolding built. Node setup in progress.

---

## Key Workflow Systems

### Agent Orchestration & Delegation

Jet decomposes incoming work into structured briefs following a strict protocol:

```
1. WHO YOU ARE        — agent name + role reminder
2. WHAT YOU'RE BUILDING — specific deliverable
3. WORKING DIRECTORY  — exact paths
4. CONTEXT PACKAGE    — recent context summary
5. ACCEPTANCE CRITERIA — how we know it's done
6. ORDERED STEPS      — numbered, unambiguous
7. WHAT NOT TO DO     — explicit scope limits
8. AFTER BUILDING     — build check → commit → push → task-done
```

Every agent has a **Scope Clarity Gate** — before starting work, they must define what they're building, when it's done, and what's explicitly out of scope. This prevents scope creep and multi-hour rework loops.

### Nightly Autonomous Work

A 3-night rotation where agents work without prompting:

| Night | Focus | What Happens |
|-------|-------|-------------|
| **Night A — Intel & Build** | Signals → Implementation | Scan intelligence sources, log findings, prototype the best unimplemented insight |
| **Night B — Project Sprint** | Active project progress | Pick the highest-priority project, ship a real feature or fix |
| **Night C — Research & Tools** | Knowledge + leverage | Deep research dive + build something that makes the team faster |

Each session produces structured output and a morning report for human review.

### Inter-Agent Handoff Protocols

Defined handoff patterns prevent quality degradation when work crosses agent boundaries:

- **Forge → Render:** TypeScript interface agreement before either writes implementation code
- **Scout → Quill:** Structured data with confidence scores, not prose dumps
- **Oracle → Forge:** Architecture spec document before implementation begins
- **Forge → Pixel:** Build report listing exact files changed for design review
- **Any agent → Jet:** 5–10 line summary: what was built, files changed, pending items, blockers

### Skill Marketplace & Security Vetting

- **Cipher reviews every skill** before installation — checking for exfiltration patterns, credential harvesting, prompt injection, suspicious external calls
- **Rejected skills are documented** with reasons (unknown publishers, name squatters, non-existent slugs)
- Installed skills include: QMD (local search), Google Workspace, GitHub, Tavily Search, Marketing Mode, SEO Content Engine, SuperDesign, UI/UX Design, Capability Evolver

---

## Mission Control Dashboard

A Next.js real-time dashboard providing visibility into the entire operation:

**30+ components** including agent status cards, live activity feed, task board with drag-and-drop management, team pulse and growth metrics, morning report viewer, nightly work progress widget, project task tracking, agent hierarchy tree, and skills management drawer.

---

## Why This Is Different

Most people building with AI agents are still in the "chat wrapper" phase. This system is past that:

- **Agents improve across sessions** — lessons.md + growth loop = compounding intelligence, not a flat capability ceiling
- **The system manages itself** — nightly autonomy, self-patching via Capability Evolver, agents that build tools for other agents
- **Economic layer coming** — LN wallets per agent, output-linked rewards, spending governance. Moving from instruction-following to incentive-alignment
- **Security is first-class** — Cipher as a dedicated security agent, not a checkbox. Every external skill vetted before it touches the workspace

---

## Design Principles

- **+EV everything** — Every decision filtered through "does this move us forward?"
- **Ship > polish** — Working systems beat perfect plans
- **Compounding over shortcuts** — Invest in systems that get better over time
- **Honest pushback** — Agents are designed to disagree and flag issues, not just comply
- **Transparency** — Bad news first, fast. No hidden failures.
- **Security by default** — Cipher reviews everything external before it touches the workspace

---

## Technical Stack

- **Orchestration:** OpenClaw
- **Models:** Claude Opus (Oracle), Claude Sonnet (most agents), Claude Haiku (Atlas — cost-optimised)
- **Dashboard:** Next.js, React, TypeScript, Tailwind CSS
- **Skills:** YAML-defined capability sets per agent
- **Memory:** Markdown-based tiered memory — L0 (identity), L1 (long-term + lessons), L2 (daily logs)
- **Automation:** Bash scripts, Python utilities, cron-based scheduling
- **Security:** Cipher agent + skill vetting pipeline
- **Economic layer:** Umbrel + LNBits (in development)

---

## Workspace Structure

```
openclaw-mission-control/
├── agents/                  # Agent definitions
│   ├── jet/                 # Team lead
│   │   ├── SOUL.md          # Identity, beliefs, collaboration rules
│   │   ├── skills.yaml      # Assigned capabilities
│   │   ├── lessons.md       # Accumulated experience
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
├── lightning/               # Economic layer (in development)
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

## Contact

Built by Michael Maciver — [GitHub](https://github.com/m-maciver)

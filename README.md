# OpenClaw Mission Control

> *A 9-agent AI team with isolated context, persistent memory, and a Discord-native workspace. Built to run continuously without burning tokens or hitting rate limits.*

This is the architecture behind a production multi-agent system. No demos. No toy examples. The agents run nightly, improve over sessions, and ship real work. What follows is a technical breakdown of how it's structured and why it works.

---

## Architecture: Why 9 Specialised Agents Beat One General Agent

The most common mistake in multi-agent system design is building a single orchestrator that tries to do everything. You end up with an agent that knows a little about everything, accumulates context about everything, and eventually costs a lot to run — because its session history contains everything.

This system takes the opposite approach: **one agent per role, hard role boundaries, isolated context.**

```
                        ┌──────────┐
                        │  Jet ⚡  │  ← Orchestrator / Work Queue
                        └────┬─────┘
           ┌────────┬────────┼────────┬────────┐
           ▼        ▼        ▼        ▼        ▼
       Scout 🔍  Forge 💻  Quill ✍️  Render 🖥️  Atlas ⚙️
       Research  Backend  Writing  Frontend   Ops/Infra
           
           ┌────────┬────────┐
           ▼        ▼        ▼
       Oracle 🔮  Pixel 🎨  Cipher 🔐
       Strategy   Design    Security
```

Each agent:
- Has **one Discord bot** mapped to it — its identity on the platform
- Has **one primary channel** — its feed, its history, its workspace
- Loads **only its own channel history** when it wakes — not the whole system
- Has **its own lesson file** — accumulated experience specific to its domain
- Runs on a **model matched to its workload** — not everything gets Sonnet

### Why This Beats a Single Agent

**Context isolation is a feature, not a limitation.** When Forge wakes up to work on an API, it doesn't need to know what Quill wrote last week or what Scout found this morning. Loading irrelevant history costs tokens and degrades focus. Forge loads Forge's history. That's it.

**Specialisation compounds.** Forge's `lessons.md` contains deployment traps, API quirks, and build patterns from every session it's run. Cipher's contains security observations specific to the codebases it's reviewed. These lessons stay sharp because they're scoped — they don't get diluted by unrelated work.

**Failure is contained.** If Pixel gets confused about a design direction, that confusion doesn't bleed into Scout's research session. Each agent's context is its own.

**Model matching cuts cost.** Haiku for ops work. Sonnet for most agents. Opus only when Oracle is called in for hard architectural decisions. Running Opus on cron job maintenance would be expensive and unnecessary.

---

## The Team

| Agent | Emoji | Role | Model | Responsibilities |
|-------|-------|------|-------|-----------------|
| Jet | ⚡ | Lead / Orchestrator | Sonnet | Nightly work queue, task delegation, morning reports |
| Scout | 🔍 | Research / Intel | Sonnet | Web research, market signals, competitive analysis |
| Quill | ✍️ | Content / Writing | Sonnet | Documentation, copy, analysis |
| Forge | 💻 | Backend / Python | Sonnet | APIs, data pipelines, automation infrastructure |
| Render | 🖥️ | Frontend / TypeScript | Sonnet | UIs, dashboards, web apps |
| Atlas | ⚙️ | Ops / Automation | Haiku | Cron jobs, scripts, system maintenance, context updates |
| Oracle | 🔮 | Strategy | Opus | Hard architectural decisions, deep analysis — called in when needed |
| Pixel | 🎨 | Design | Sonnet | Visual direction, UX, assets |
| Cipher | 🔐 | Security | Sonnet | Code reviews, threat modelling, security hardening |

Atlas runs on Haiku deliberately. Ops work — checking file states, running scripts, updating context files — doesn't need Sonnet. It needs speed and low cost. Atlas handles dozens of small tasks per day; those tokens add up fast if you're not paying attention.

Oracle runs on Opus deliberately too. It's expensive, and that's the point — calling Oracle is a decision, not a default. When you reach for it, you know the problem is hard enough to justify it.

---

## Discord as the Workspace

### Why Discord Over Slack, Email, or a Custom UI

Discord is the communication hub for this system. Not because it's the coolest tool — because it solves a concrete problem.

**Persistent channels are persistent context.** Every agent has a dedicated channel. That channel is its working memory externalized. When it wakes up, it reads its channel history and knows what's been happening. The channel is the continuity mechanism.

With email or ephemeral messaging, you'd need to rebuild that context from scratch every session or maintain a separate state store. Discord does it natively, for free, with a clean API.

**The human interacts the same way the agents interact with each other.** There's no separate "human interface" and "agent interface." Michael types in the #jet channel the same way Forge sends Jet a task result. Same protocol. Same channel. No context switching between a chat app and some dashboard.

**Any device, anywhere, always in sync.** The Discord mobile app is better than most custom admin UIs ever ship to be. Notifications, history, file attachments, threads, reactions — it's all there. The morning report lands in #morning-reports at 5am. Check it on a phone over coffee. That's it.

**Bot identity gives agents presence.** Each agent has its own Discord bot, its own username, its own avatar. When Forge posts a build result and Quill posts a doc summary, they appear as distinct entities — not noise from a single bot account. This matters for legibility when you're reviewing what happened overnight.

### Channel Structure

```
📁 Mission Control
├── #jet            ← Jet's primary channel / work queue / delegation
├── #morning-reports ← Nightly run summaries, delivered 5am
├── #documents      ← Reports, drafts, outputs from all agents
├── #forge          ← Build logs, deployment results
├── #scout          ← Research outputs, market signals
├── #quill          ← Drafts, copy, written outputs
├── #render         ← Frontend work, UI updates
├── #atlas          ← Ops logs, system status
├── #oracle         ← Strategic analysis, architecture decisions
├── #pixel          ← Design work, assets
└── #cipher         ← Security reviews, threat logs
```

Each agent reads only its own channel when it wakes up. The channel history IS the session context.

---

## Token Cost Efficiency

Running 9 agents continuously sounds expensive. The architecture is specifically designed to keep costs low. Here's exactly how.

### 1. Isolated Channel History

The biggest cost driver in multi-agent systems is context loading. If every agent loaded the full system history every session, token costs would scale O(agents × history_length). That's the death spiral.

Here, each agent loads only its own channel history. The cost scales with how active that specific agent has been — not with system-wide activity. Forge doesn't pay tokens for what Scout found last Tuesday.

### 2. Checkpoints Instead of Session Replays

When an agent is mid-task and needs to resume, it doesn't re-read 50 messages to reconstruct what happened. It reads a single JSON file.

```json
// agents/forge/checkpoint.json
{
  "task": "Wire PRE_MARKET_ENABLED into scan loop",
  "status": "in_progress",
  "lastStep": "Modified scan.py line 142 — needs integration test",
  "nextAction": "Run test suite against staging, commit if passing",
  "sessionId": "2025-03-24-b"
}
```

That's 5 lines. Not 50 messages. The agent picks up exactly where it left off without any context archaeology.

### 3. Model Tiering

| Workload | Model | Why |
|----------|-------|-----|
| Ops tasks (Atlas) | Haiku | Fast, cheap, sufficient for script execution and file management |
| Most agents | Sonnet | Strong reasoning, reasonable cost, fits the work |
| Hard architectural problems (Oracle) | Opus | Called in deliberately for the problems that actually need it |

The key discipline is that Opus is never the default. It's called when justified.

### 4. Heartbeat System

Agents check in every 45 minutes during active hours. A heartbeat call is tiny — it reads `HEARTBEAT.md`, a small file with current priorities and any flags set by other agents.

```markdown
# HEARTBEAT.md
- Outpost scan running — don't interrupt Forge
- Scout found new competitor pricing — brief Oracle when available
- Nothing urgent otherwise
```

Instead of loading full channel history every 45 minutes to see if anything needs attention, agents load one small file. 99% of heartbeats are a 5-second context check that returns `HEARTBEAT_OK`.

### 5. Ephemeral Sub-agents

When a task is complex or needs isolated execution, an agent spawns a sub-agent. The sub-agent starts with a clean context, does one job, exits.

There's no accumulated context drift — the sub-agent doesn't carry the parent's session history. It gets a targeted brief, executes, reports back. This is how long-running builds happen without ballooning the parent agent's context window.

### 6. Memory Files Prevent Context Re-discovery

Agents maintain:
- `agents/{id}/lessons.md` — specific learnings from past sessions
- `agents/{id}/checkpoint.json` — mid-task state
- `memory/YYYY-MM-DD.md` — daily raw logs
- `MEMORY.md` — curated long-term memory (main session only)

When an agent wakes up and reads its lessons file, it doesn't need to re-discover that a particular API endpoint changed or that a deployment config has a specific quirk. That was already learned, written down, and now costs a few hundred tokens to recall instead of a full debug session to rediscover.

---

## Rate Limit Avoidance

9 agents. Anthropic API rate limits. This looks like a problem — but it's not, because of how the system is structured.

### Sequential Nightly Queue

The nightly work queue runs agents **sequentially**, not concurrently. When Jet processes the queue:

```
23:00  Jet wakes → reads WORK-QUEUE.md
23:05  Spawns Forge for high-priority backend task
        → Forge works, exits cleanly
01:00  Spawns Scout for research task
        → Scout works, exits cleanly
02:30  Spawns Quill for documentation
        → Quill works, exits cleanly
04:00  Jet writes morning report, exits
```

At any given moment, there are typically 1-2 active sessions, not 9. The "9 agents" describes the team structure, not 9 simultaneous API calls.

### Sub-agent Session Isolation

Sub-agents run as **separate sessions** in the API. This is important: they draw from a separate context window, not the parent's. A sub-agent spawned by Forge to run integration tests doesn't count against Forge's context limit. They're independent API sessions.

This also means if a sub-agent runs long or generates a lot of output, it doesn't pollute the parent's token budget.

### Staggered Heartbeat Polling

Agents don't all check in at the same time. Heartbeat schedules are staggered — Jet at :00, Scout at :10, Forge at :20, etc. No thundering herd of simultaneous API calls at the top of the hour.

### Heavy Work at Off-Peak Hours

Overnight builds — large codebases, multi-step pipelines, research synthesis — run between midnight and 4am. This isn't just about rate limits; it's about throughput. Off-peak API response times are faster, and there's no competition with interactive sessions.

---

## The Memory System

Agents wake fresh every session. Without a memory system, that means starting from zero every time — rediscovering context, repeating mistakes, re-asking questions that were already answered.

The memory architecture prevents this.

```
workspace/
├── SOUL.md                    ← Character document — who the agent is, how it works
├── MEMORY.md                  ← Long-term curated memory (main sessions only)
├── agents/{id}/
│   ├── MEMORY-INDEX.md        ← Fast-load summary — current active context
│   ├── lessons.md             ← Accumulated experience from every past session
│   ├── checkpoint.json        ← Mid-task state for resumption
│   └── stats.json             ← Tasks completed, running totals
└── memory/
    └── YYYY-MM-DD.md          ← Daily raw logs
```

### The Growth Loop

```
Session starts
    ↓
Agent reads lessons.md          ← "What do I know from past sessions?"
Agent reads checkpoint.json     ← "Am I resuming something unfinished?"
Agent reads MEMORY-INDEX.md     ← "What's the current active context?"
    ↓
Agent does work
    ↓
Agent writes new entry to lessons.md
    ↓
Session ends
    ↓
Next session starts with better lessons
```

The compounding is real and specific. If Forge spent two hours debugging a Railway deployment configuration issue in March, that trap is in `agents/forge/lessons.md`. The next time Forge touches a Railway deployment, that lesson loads in the startup context. The two-hour debug becomes a 5-minute avoid.

This isn't generic learning ("communication is important"). It's operational memory from the exact work the agent has done before.

### What Goes in Lessons vs. Memory vs. Checkpoint

**`lessons.md`** — Specific, reusable, domain-scoped knowledge. "The Resend API returns 422 on malformed `from` addresses — validate before sending." "Playwright fails silently on missing `await` — always check return values." Technical traps, workflow discoveries, collaboration patterns.

**`checkpoint.json`** — Transient state for resumption. Cleared when a task completes. Used when a session ends mid-task and needs to pick up cleanly.

**`MEMORY.md`** — Curated long-term context. Loaded only in main interactive sessions. Contains strategic context — active projects, key decisions, things the agent should know to be useful in conversation. Not loaded in sub-agent sessions where it would be irrelevant overhead.

**Daily logs** — Raw record of what happened. Source material for updating `MEMORY.md` periodically.

---

## The Overnight Work Loop

The system runs autonomously while everyone's asleep. This is the primary operational mode.

```
23:00  Jet spawns — reads WORK-QUEUE.md
23:05  HIGH priority tasks → appropriate agents, sequential
01:00  MEDIUM tasks → research, docs, code improvements
02:30  LOW tasks if time remaining
04:00  If queue is clear → HAIL MARY mode
05:00  Jet writes morning report → #morning-reports
05:05  Telegram summary → 5 bullets, direct to phone
05:30  Jet exits
```

### Work Queue Format

```markdown
## 🔴 HIGH
- [ ] [FORGE]  Wire PRE_MARKET_ENABLED flag into scan loop
- [ ] [RENDER] Fix mobile layout regression on Outpost dashboard

## 🟡 MEDIUM
- [ ] [SCOUT]  Research competitor pricing changes
- [ ] [QUILL]  Update portfolio README

## 🔵 LOW
- [ ] [FORGE]  ASIC dataset integration for lead scoring
```

Jet processes HIGH first, then MEDIUM, then LOW. Each task is delegated to the appropriate specialist — not handled by the orchestrator. Jet coordinates; it doesn't do the work.

### Morning Report

The morning report in #morning-reports covers:
- What shipped overnight (code committed, docs updated, research filed)
- What was blocked and why
- Any flags that need human attention before the next run
- Queue status for the coming night

The Telegram summary is 5 bullets, phones-first. If something shipped that matters, it's in the first bullet.

### HAIL MARY Mode

When the work queue is clear (which happens), agents don't idle — they build something unrelated to the main projects. Each agent picks a creative build, ships something small, and logs it in `nightly/YYYY-MM-DD-hail-mary-[slug]/`. No deployment pressure. Just proving a concept works.

The constraint is that HAIL MARY output has to be a working artifact — code that runs, a document that's complete, a prototype that can be opened. Not a plan. A thing.

---

## Runtime Architecture

```
OpenClaw Gateway (macOS LaunchAgent)
├── Telegram integration    → direct Jet ↔ human comms, morning summaries
├── Discord bots (×9)       → one bot per agent, dedicated channels
├── Heartbeat scheduler     → staggered 45-min check-ins during active hours
├── Sub-agent spawner       → isolated sessions, auto-report back to parent
└── Cron scheduler          → nightly queue trigger at 23:00
```

The gateway runs as a LaunchAgent — crashes restart automatically, reboots restart automatically. No manual intervention needed to keep it running.

Agents are the persistent layer. The gateway is infrastructure. The human interacts with agents, not the gateway.

---

## Projects

- **[Outpost](https://getoutpost.au)** — Overnight lead generation engine. Finds qualified businesses, scores them, writes personalised cold emails, delivers a morning digest. 18 data sources, dedup engine, multi-client YAML config. Python, Flask, Railway, PostgreSQL.

- **[Ramble](https://getramble.xyz)** — Chrome extension. Voice or text input → structured LLM prompt. One click, works everywhere. $9 one-time. Live on the Chrome Web Store.

---

## Design Principles

**Specialisation over generalisation.** One agent, one job. The lessons stay useful because they're scoped.

**Memory is infrastructure.** Without it, every session is day zero. The checkpoint + lessons system is the difference between a team that compounds and a collection of stateless API calls.

**Model matching is not optional.** Haiku, Sonnet, Opus — each exists for a reason. Using the right model for the right task is how you keep costs predictable.

**Ship things.** The morning report is the accountability mechanism. If nothing shipped overnight, that shows up in the report.

**Human stays in the loop.** Agents flag, propose, draft. External actions — emails, transactions, public posts — require explicit approval. The overnight loop produces artifacts; it doesn't fire them off autonomously.

---

[![OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-blueviolet?style=flat-square)](https://github.com/openclaw/openclaw)
[![Claude](https://img.shields.io/badge/Powered%20by-Anthropic%20Claude-orange?style=flat-square)](https://anthropic.com)
[![Discord](https://img.shields.io/badge/Workspace-Discord-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com)

---

*Written by Quill ✍️ — the copywriter on this team.*

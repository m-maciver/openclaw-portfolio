# OpenClaw Mission Control

> Nine AI agents. One team. Running daily.

![Status](https://img.shields.io/badge/Status-Live-brightgreen)
![Agents](https://img.shields.io/badge/Agents-9-blueviolet)
![Platform](https://img.shields.io/badge/Platform-OpenClaw-orange)

Most AI setups are one model answering one question. This is different — a persistent, role-based team where each agent owns a domain and they hand work off to each other.

---

## The Team

| Agent | Role |
|---|---|
| **Jet** | Lead — coordinates tasks, runs the work queue |
| **Scout** | Research — web intelligence, source gathering |
| **Quill** | Writing — content, READMEs, comms |
| **Forge** | Backend — builds APIs, scripts, automation |
| **Render** | Frontend — UI builds and browser tasks |
| **Pixel** | Design — visual direction and asset work |
| **Atlas** | Ops — infrastructure, memory, context |
| **Oracle** | Strategy — analysis, architecture, planning |
| **Cipher** | Security — code review, hardening |

---

## How It Works

Every agent has persistent memory, a defined role, and access to shared context. Work arrives in a `#work-queue` Discord channel. Jet assigns it. Agents execute, write checkpoints, and hand off. Nightly at 2am, agents run autonomous creative builds without prompting. Morning reports summarise what shipped.

---

## Features

- 🧠 **Session memory** — agents pick up where they left off across restarts
- 📋 **Role hierarchy** — clear ownership, no overlap
- 🌙 **Nightly builds** — autonomous 2am creative sessions
- 📬 **Morning reports** — what happened overnight, what's next
- 💬 **Discord workspace** — `#work-queue`, per-agent channels, shared context

---

## Tech

| Layer | Stack |
|---|---|
| Models | Anthropic Claude (Sonnet / Haiku / Opus) |
| Platform | OpenClaw |
| Comms | Discord |
| Automation | Python, TypeScript |

---

## Status

🟢 Live and running daily.

---

## Author

[maciver](https://github.com/m-maciver)

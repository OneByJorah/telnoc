<div align="center">

![telnoc banner](docs/assets/banner.svg)

# telnoc

*Formerly TeleOps.*

**A unified NOC platform for Telegram — monitor agents, discover SNMP devices, run a live dashboard, and manage Linux and Windows hosts from chat commands.**

<a href="https://github.com/OneByJorah/telnoc/stargazers"><img src="https://img.shields.io/github/stars/OneByJorah/telnoc?style=flat-square" alt="Stars"></a>
<a href="https://github.com/OneByJorah/telnoc/commits"><img src="https://img.shields.io/github/last-commit/OneByJorah/telnoc?style=flat-square" alt="Last commit"></a>
<img src="https://img.shields.io/github/license/OneByJorah/telnoc?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
<img src="https://img.shields.io/badge/Flask-SocketIO-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask-SocketIO">
<img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker Compose">

</div>

![telnoc dashboard](docs/screenshots/dashboard-desktop.png)

## What This Is

telnoc turns Telegram into a network operations console. A bot fronts a set of cross-platform agents, an SNMP discovery engine, and a live web dashboard, so you can check host health, run signed commands, and get threshold alerts without opening a terminal or a monitoring portal.

It is built for small NOC and homelab operators who want lightweight, self-hosted infrastructure monitoring that reaches them where they already are — chat.

## Quick Start

```bash
git clone https://github.com/OneByJorah/telnoc.git
cd telnoc

cp .env.example .env        # set TELEGRAM_BOT_TOKEN + ADMIN_CHAT_IDS to enable the bot
docker compose up -d --build
```

Open **http://localhost:5000** for the dashboard. The agent server listens on **http://localhost:8080**.

> [!TIP]
> telnoc serves the dashboard and agent server even without a real Telegram token. In that mode it seeds synthetic demo data so you can explore the UI immediately. Set `TELEGRAM_BOT_TOKEN` and `ADMIN_CHAT_IDS` to enable the Telegram control plane.

## Features

- **Telegram control plane** — admin-gated commands for status, agents, SNMP, and per-host actions.
- **Cross-platform agents** — a stdlib Linux agent and a PowerShell 5.1 Windows agent with HMAC-SHA256 signed command dispatch.
- **SNMP discovery** — automated device discovery and polling over SNMP v1/v2c/v3.
- **Live dashboard** — Flask + SocketIO UI with REST polling fallback, served on port 5000.
- **Alert management** — CPU/memory/disk thresholds, cooldown, and agent offline detection.
- **Agent server** — self-registration, heartbeat, and installer downloads on port 8080.
- **Windows host management** — AD, DNS, and DHCP actions from the Windows agent.
- **Redis-backed state** — durable job/state storage with append-only persistence.
- **Dashboard-only / demo mode** — run locally without a Telegram token for screenshots and smoke tests.

## Architecture

```
Telegram Admin ──commands──▶ NetBot ──HMAC-signed commands──▶ Agents (Linux/Windows)
                                │
      NetworkScanner ──────────▶│  probes http://<host>:7845/info
      SNMPScanner ──────────────▶│  polls v2c communities
                                ▼
              Agent Server (:8080)  ·  Dashboard (:5000)  ·  Alerts → Telegram
```

Agents register themselves (`POST /agent/register`) or are discovered by subnet scan, report heartbeats every 25 s, and execute signed commands (`stats`, `services`, `firewall`, `docker_ps`, AD/DNS/DHCP on Windows, `cmd` on Linux).

## Configuration

Primary configuration lives in **`config/config.yaml`** (seeded from `config/config.yaml.example` on first run). Environment variables override the YAML values.

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | *(empty)* | Bot token from BotFather (overrides YAML) |
| `ADMIN_CHAT_IDS` | *(empty)* | Comma-separated Telegram user IDs with admin access |
| `SECRET_KEY` | *(empty)* | HMAC secret shared with agents (overrides YAML) |
| `REDIS_HOST` / `REDIS_PORT` | `redis` / `6379` | Redis connection |
| `REDIS_PASSWORD` | *(generated)* | Redis auth password |
| `DASHBOARD_PORT` | `5000` | Web dashboard port |
| `AGENT_PORT` | `8080` | Agent server port |
| `SNMP_COMMUNITY` | `public` | Default SNMP community |
| `SCAN_INTERVAL_MINUTES` | `60` | Network discovery interval |
| `TELNOC_DEMO` | `0` | Set `1` to seed synthetic agents/SNMP devices |

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot (admin menu) |
| `/status` | Agent & SNMP device status overview |
| `/agents` | List registered agents |
| `/dashboard` | Get dashboard URL |
| `/win <host> [action]` | Windows agent menu or action |
| `/lx <host> [action]` | Linux agent menu or action |
| `/snmp list\|scan\|<ip>` | SNMP devices, scan, or poll one device |
| `/alert` | Alert configuration info |

## API & Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI (port 5000) |
| `/api/agents` | GET | Registered agents |
| `/api/snmp` | GET | Discovered SNMP devices |
| `/api/summary` | GET | Aggregated status summary |
| `/agent/register` | POST | Agent self-registration (port 8080) |
| `/agent/download/linux` | GET | Linux agent installer script |
| `/agent/download/windows` | GET | Windows agent installer script |
| `/install/linux` | GET | Linux install helper |
| `/install/windows` | GET | Windows install helper |
| `/health` | GET | Agent server health |

## Screenshots

| Desktop | Mobile |
|---|---|
| ![Dashboard desktop](docs/screenshots/dashboard-desktop.png) | ![Dashboard mobile](docs/screenshots/dashboard-mobile.png) |

More captures live in [`docs/screenshots/`](docs/screenshots/).

## Use Cases

1. **Homelab operators** — monitor a mixed Linux/Windows fleet from Telegram.
2. **Small NOCs** — combine agent metrics and SNMP devices in one dashboard.
3. **Remote admins** — run signed host commands without a VPN into a jump box.

## Tech Stack

Python 3.11, python-telegram-bot, aiohttp, Flask + Flask-SocketIO, pysnmp, Redis, SQLAlchemy, PowerShell (Windows agent), Docker Compose.

## Security

Agent `/command` endpoints require HMAC-SHA256 signatures over `timestamp:body` with a ±5-minute freshness window. The dashboard and agent server expose operational data without authentication — do not expose ports 5000/8080 to untrusted networks. See [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). [Open an issue](https://github.com/OneByJorah/telnoc/issues) to report a bug or request a feature.

## License

MIT — see [LICENSE](LICENSE).

## Connect

- [jorahone.com](https://jorahone.com)
- [GitHub Org](https://github.com/OneByJorah)
- [info@jorahone.com](mailto:info@jorahone.com)

#!/usr/bin/env python3
"""
telnoc — Telegram Network Monitoring & Control Agent
Main entry point
"""

import asyncio
import logging
import os
import sys
import types
from pathlib import Path

import yaml
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# These must follow the sys.path.insert above, so E402 is expected here.
from bot.demo import seed_demo_data  # noqa: E402
from bot.handlers import (  # noqa: E402
    agents_handler,
    alert_handler,
    callback_handler,
    dashboard_handler,
    linux_handler,
    snmp_handler,
    start_handler,
    status_handler,
    windows_handler,
)
from bot.scheduler import setup_scheduler  # noqa: E402
from discovery.network_scanner import NetworkScanner  # noqa: E402
from discovery.snmp_scanner import SNMPScanner  # noqa: E402

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/netbot.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("telnoc.main")

# ── Config ───────────────────────────────────────────────────────────────────


PLACEHOLDER_TOKENS = {
    "",
    "YOUR_TELEGRAM_BOT_TOKEN",
    "change_me_your_telegram_bot_token",
    "demo",
}


def load_config() -> dict:
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        log.error("config/config.yaml not found. Copy config.yaml.example and fill in values.")
        sys.exit(1)
    with open(config_path) as f:
        cfg = yaml.safe_load(f) or {}

    # Environment overrides (.env loaded by docker-entrypoint.sh)
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        cfg.setdefault("bot", {})["token"] = token

    admins = os.environ.get("ADMIN_CHAT_IDS", "")
    ids = [int(x.strip()) for x in admins.split(",") if x.strip().lstrip("-").isdigit()]
    if ids:
        cfg.setdefault("bot", {})["admin_ids"] = ids

    secret = os.environ.get("SECRET_KEY")
    if secret:
        cfg.setdefault("server", {})["secret_key"] = secret

    return cfg


# ── Background services ───────────────────────────────────────────────────────


async def start_background_services(application):
    """Start scanner, SNMP, agent server, and dashboard."""
    cfg = application.bot_data["config"]
    log.info("🚀 telnoc starting up...")

    # Start network scanner
    scanner = NetworkScanner(cfg)
    scanner.set_agent_store(application.bot_data["agents"])
    application.bot_data["scanner"] = scanner
    asyncio.create_task(scanner.start_background_scan())

    # Start SNMP scanner
    snmp = SNMPScanner(cfg)
    snmp.set_device_store(application.bot_data["snmp_devices"])
    application.bot_data["snmp"] = snmp
    asyncio.create_task(snmp.start_background_poll())

    # Agent registration & download server
    try:
        from bot.agent_server import start_agent_server
        await start_agent_server(
            application.bot_data["agents"], application.bot_data["snmp_devices"], cfg
        )
    except Exception as e:
        log.error(f"Agent server failed to start: {e}")

    # Web dashboard (runs in a background thread)
    if cfg.get("dashboard", {}).get("enabled", False):
        try:
            import threading
            from dashboard.app import start_dashboard
            t = threading.Thread(
                target=start_dashboard,
                args=(application.bot_data["agents"], application.bot_data["snmp_devices"], cfg),
                daemon=True,
            )
            t.start()
        except Exception as e:
            log.error(f"Dashboard failed to start: {e}")

    log.info("✅ telnoc ready. All systems go.")


# Telegram post-init hook delegates to shared startup.
async def post_init(application):
    await start_background_services(application)


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    os.makedirs("logs", exist_ok=True)
    cfg = load_config()

    token = cfg.get("bot", {}).get("token", "")
    token_valid = token not in PLACEHOLDER_TOKENS

    if not token_valid:
        log.warning(
            "No valid Telegram bot token configured; running dashboard and agent server only."
        )

    # Build a minimal application-like object so background services can run
    # whether or not the Telegram bot is active. Shared dicts are passed by
    # reference into the dashboard thread, so seeding demo data works live.
    agents = {}
    snmp_devices = {}
    app_stub = types.SimpleNamespace(
        bot_data={
            "config": cfg,
            "agents": agents,
            "snmp_devices": snmp_devices,
        }
    )

    demo_mode = os.environ.get("TELNOC_DEMO", "0") == "1" or not token_valid
    if demo_mode:
        seed_demo_data(agents, snmp_devices)
        if token_valid:
            log.info("Demo mode enabled: seeded synthetic agents and SNMP devices.")

    if token_valid:
        # Full Telegram mode
        app = (
            Application.builder()
            .token(token)
            .post_init(post_init)
            .build()
        )
        app.bot_data["config"] = cfg
        app.bot_data["agents"] = agents
        app.bot_data["snmp_devices"] = snmp_devices

        # ── Command Handlers ─────────────────────────────────────────────────
        app.add_handler(CommandHandler("start",     start_handler))
        app.add_handler(CommandHandler("status",    status_handler))
        app.add_handler(CommandHandler("agents",    agents_handler))
        app.add_handler(CommandHandler("dashboard", dashboard_handler))
        app.add_handler(CommandHandler("win",       windows_handler))
        app.add_handler(CommandHandler("lx",        linux_handler))
        app.add_handler(CommandHandler("snmp",      snmp_handler))
        app.add_handler(CommandHandler("alert",     alert_handler))

        # Inline keyboard callbacks
        app.add_handler(CallbackQueryHandler(callback_handler))

        # Setup scheduled jobs (heartbeat checks, alerts)
        setup_scheduler(app)

        log.info(f"Bot polling started. Admins: {cfg['bot']['admin_ids']}")
        app.run_polling(drop_pending_updates=True)
    else:
        # Dashboard-only mode: start background services on one event loop and
        # keep it alive so the aiohttp agent server and dashboard thread survive.
        async def _keep_alive():
            await post_init(app_stub)
            await asyncio.Event().wait()

        try:
            asyncio.run(_keep_alive())
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

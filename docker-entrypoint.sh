#!/bin/bash
# telnoc Docker Entrypoint
# Seeds config/config.yaml from environment on first run, then starts the app.

set -e

# Prefer values already provided by the runtime (env_file, secrets, etc.).
# If TELEGRAM_BOT_TOKEN is unset, fall back to the legacy interactive/non-interactive
# setup wizard so existing behaviour is preserved.
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
    # If .env doesn't exist, run setup wizard
    if [ ! -f /app/.env ]; then
        echo "============================================"
        echo "  telnoc — First Run Setup"
        echo "============================================"
        echo ""

        # Generate random secrets
        SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        REDIS_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

        # Check if running interactively
        if [ -t 0 ]; then
            # Interactive mode
            echo "┌─ Telegram Bot Configuration ─────────────────────────┐"
            read -p "│ Telegram Bot Token: " BOT_TOKEN
            read -p "│ Admin Chat IDs (comma-separated): " ADMIN_IDS
            echo "└──────────────────────────────────────────────────────┘"

            echo ""
            echo "┌─ Redis Configuration ────────────────────────────────┐"
            read -p "│ Redis host [redis]: " REDIS_HOST
            REDIS_HOST=${REDIS_HOST:-redis}
            read -p "│ Redis port [6379]: " REDIS_PORT
            REDIS_PORT=${REDIS_PORT:-6379}
            echo "└──────────────────────────────────────────────────────┘"

            echo ""
            echo "┌─ Dashboard ─────────────────────────────────────────┐"
            read -p "│ Dashboard port [5000]: " DASH_PORT
            DASH_PORT=${DASH_PORT:-5000}
            read -p "│ Agent port [8080]: " AGENT_PORT
            AGENT_PORT=${AGENT_PORT:-8080}
            echo "└──────────────────────────────────────────────────────┘"
        else
            # Non-interactive mode — use defaults
            echo "Non-interactive mode — using auto-generated defaults"
            echo "⚠️  Set TELEGRAM_BOT_TOKEN and ADMIN_CHAT_IDS in .env for Telegram bot to work"
            BOT_TOKEN=""
            ADMIN_IDS=""
            REDIS_HOST="redis"
            REDIS_PORT=6379
            DASH_PORT=5000
            AGENT_PORT=8080
        fi

        # Write .env
        cat > /app/.env <<EOF
TELEGRAM_BOT_TOKEN=${BOT_TOKEN:-}
ADMIN_CHAT_IDS=${ADMIN_IDS:-}
REDIS_PASSWORD=${REDIS_PASS}
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
DASHBOARD_PORT=${DASH_PORT:-5000}
AGENT_PORT=${AGENT_PORT:-8080}
SECRET_KEY=${SECRET}
LOG_LEVEL=INFO
EOF

        echo ""
        echo "✅ Configuration saved to /app/.env"
        echo "   Redis password: ${REDIS_PASS}"
        echo ""
        echo "⚠️  Save these credentials — they won't be shown again."
        echo "============================================"
    fi

    # Source .env
    set -a
    source /app/.env
    set +a
fi

# Seed config/config.yaml from the example using .env values (bot reads YAML, not .env)
if [ ! -f /app/config/config.yaml ] && [ -f /app/config/config.yaml.example ]; then
    mkdir -p /app/config
    python3 - <<'PYEOF'
import os

import yaml

with open("/app/config/config.yaml.example") as f:
    cfg = yaml.safe_load(f) or {}

token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if token and token not in {"YOUR_TELEGRAM_BOT_TOKEN", "change_me_your_telegram_bot_token"}:
    cfg.setdefault("bot", {})["token"] = token

admins = os.environ.get("ADMIN_CHAT_IDS", "")
ids = [int(x.strip()) for x in admins.split(",") if x.strip().lstrip("-").isdigit()]
if ids:
    cfg.setdefault("bot", {})["admin_ids"] = ids

secret = os.environ.get("SECRET_KEY")
if secret:
    cfg.setdefault("server", {})["secret_key"] = secret

with open("/app/config/config.yaml", "w") as f:
    yaml.safe_dump(cfg, f, default_flow_style=False)
print("Seeded /app/config/config.yaml")
PYEOF
fi

echo "Starting telnoc..."
exec "$@"

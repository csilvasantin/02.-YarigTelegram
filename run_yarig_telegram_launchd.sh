#!/bin/zsh
set -euo pipefail
cd /Users/csilvasantin/Claude/repos/Yarig.Telegram
exec /opt/homebrew/bin/python3.12 -m src.bot

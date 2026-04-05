#!/bin/zsh
set -euo pipefail
LABEL=com.csilvasantin.yarigtelegram
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
ERR_LOG="/Users/Carlos/Documents/Codex/Yarig.Telegram/logs/launchd.err.log"
OUT_LOG="/Users/Carlos/Documents/Codex/Yarig.Telegram/logs/launchd.out.log"

case "${1:-status}" in
  start)
    launchctl bootstrap "gui/$(id -u)" "$PLIST" 2>/dev/null || launchctl kickstart -k "gui/$(id -u)/$LABEL"
    ;;
  stop)
    launchctl bootout "gui/$(id -u)" "$PLIST"
    ;;
  restart)
    launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    ;;
  status)
    launchctl print "gui/$(id -u)/$LABEL"
    ;;
  logs)
    tail -n 60 "$ERR_LOG"
    echo '---OUT---'
    tail -n 60 "$OUT_LOG"
    ;;
  *)
    echo "Uso: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac

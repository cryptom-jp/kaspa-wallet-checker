#!/bin/bash

# Kaspaノード制御スクリプト

PID_FILE="$HOME/KaspaDev/kaspad.pid"

case "$1" in
    start)
        bash "$HOME/KaspaDev/scripts/start_kaspad.sh"
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            kill "$PID" 2>/dev/null
            rm -f "$PID_FILE"
            echo "✅ ノード停止完了 (PID: $PID)"
        else
            echo "⚠️ PIDファイルが見つかりません"
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ ノード動作中 (PID: $PID)"
            else
                echo "❌ ノード停止中（PIDファイルは存在）"
            fi
        else
            echo "❌ ノード停止中"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    *)
        echo "使い方: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac

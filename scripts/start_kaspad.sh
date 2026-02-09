#!/bin/bash

# Kaspaノード自動起動スクリプト

LOG_FILE="$HOME/KaspaDev/logs/kaspad_startup.log"
KASPAD_PATH="$HOME/rusty-kaspa/target/release/kaspad"
PID_FILE="$HOME/KaspaDev/kaspad.pid"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Kaspaノード起動開始" >> "$LOG_FILE"

# 既存プロセス確認
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ノードは既に起動中 (PID: $OLD_PID)" >> "$LOG_FILE"
        exit 0
    fi
fi

# ノード起動
cd "$(dirname "$KASPAD_PATH")"
nohup "$KASPAD_PATH" \
    --rpclisten=127.0.0.1:16110 \
    --rpclisten-json=127.0.0.1:18110 \
    --utxoindex \
    >> "$HOME/KaspaDev/logs/kaspad.log" 2>&1 &

NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - ノード起動完了 (PID: $NEW_PID)" >> "$LOG_FILE"

# 5秒待機して接続確認
sleep 5
if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ノード正常動作中" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - エラー: ノード起動失敗" >> "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

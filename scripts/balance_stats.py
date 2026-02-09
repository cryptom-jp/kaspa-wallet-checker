#!/usr/bin/env python3
"""
残高履歴の統計情報表示
"""

import csv
import os
from datetime import datetime
from collections import defaultdict

CSV_FILE = os.path.expanduser("~/KaspaDev/logs/balance_history.csv")

def analyze_balance_history():
    """残高履歴を分析"""
    if not os.path.exists(CSV_FILE):
        print("❌ CSVファイルが見つかりません")
        return
    
    records = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    if not records:
        print("📊 データがまだありません")
        return
    
    # 基本統計
    total_records = len(records)
    first_record = records[0]
    last_record = records[-1]
    
    # アドレスごとの集計
    by_address = defaultdict(list)
    for record in records:
        by_address[record['address']].append(float(record['balance_kas']))
    
    print("=" * 70)
    print("📊 Kaspa残高履歴 統計情報")
    print("=" * 70)
    print(f"\n📅 記録期間:")
    print(f"  開始: {first_record['timestamp']}")
    print(f"  最新: {last_record['timestamp']}")
    print(f"  記録数: {total_records} 件")
    
    print(f"\n💰 アドレス別統計:")
    for addr, balances in by_address.items():
        addr_short = f"...{addr[-10:]}"
        min_bal = min(balances)
        max_bal = max(balances)
        current_bal = balances[-1]
        change = balances[-1] - balances[0]
        
        print(f"\n  🔑 {addr_short}")
        print(f"     現在: {current_bal:.8f} KAS")
        print(f"     最小: {min_bal:.8f} KAS")
        print(f"     最大: {max_bal:.8f} KAS")
        print(f"     変動: {change:+.8f} KAS")
        print(f"     記録: {len(balances)} 回")
    
    print("\n" + "=" * 70)
    
    # 最近の変動をチェック
    if total_records >= 2:
        recent_changes = []
        for i in range(1, min(10, total_records)):
            prev = float(records[-i-1]['balance_kas'])
            curr = float(records[-i]['balance_kas'])
            if prev != curr:
                recent_changes.append({
                    'time': records[-i]['timestamp'],
                    'change': curr - prev,
                    'balance': curr
                })
        
        if recent_changes:
            print("\n🔔 最近の残高変動:")
            for change in recent_changes[:5]:
                sign = "+" if change['change'] > 0 else ""
                print(f"  {change['time']}: {sign}{change['change']:.8f} KAS → {change['balance']:.8f} KAS")
        else:
            print("\n✅ 最近10件の記録で変動なし")
    
    print()

if __name__ == '__main__':
    analyze_balance_history()

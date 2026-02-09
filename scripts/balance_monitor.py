#!/usr/bin/env python3
"""
定期的な残高チェックスクリプト（サブプロセス版）
"""

import json
import subprocess
import os
import csv
from datetime import datetime
import time

# 監視対象アドレス
ADDRESSES = [
    "kaspa:qqk9m5z05ej8e0j4tmx9geaqw6zeexa46pllgqllv28krv0cpgr9ucl3x5gxp"
]

# CSVファイルパス
CSV_FILE = os.path.expanduser("~/KaspaDev/logs/balance_history.csv")
BALANCE_PY = os.path.expanduser("~/KaspaDev/src/kaspa_wallet/balance.py")
VENV_PYTHON = os.path.expanduser("~/KaspaDev/kaspa_venv/bin/python3")

def save_to_csv(address, balance_sompi, balance_kas):
    """残高をCSVに保存"""
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'address', 'balance_sompi', 'balance_kas'])
        
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            address,
            balance_sompi,
            balance_kas
        ])

def check_balance(address):
    """残高確認"""
    try:
        result = subprocess.run(
            [VENV_PYTHON, BALANCE_PY, address],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            balance_sompi = data['balance_sompi']
            balance_kas = data['balance_kas']
            
            save_to_csv(address, balance_sompi, balance_kas)
            
            print(f"✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                  f"{address[-10:]}: {balance_kas} KAS")
            return balance_sompi
        else:
            print(f"❌ エラー: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 例外発生: {e}")
        return None

def main():
    """メイン処理"""
    print(f"=== 残高監視開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"監視アドレス数: {len(ADDRESSES)}")
    print(f"記録先: {CSV_FILE}")
    print("-" * 60)
    
    for address in ADDRESSES:
        check_balance(address)
        time.sleep(1)
    
    print("-" * 60)

if __name__ == '__main__':
    main()

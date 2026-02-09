#!/usr/bin/env python3
"""
残高変動通知スクリプト（サブプロセス版）
"""

import json
import subprocess
import os
from datetime import datetime

# 監視アドレス
ADDRESS = "kaspa:qqk9m5z05ej8e0j4tmx9geaqw6zeexa46pllgqllv28krv0cpgr9ucl3x5gxp"

# 前回残高記録ファイル
STATE_FILE = os.path.expanduser("~/KaspaDev/logs/last_balance.json")
BALANCE_PY = os.path.expanduser("~/KaspaDev/src/kaspa_wallet/balance.py")
VENV_PYTHON = os.path.expanduser("~/KaspaDev/kaspa_venv/bin/python3")

def load_last_balance():
    """前回残高を読み込み"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_last_balance(address, balance):
    """今回残高を保存"""
    data = load_last_balance()
    data[address] = balance
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def send_notification(title, message):
    """Mac通知を送信"""
    script = f'''
    display notification "{message}" with title "{title}"
    '''
    subprocess.run(['osascript', '-e', script])

def get_balance(address):
    """balance.pyを実行して残高取得"""
    try:
        result = subprocess.run(
            [VENV_PYTHON, BALANCE_PY, address],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"status": "error", "message": result.stderr}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_and_alert(address):
    """残高確認して変動があれば通知"""
    result = get_balance(address)
    
    if result.get('status') != 'success':
        print(f"❌ 残高取得失敗: {result.get('message')}")
        return
    
    current_balance = result['balance_kas']
    last_data = load_last_balance()
    last_balance = last_data.get(address)
    
    if last_balance is None:
        print(f"📊 初回記録: {current_balance} KAS")
        save_last_balance(address, current_balance)
        send_notification("Kaspa残高監視", f"監視開始: {current_balance} KAS")
    elif current_balance != last_balance:
        diff = current_balance - last_balance
        sign = "+" if diff > 0 else ""
        
        print(f"🔔 残高変動検知!")
        print(f"   前回: {last_balance} KAS")
        print(f"   今回: {current_balance} KAS")
        print(f"   差分: {sign}{diff} KAS")
        
        save_last_balance(address, current_balance)
        send_notification(
            "Kaspa残高変動検知！",
            f"{sign}{diff} KAS (現在: {current_balance} KAS)"
        )
    else:
        print(f"✅ 変動なし: {current_balance} KAS")

def main():
    print(f"=== 残高変動チェック: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    check_and_alert(ADDRESS)

if __name__ == '__main__':
    main()

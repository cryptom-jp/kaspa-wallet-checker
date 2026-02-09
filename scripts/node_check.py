import requests
import json

# Kaspaノードに接続（あなたのローカルノード）
url = "http://127.0.0.1:18110"

try:
    # "getBlockDagInfo" = 今のブロックチェーンの状態を聞くコマンド
    response = requests.post(
        url,
        json={"jsonrpc": "2.0", "id": 1, "method": "getBlockDagInfoRequest", "params": {}}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Kaspaノード接続成功！")
        print(f"📊 ブロック高: {data['result']['blockCount']:,}")
        print(f"🌐 仮想親ブロック高: {data['result']['virtualParentHashes'][0][:16]}...")
        print("🚀 ノードは正常稼働中です！")
    else:
        print("❌ 接続エラー:", response.status_code)
        
except Exception as e:
    print("❌ 接続失敗:", str(e))
    print("💡 ヒント: Rusty-Kaspaノード（PID 44981）が動いているか確認してください")

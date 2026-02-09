# Kaspa Wallet Balance Checker 運用マニュアル

## CLI版の使い方
cd ~/KaspaDev && source kaspa_venv/bin/activate && cd src/kaspa_wallet
python3 balance.py kaspa:アドレス

## Web版の使い方
cd ~/KaspaDev && source kaspa_venv/bin/activate && cd server_py
python3 app.py

## ログ確認
tail -f ~/KaspaDev/logs/balance.log
grep ERROR ~/KaspaDev/logs/balance.log

## トラブルシューティング
### ノード確認
ps aux | grep kaspad

### ポート5000使用中の場合
lsof -ti:5000
kill $(lsof -ti:5000)

## バックアップ
cd ~/KaspaDev
tar -czf kaspa_backup_$(date +%Y%m%d).tar.gz src/ server_py/ proto/ requirements.txt README.md docs/

## 設定ファイル
src/kaspa_wallet/config.yaml

## セキュリティ
- 秘密鍵をコードに含めない
- ログファイルのパーミッション確認: chmod 600 logs/*.log

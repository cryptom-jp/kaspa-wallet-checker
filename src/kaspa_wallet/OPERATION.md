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
ps aux | grep kaspad
lsof -ti:5000
kill $(lsof -ti:5000)

## バックアップ
cd ~/KaspaDev
tar -czf kaspa_backup_$(date +%Y%m%d).tar.gz src/ server_py/ proto/ requirements.txt README.md

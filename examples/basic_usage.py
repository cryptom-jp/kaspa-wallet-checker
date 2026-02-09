"""
Kaspa Wallet Balance Checker - Basic Usage Example
"""
from kaspa_wallet.balance import get_balance

# Example 1: Get balance for a single address
address = "kaspa:qryy7tutt284r2uka0264q9c00kd5yc3p87entk9um2dguvfzzh3ykeztznxq"
balance = get_balance(address)
print(f"Balance: {balance} KAS")

# Example 2: Monitor balance changes
# See scripts/balance_monitor.py for full implementation

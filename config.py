import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "SupportUsername")

# Subscription Plans
PLANS = {
    "1week": {"name": "1 Week", "price": 49, "days": 7, "original": 100},
    "3months": {"name": "3 Months", "price": 149, "days": 90, "original": 300},
    "lifetime": {"name": "Lifetime", "price": 249, "days": None, "original": 1000}
}

# Payment Methods
PAYMENT_METHODS = {
    "btc": {"name": "Bitcoin (BTC)", "symbol": "₿"},
    "usdt": {"name": "USDT (TRC20)", "symbol": "💲"},
    "ltc": {"name": "LiteCoin (LTC)", "symbol": "Ł"},
    "doge": {"name": "Dogecoin (DOGE)", "symbol": "Ð"}
}

# Your Wallet Addresses (REPLACE WITH YOUR ACTUAL ADDRESSES)
WALLET_ADDRESSES = {
    "btc": "bc1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "usdt": "TRC20: TXxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "ltc": "ltc1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "doge": "Dxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
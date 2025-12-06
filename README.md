# 📈 Telegram to MetaTrader 5 Trading Bot

A fully automated Python trading bot that listens to trade signals from a specific Telegram channel and executes them instantly on a MetaTrader 5 (MT5) terminal.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![MetaTrader5](https://img.shields.io/badge/Platform-MetaTrader5-green)

## 🚀 Key Features
* **Real-time Signal Parsing:** instantly extracts `Symbol`, `Order Type` (BUY/SELL), `TP`, and `SL` from text messages.
* **Smart Execution:** Connects directly to the MT5 terminal for sub-second trade placement.
* **Symbol Mapping:** Automatically maps Telegram tickers (e.g., "GOLD") to broker symbols (e.g., "XAUUSD").
* **Risk Management:** Configurable lot sizes and slippage protection.
* **Environment Security:** Uses `.env` variables to keep API credentials safe.

## 🛠️ Prerequisites
* Python 3.10 or 3.11
* MetaTrader 5 Terminal (Logged in and "Algo Trading" enabled)
* A Telegram API ID and Hash (from [my.telegram.org](https://my.telegram.org))

## ⚙️ Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Telegram-MT5-Trading-Bot.git](https://github.com/YOUR_USERNAME/Telegram-MT5-Trading-Bot.git)
    cd Telegram-MT5-Trading-Bot
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Credentials**
    Create a `.env` file in the root directory and add your keys:
    ```env
    TG_API_ID=your_api_id_here
    TG_API_HASH=your_api_hash_here
    TG_PHONE=+234XXXXXXXXXX
    TG_CHANNEL=QuartzAcademyIntl
    ```

## ▶️ Usage

1.  Open your **MetaTrader 5** terminal.
2.  Run the bot:
    ```bash
    python main.py
    ```
3.  The bot will log in and start listening for new messages.

## ⚠️ Disclaimer
**Use at your own risk.** Automated trading involves significant financial risk. This software is provided for educational purposes only. Always test on a Demo account before using real funds.

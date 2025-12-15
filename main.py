import os
import re
import asyncio
import logging
import MetaTrader5 as mt5
from telethon import TelegramClient, events
from dotenv import load_dotenv

# 1. Load the environment variables
load_dotenv()

# --- 🔴 PASTE THIS SECTION BELOW ---

# 2. Setup Logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# 3. Initialize Headway MT5 (The Critical Fix)
# This path forces Python to find the correct Headway terminal
headway_path = r"C:\Program Files\Headway MT5 Terminal\terminal64.exe"

if not mt5.initialize(path=headway_path):
    logging.error(f"❌ MT5 Initialization Failed. Error: {mt5.last_error()}")
    logging.error("Check if the path above is correct for your PC.")
    quit()
else:
    logging.info(f"✅ Connected to Headway MT5 Account: {mt5.account_info().login}")
    logging.info("Waiting for Telegram signals...")

# 4. Check Algo Trading Permission
if not mt5.terminal_info().trade_allowed:
    logging.warning("⚠️ WARNING: Algo Trading is OFF! Click the 'Algo Trading' button in MT5.")

# --- 🔴 END OF PASTE ---

# (Your Telegram Client code goes here...)

# 2. Configuration
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
PHONE = os.getenv('TG_PHONE')
CHANNEL_ID = os.getenv('TG_CHANNEL')

# 3. Define the Symbol Map (Update this if needed!)
SYMBOL_MAP = {
    "GOLD": "XAUUSD",
    "XAU": "XAUUSD",
    "BTC": "BTCUSD",
    "BITCOIN": "BTCUSD"
}

# 4. Setup Logging (Helps us see what's happening)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# 5. Initialize the Telegram Client
# We use 'anon' here to match the file you created with login.py
client = TelegramClient('anon', API_ID, API_HASH)

async def execute_trade(action, symbol, sl, tp):
    """Connects to MT5 and places the trade."""
    if not mt5.initialize():
        logging.error("❌ MT5 Initialization failed")
        return

    # Check if symbol is valid
    mt5_symbol = SYMBOL_MAP.get(symbol.upper(), symbol.upper())
    
    # Ensure the symbol is visible in Market Watch
    if not mt5.symbol_select(mt5_symbol, True):
        logging.error(f"❌ Symbol {mt5_symbol} not found in Market Watch!")
        return

    # Prepare the order
    tick = mt5.symbol_info_tick(mt5_symbol)
    if not tick:
        logging.error(f"❌ Could not get price for {mt5_symbol}")
        return

    price = tick.ask if action == "BUY" else tick.bid
    order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": mt5_symbol,
        "volume": 0.03,  # Lot size
        "type": order_type,
        "price": price,
        "sl": float(sl) if sl else 0.0,
        "tp": float(tp) if tp else 0.0,
        "deviation": 20,
        "magic": 234000,
        "comment": "TelegramBot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send the order
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logging.info(f"✅ Trade Placed: {action} {mt5_symbol} @ {price}")
    else:
        logging.error(f"❌ Trade Failed: {result.comment}")

@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    """Listens for new messages in the channel."""
    text = event.message.message.upper()
    logging.info(f"📩 New Message: {text}")

    # Simple logic to find BUY/SELL signals
    if "BUY" in text or "SELL" in text:
        action = "BUY" if "BUY" in text else "SELL"
        
        # Try to find a symbol from our map
        detected_symbol = None
        for key in SYMBOL_MAP:
            if key in text:
                detected_symbol = key
                break
        
        if detected_symbol:
            # Simple regex to find SL and TP numbers
            sl_match = re.search(r'SL:?\s*(\d+(\.\d+)?)', text)
            tp_match = re.search(r'TP:?\s*(\d+(\.\d+)?)', text)
            
            sl = float(sl_match.group(1)) if sl_match else None
            tp = float(tp_match.group(1)) if tp_match else None

            logging.info(f"🔎 Signal Detected: {action} {detected_symbol}")
            await execute_trade(action, detected_symbol, sl, tp)

# 6. START THE BOT
print("🤖 Bot is starting...")
with client:
    print(f"✅ Logged in! Listening to channel: {CHANNEL_ID}")
    client.run_until_disconnected()

import asyncio
import re
import logging
import MetaTrader5 as mt5
from telethon import TelegramClient, events

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
PHONE = os.getenv('TG_PHONE')
CHANNEL_ID = os.getenv('TG_CHANNEL')

# Symbol Map
SYMBOL_MAP = {
    "GOLD": "XAUUSD",
    "XAU": "XAUUSD",
    "NAS100": "USTEC",
    "US30": "DJ30"
}

LOT_SIZE = 0.01
DEVIATION = 20
# ---------------------

# --- LOGGING SETUP ---
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- PARSING ENGINE ---
def parse_signal(text):
    text = text.upper().replace("\n", " ")
    
    # 1. Extract Symbol
    symbol = None
    for tg_name, mt5_name in SYMBOL_MAP.items():
        if tg_name in text:
            symbol = mt5_name
            break
    
    # 2. Extract Action (BUY/SELL)
    action = "BUY" if "BUY" in text else "SELL" if "SELL" in text else None
    
    # 3. Extract TP and SL
    # Regex looks for "TP" or "SL" followed by a number
    tp_match = re.search(r"TP\s*[:\d]*\s*[:=]?\s*([\d.]+)", text)
    sl_match = re.search(r"(?:SL|STOPLSS|STOP LOSS)\s*[:=]?\s*([\d.]+)", text)

    if symbol and action and tp_match and sl_match:
        return {
            "symbol": symbol,
            "action": action,
            "tp": float(tp_match.group(1)),
            "sl": float(sl_match.group(1))
        }
    return None

# --- EXECUTION ENGINE ---
def execute_trade(signal):
    # Initialize MT5
    if not mt5.initialize():
        logger.error(f"MT5 Init Failed: {mt5.last_error()}")
        return

    symbol = signal["symbol"]
    
    # Check if symbol is valid/visible in Market Watch
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Symbol {symbol} not found (Check Market Watch in MT5)")
        return

    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logger.error(f"No price data for {symbol}")
        return

    # Determine Entry Price
    if signal["action"] == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": signal["sl"],
        "tp": signal["tp"],
        "deviation": DEVIATION,
        "magic": 111222,
        "comment": "TelegramBot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send Order
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Trade Failed: {result.comment} (Code: {result.retcode})")
    else:
        logger.info(f"✅ Executed {signal['action']} on {symbol} | Price: {price}")

# --- MAIN LOOP ---
client = TelegramClient('session_name', API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    # Log the incoming message so you know it's working
    logger.info(f"📩 New Message: {event.raw_text[:30]}...") 
    
    signal = parse_signal(event.raw_text)
    
    if signal:
        logger.info(f"Signal Detected: {signal}")
        await asyncio.to_thread(execute_trade, signal)

print("🤖 Bot is connecting...")
client.start(phone=PHONE)
client.run_until_disconnected()

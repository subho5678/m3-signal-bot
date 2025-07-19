import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from tradingview_ta import TA_Handler, Interval, Exchange
import asyncio

# --- Valid 20 Pairs ---
VALID_PAIRS = {
    "eurusd", "audjpy", "eurgbp", "audusd", "eurjpy", "audcad",
    "gbpchf", "eurcad", "eurchf", "gbpaud", "usdcad", "chfjpy",
    "euraud", "gbpcad", "gbpjpy", "audchf", "usdchf", "gbpusd",
    "cadjpy", "usdjpy"
}

# --- TradingView Symbol Mapping ---
PAIR_TO_TV = {
    pair: pair[:3].upper() + "/" + pair[3:].upper() for pair in VALID_PAIRS
}

# --- Analysis Logic (Real-Time M3 TradingView Data) ---
def analyze_pair(pair: str) -> str:
    symbol = PAIR_TO_TV.get(pair.lower())
    if not symbol:
        return "Ignore"

    handler = TA_Handler(
        symbol=symbol,
        screener="forex",
        exchange="FX_IDC",
        interval=Interval.INTERVAL_3_MINUTES
    )

    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        candles = analysis.summary["RECOMMENDATION"]

        if rsi < 30 and candles in ["BUY", "STRONG_BUY"]:
            return "Green"
        elif rsi > 70 and candles in ["SELL", "STRONG_SELL"]:
            return "Red"
        else:
            return "Ignore"
    except Exception as e:
        print(f"Error analyzing {pair}: {e}")
        return "Ignore"

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 M3 Binary Signal Bot Connected to TradingView!\nSend any of the 20 currency pairs (e.g., eurusd, usdjpy) to get a real-time signal.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    if user_input in VALID_PAIRS:
        await update.message.reply_text("⏳ Analyzing market, please wait...")
        result = await asyncio.to_thread(analyze_pair, user_input)
        await update.message.reply_text(f"{user_input.upper()} → {result}")
    else:
        await update.message.reply_text("❌ Invalid pair. Please send one of the 20 valid pairs only.")

# --- Main Bot Setup ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    TOKEN = "8110746695:AAFwLv96U6boiZp3i25RvCYY56VVnggqP3g"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running with real TradingView M3 data...")
    app.run_polling()
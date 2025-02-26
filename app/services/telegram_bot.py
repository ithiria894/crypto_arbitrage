import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from typing import Optional
from monitors import *

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get Telegram Bot Token from environment variable
BOT_TOKEN = "7818833650:AAG94JOiRUOz9n78cubjwUMnKhpWRoLtoUw"
API_BASE_URL = "http://localhost:8000"  # Assume API is running locally

# User state cache (for multi-step operations)
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command, create user"""
    user = update.effective_user
    user_data = {
        "telegram_id": str(user.id),
        "username": user.username or user.first_name
    }
    
    try:
        # Check if user exists
        response = requests.get(f"{API_BASE_URL}/users/telegram/{user_data['telegram_id']}")
        if response.status_code == 200:
            await update.message.reply_text("🎉 Welcome back! Use /help to see available commands")
            return

        # Create new user
        response = requests.post(f"{API_BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            await update.message.reply_text(
                "✅ Account created successfully!\n\n"
                "This bot helps you monitor price differences across multiple exchanges, identifying arbitrage opportunities for the same cryptocurrency. Stay ahead of the market and maximize your profits with real-time alerts! 📈💰\n\n"
                "Use these commands to start monitoring:\n"
                "/add_pair - Add a currency pair to monitor\n"
                "/list_pairs - View your watchlist\n"
                "/remove_pair - Remove a currency pair from your watchlist\n"
                "/add_exchange - Add an exchange to monitor\n"
                "/remove_exchange - Remove an exchange from monitoring\n"
                "/list_available_pairs - View all available currency pairs\n"
                "/list_on_time - List real-time arbitrage opportunities\n"
                "/delete_me - Delete your account and stop monitoring\n"
                "/help - Show all commands"
            )
        else:
            await update.message.reply_text("⚠️ Failed to create account, please try later")

    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text("🔴 Server connection failed, please try later")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = (
        "📚 Available commands:\n\n"
        "/start - Create new account\n"
        "/add_pair - Add a currency pair to monitor\n"
        "/list_pairs - View your watchlist\n"
        "/remove_pair - Remove a currency pair from your watchlist\n"
        "/add_exchange - Add an exchange to monitor\n"
        "/remove_exchange - Remove an exchange from monitoring\n"
        "/list_available_pairs - View all available currency pairs\n"
        "/list_on_time - List real-time arbitrage opportunities\n"
        "/delete_me - Delete your account and stop monitoring\n"
        "/help - Show all commands"
    )
    await update.message.reply_text(help_text)

async def add_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add pair command"""
    user = update.effective_user
    args = context.args
    
    # Validate arguments
    if not args or len(args) < 2:
        await update.message.reply_text(
            "❌ Invalid format! Please use:\n"
            "/add_pair [PAIR] [EXCHANGES]\n"
            "Example: /add_pair BTCUSDT Binance,Kraken"
        )
        return

    pair = args[0].upper()
    exchanges = ",".join(args[1:])  # Combine exchange arguments

    try:
        # Get user ID
        user_id = _get_user_id(user.id)
        if not user_id:
            await update.message.reply_text("❌ Please create account with /start first")
            return

        # Check pair existence
        cp_response = requests.get(f"{API_BASE_URL}/currency_pairs/{pair}")
        if cp_response.status_code != 200:
            await update.message.reply_text(f"❌ Currency pair {pair} does not exist")
            return

        # Create user-pair association
        data = {
            "currency_pair_id": cp_response.json()["id"],
            "selected_exchanges": exchanges
        }
        response = requests.post(
            f"{API_BASE_URL}/user_currency_pairs/{user_id}",
            json=data
        )

        if response.status_code == 200:
            await update.message.reply_text(
                f"✅ Monitoring added:\n"
                f"Pair: {pair}\n"
                f"Exchanges: {exchanges}"
            )
        else:
            await update.message.reply_text("❌ Failed to add, please check input format")

    except Exception as e:
        logger.error(f"Add pair error: {e}")
        await update.message.reply_text("🔴 Server error, please try later")

async def list_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List monitored pairs"""
    user = update.effective_user
    try:
        user_id = _get_user_id(user.id)
        response = requests.get(f"{API_BASE_URL}/user_currency_pairs/{user_id}/with_details")
        
        if response.status_code != 200:
            await update.message.reply_text("❌ Failed to get data")
            return

        pairs = response.json()
        if not pairs:
            await update.message.reply_text("📭 You are not monitoring any pairs yet")
            return

        message = "📋 Your watchlist:\n\n"
        for p in pairs:
            message += (
                f"🔹 {p['pair']}\n"
                f"Exchanges: {p['exchanges']}\n"
                f"Remove with: /remove_pair {p['pair']}\n\n"
            )

        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"List pairs error: {e}")
        await update.message.reply_text("🔴 Server error, please try later")

async def remove_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle remove pair command"""
    user = update.effective_user
    args = context.args
    
    if not args:
        await update.message.reply_text("❌ Please specify pair to remove, example: /remove_pair BTCUSDT")
        return

    pair = args[0].upper()

    try:
        user_id = _get_user_id(user.id)
        if not user_id:
            await update.message.reply_text("❌ Please create account with /start first")
            return

        # Get pair ID
        cp_response = requests.get(f"{API_BASE_URL}/currency_pairs/{pair}")
        if cp_response.status_code != 200:
            await update.message.reply_text(f"❌ Currency pair {pair} does not exist")
            return

        # Delete association
        response = requests.delete(
            f"{API_BASE_URL}/user_currency_pairs/{user_id}/{cp_response.json()['id']}"
        )

        if response.status_code == 200:
            await update.message.reply_text(f"✅ Removed monitoring for {pair}")
        else:
            await update.message.reply_text("❌ Removal failed, confirm pair is in your watchlist")

    except Exception as e:
        logger.error(f"Remove pair error: {e}")
        await update.message.reply_text("🔴 Server error, please try later")

async def update_exchanges(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    """Generic exchange update handler"""
    user = update.effective_user
    args = context.args
    command = update.message.text.split()[0]

    if not args or len(args) < 2:
        await update.message.reply_text(
            f"❌ Invalid format! Please use:\n"
            f"{command} [PAIR] [EXCHANGE]\n"
            f"Example: {command} BTCUSDT Binance"
        )
        return

    pair = args[0].upper()
    exchange = args[1].title()  # Normalize exchange name format

    try:
        user_id = _get_user_id(user.id)
        if not user_id:
            await update.message.reply_text("❌ Please create account with /start first")
            return

        # Get pair ID
        cp_response = requests.get(f"{API_BASE_URL}/currency_pairs/{pair}")
        if cp_response.status_code != 200:
            await update.message.reply_text(f"❌ Currency pair {pair} does not exist")
            return

        # Build update data
        update_data = {
            "new_exchanges": None,
            "exchange_to_add": exchange if action == "add" else None,
            "exchange_to_remove": exchange if action == "remove" else None
        }

        response = requests.put(
            f"{API_BASE_URL}/user_currency_pairs/{user_id}/{cp_response.json()['id']}",
            json=update_data
        )

        if response.status_code == 200:
            verb = "Added" if action == "add" else "Removed"
            await update.message.reply_text(f"✅ Successfully {verb} exchange {exchange}")
        else:
            await update.message.reply_text(f"❌ {verb.capitalize()} failed, check input")

    except Exception as e:
        logger.error(f"Exchange update error: {e}")
        await update.message.reply_text("🔴 Server error, please try later")

async def add_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add exchange"""
    await update_exchanges(update, context, "add")

async def remove_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle remove exchange"""
    await update_exchanges(update, context, "remove")

async def delete_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete user account"""
    user = update.effective_user
    
    try:
        user_id = _get_user_id(user.id)
        if not user_id:
            await update.message.reply_text("❌ Account not found")
            return

        response = requests.delete(f"{API_BASE_URL}/users/{user_id}")
        if response.status_code == 200:
            await update.message.reply_text("🗑️ Your account has been permanently deleted")
        else:
            await update.message.reply_text("❌ Deletion failed, please try later")

    except Exception as e:
        logger.error(f"Delete user error: {e}")
        await update.message.reply_text("🔴 Server error, please try later")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text("🤔 Unrecognized command, use /help to see available commands")

def _get_user_id(telegram_id: int) -> Optional[int]:
    """Get user ID by Telegram ID"""
    try:
        response = requests.get(f"{API_BASE_URL}/users/telegram/{telegram_id}")
        return response.json()["id"] if response.status_code == 200 else None
    except:
        return None

async def list_available_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available pairs and add instructions"""
    try:
        # Get all pairs from database
        response = requests.get(f"{API_BASE_URL}/currency_pairs/")
        pairs = [p["pair"] for p in response.json()]
        
        message = (
            "📊 Available currency pairs:\n" +
            "\n".join(f"• {pair}" for pair in pairs) +
            "\n\nHow to add monitoring:\n"
            "1. Use /add_pair [PAIR] [EXCHANGES]\n"
            "2. Separate exchanges with commas\n"
            "3. Supported exchanges: Upbit, BinanceUS, Bitget, MEXC\n"
            "Example: /add_pair BTCUSDT BinanceUS,MEXC"
        )
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"List available pairs error: {e}")
        await update.message.reply_text("🔴 Failed to get pairs list, please try later")

async def list_on_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Real-time price check"""
    user = update.effective_user
    args = context.args
    
    if not args:
        await update.message.reply_text("❌ Please specify pair, example: /list_on_time BTCUSDT")
        return
    
    pair = args[0].upper()
    capital = 10000  # Default capital
    
    try:
        # Check pair existence
        cp_response = requests.get(f"{API_BASE_URL}/currency_pairs/{pair}")
        if cp_response.status_code != 200:
            await update.message.reply_text(
                f"❌ Currency pair {pair} not found\n"
                "Use /list_available_pairs to see available pairs"
            )
            return
        
        # Get real-time data
        prices = {
            "Upbit": get_upbit_price(f"USDT-{pair}"),
            "BinanceUS": get_binance_us_price(pair),
            "Bitget": get_bitget_price(pair),
            "MEXC": get_mexc_price(pair)
        }
        
        fees = get_fees()
        
        # Calculate arbitrage info
        max_ex, max_price, min_ex, min_price, profit, pct_profit = calculate_profit(
            capital, prices, fees
        )
        
        # Format price information
        price_list = "\n".join(
            f"{ex}: ${price}{' (MAX)' if ex == max_ex else ' (MIN)' if ex == min_ex else ''}"
            for ex, price in prices.items()
        )
        
        message = (
            f"🕒 Real-time prices - {pair}:\n{price_list}\n\n"
            f"Initial capital: ${capital}\n"
            f"Arbitrage profit: ${profit:.2f}\n"
            f"Profit margin: {pct_profit:.2f}%"
        )
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Real-time check error: {e}")
        await update.message.reply_text("🔴 Failed to get real-time data, please try later")

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable must be set")

    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add_pair", add_pair))
    app.add_handler(CommandHandler("list_pairs", list_pairs))
    app.add_handler(CommandHandler("remove_pair", remove_pair))
    app.add_handler(CommandHandler("add_exchange", add_exchange))
    app.add_handler(CommandHandler("remove_exchange", remove_exchange))
    app.add_handler(CommandHandler("delete_me", delete_me))
    app.add_handler(CommandHandler("list_on_time", list_on_time))
    app.add_handler(CommandHandler("list_available_pairs", list_available_pairs))

    # Handle unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Start the bot
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
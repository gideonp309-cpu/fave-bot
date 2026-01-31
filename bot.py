import os
import logging
import random
import string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global states
user_states = {}  # Track user trading states (True = trading, False = stopped)

# ETH address placeholder
ETH_PLACEHOLDER = "0x" + "".join(random.choices("0123456789abcdef", k=40))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message and show buttons when /start is issued."""
    user = update.effective_user
    keyboard = create_main_keyboard()
    
    welcome_text = (
        f"👋 Welcome {user.first_name}!\n\n"
        "🤖 *ETH Trading Bot*\n"
        "Start trading ETH with our automated bot\n\n"
        "📊 *Available Commands:*\n"
        "• /start - Show this menu\n"
        "• /deposit - Deposit ETH\n"
        "• /trade - Start trading\n"
        "• /status - Check trading status\n"
        "• /withdraw - Withdraw profits\n"
    )
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

def create_main_keyboard():
    """Create inline keyboard with 4 buttons"""
    keyboard = [
        [
            InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
            InlineKeyboardButton("📈 Trade", callback_data="trade"),
        ],
        [
            InlineKeyboardButton("⏸️ Stop/Start", callback_data="toggle_trade"),
            InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
        ],
        [
            InlineKeyboardButton("📊 Status", callback_data="status"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "deposit":
        await deposit_command(update, context)
    elif query.data == "trade":
        await trade_command(update, context)
    elif query.data == "toggle_trade":
        await toggle_trading(update, context)
    elif query.data == "withdraw":
        await withdraw_command(update, context)
    elif query.data == "status":
        await status_command(update, context)

async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle deposit button/command"""
    # Generate random deposit address
    random_address = "0x" + ''.join(random.choices('0123456789abcdef', k=40))
    
    deposit_message = (
        "💰 *DEPOSIT ETH*\n\n"
        f"Send ETH to this address:\n"
        f"`{random_address}`\n\n"
        "📝 *Instructions:*\n"
        "1. Copy the address above\n"
        "2. Send ETH from your wallet\n"
        "3. Minimum deposit: 0.1 ETH\n"
        "4. Wait for 3 confirmations\n\n"
        "⚠️ *Only send ETH to this address!*\n"
        "Do not send other tokens."
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            deposit_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
    else:
        await update.message.reply_text(
            deposit_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )

async def trade_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle trade button/command"""
    trade_message = (
        "🚀 *TRADE EXECUTED!*\n\n"
        "✅ Hurry! I'm going into the ETH market now to make profit for you!\n\n"
        "📊 *Trade Details:*\n"
        "• Asset: ETH/USDT\n"
        "• Direction: Long\n"
        "• Entry: Market Price\n"
        "• Leverage: 5x\n"
        "• Risk: 2%\n\n"
        "⏱️ Trade will be monitored automatically.\n"
        "You'll receive notifications on profit targets."
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            trade_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
    else:
        await update.message.reply_text(
            trade_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )

async def toggle_trading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle trading on/off"""
    user_id = update.effective_user.id
    
    # Toggle state
    if user_id not in user_states:
        user_states[user_id] = True  # Start as trading
    else:
        user_states[user_id] = not user_states[user_id]
    
    status = "✅ TRADING" if user_states[user_id] else "⏸️ STOPPED"
    
    toggle_message = (
        f"🔄 *TRADING STATUS UPDATED*\n\n"
        f"Current Status: *{status}*\n\n"
        f"{'✅ Trading bot is now active and executing trades.' if user_states[user_id] else '⏸️ Trading bot has been paused. No new trades will be executed.'}\n\n"
        f"Click again to toggle."
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            toggle_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
    else:
        await update.message.reply_text(
            toggle_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle withdraw button/command"""
    # Store that we're waiting for address
    context.user_data['awaiting_address'] = True
    
    withdraw_message = (
        "💸 *WITHDRAW PROFITS*\n\n"
        "Please send your ETH address where you want to receive:\n\n"
        "📝 *Format:* `0xYourEthereumAddress`\n\n"
        f"💰 *Pending Withdrawal:* 10 ETH\n"
        f"⏱️ *Processing Time:* 5-10 minutes\n"
        f"📦 *Network Fee:* 0.001 ETH"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            withdraw_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Back", callback_data="back")]])
        )
    else:
        await update.message.reply_text(
            withdraw_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Back", callback_data="back")]])
        )

async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ETH address input"""
    if context.user_data.get('awaiting_address'):
        eth_address = update.message.text
        
        # Simple validation (just check if it looks like an ETH address)
        if eth_address.startswith('0x') and len(eth_address) == 42:
            success_message = (
                "🎉 *WITHDRAWAL CONFIRMED!*\n\n"
                f"✅ Congratulations! 10 ETH profit is coming your way!\n\n"
                f"📬 *To Address:* `{eth_address[:10]}...{eth_address[-8:]}`\n"
                f"💰 *Amount:* 10 ETH\n"
                f"📊 *Transaction ID:* 0x{''.join(random.choices('0123456789abcdef', k=64))}\n"
                f"⏱️ *Estimated Arrival:* 5-10 minutes\n\n"
                f"🔄 Refresh your wallet to see the balance."
            )
            
            await update.message.reply_text(
                success_message,
                parse_mode="Markdown",
                reply_markup=create_main_keyboard()
            )
            
            # Reset state
            context.user_data['awaiting_address'] = False
        else:
            await update.message.reply_text(
                "⚠️ Please enter a valid ETH address (should start with 0x and be 42 characters).",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Back", callback_data="back")]])
            )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show trading status"""
    user_id = update.effective_user.id
    trading_status = user_states.get(user_id, False)
    
    status_message = (
        "📊 *TRADING STATUS*\n\n"
        f"🤖 *Bot Status:* {'✅ ACTIVE' if trading_status else '⏸️ PAUSED'}\n"
        f"💰 *Balance:* 15.5 ETH\n"
        f"📈 *Active Trades:* 3\n"
        f"💵 *Total Profit:* 10 ETH\n"
        f"📅 *Last Trade:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"🔔 *Notifications:* Enabled\n"
        f"⚡ *Response Time:* < 1s"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            status_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
    else:
        await update.message.reply_text(
            status_message,
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )

async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back button"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        await query.edit_message_text(
            "Main Menu",
            reply_markup=create_main_keyboard()
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = (
        "🤖 *ETH Trading Bot Help*\n\n"
        "📋 *Commands:*\n"
        "/start - Start the bot\n"
        "/deposit - Deposit ETH\n"
        "/trade - Execute trade\n"
        "/status - Check status\n"
        "/withdraw - Withdraw profits\n"
        "/help - Show this message\n\n"
        "📱 *How to use:*\n"
        "1. Deposit ETH using the Deposit button\n"
        "2. Start trading with Trade button\n"
        "3. Monitor your trades\n"
        "4. Withdraw profits anytime\n\n"
        "⚠️ *Disclaimer:* This is a demo bot for educational purposes."
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main() -> None:
    """Start the bot."""
    # Get token from environment variable
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("deposit", deposit_command))
    application.add_handler(CommandHandler("trade", trade_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("withdraw", withdraw_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(deposit|trade|toggle_trade|withdraw|status)$"))
    application.add_handler(CallbackQueryHandler(back_button, pattern="^back$"))
    
    # Add message handler for ETH addresses
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    
    # Start the Bot
    PORT = int(os.environ.get('PORT', 8443))
    
    if os.getenv('RENDER'):  # Running on Render
        # Use webhook for Render deployment
        webhook_url = f"https://{os.getenv('RENDER_SERVICE_NAME')}.onrender.com/{TOKEN}"
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Use polling for local development
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

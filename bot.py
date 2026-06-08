import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from config import *
from database import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with main menu"""
    user = update.effective_user
    user_id = user.id
    
    # Check if user exists in database
    db_user = get_user(user_id)
    if not db_user:
        create_user(user_id, user.username, user.first_name)
    
    # Create main menu keyboard
    keyboard = [
        [
            InlineKeyboardButton("🛒 BUY VIP", callback_data="buy_vip"),
            InlineKeyboardButton("👤 My Account", callback_data="my_account")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("🆘 Support", callback_data="support")
        ],
        [
            InlineKeyboardButton("🌐 Languages", callback_data="languages")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
📈 **Welcome to Signal Bot, {user.first_name}!** 📈

Get ready to elevate your trading game. I provide **HIGH-QUALITY** premium signals designed to maximize your profits.

✅ **VIP Subscription Includes:**
✅ High-Quality Premium Signals
✅ Success Rate +75%
✅ 30+ Signals Daily (Faster Than Others)
✅ Entry – Targets – StopLoss – Leverage

📦 **Available Plans (Limited Offer):**
▫️ 1 Week Access — ~~$100~~ **$49**
▫️ 3 Months Access — ~~$300~~ **$149**
▫️ Lifetime Access — ~~$1,000~~ **$249**

🛡️ *Disclaimer: Trading involves risk. Past performance does not guarantee future results.*
"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    print(f"Button clicked: {data}")
    
    if data == "buy_vip":
        await show_plans(update, context)
    elif data == "my_account":
        await show_account(update, context)
    elif data == "stats":
        await show_stats(update, context)
    elif data == "support":
        await show_support(update, context)
    elif data == "languages":
        await show_languages(update, context)
    elif data == "back_to_menu":
        await back_to_menu(update, context)
    elif data.startswith("plan_"):
        await show_payment_methods(update, context, data)
    elif data.startswith("pay_"):
        await process_payment_selection(update, context, data)
    elif data.startswith("upload_proof_"):
        await upload_proof_handler(update, context, data)
    else:
        print(f"Unknown callback: {data}")

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show subscription plans"""
    query = update.callback_query
    
    keyboard = [
        [
            InlineKeyboardButton("📅 1 Week - $49", callback_data="plan_1week"),
            InlineKeyboardButton("📆 3 Months - $149", callback_data="plan_3months")
        ],
        [
            InlineKeyboardButton("♾️ Lifetime - $249", callback_data="plan_lifetime")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
💎 VIP Subscription Plans

Choose the plan that works best for you:

┌─────────────────────────────────────┐
│  📅 1 Week      — $49  (was $100)   │
│  📆 3 Months    — $149 (was $300)   │
│  ♾️ Lifetime    — $249 (was $1,000) │
└─────────────────────────────────────┘

Select your plan above to continue to payment.
"""
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE, plan_callback):
    """Show payment methods for selected plan"""
    query = update.callback_query
    plan_key = plan_callback.replace("plan_", "")
    plan = PLANS[plan_key]
    
    # Store selected plan in context.user_data
    context.user_data['selected_plan'] = plan_key
    
    keyboard = [
        [
            InlineKeyboardButton("₿ BTC (Bitcoin)", callback_data=f"pay_btc_{plan_key}"),
            InlineKeyboardButton("💲 USDT (Tether)", callback_data=f"pay_usdt_{plan_key}")
        ],
        [
            InlineKeyboardButton("Ł LTC (LiteCoin)", callback_data=f"pay_ltc_{plan_key}"),
            InlineKeyboardButton("Ð DOGE (Dogecoin)", callback_data=f"pay_doge_{plan_key}")
        ],
        [InlineKeyboardButton("🔙 Back to Plans", callback_data="buy_vip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
💰 Payment for {plan['name']} Plan

Amount: ${plan['price']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select your payment method below:
"""
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    """Process payment method selection"""
    query = update.callback_query
    
    print(f"Processing payment: {data}")
    
    parts = data.split("_")
    
    if len(parts) < 3:
        print(f"Error: Invalid format - {parts}")
        await query.edit_message_text("❌ Invalid payment option. Please go back and try again.")
        return
    
    method = parts[1]  # btc, usdt, ltc, doge
    plan_key = parts[2]  # 1week, 3months, lifetime
    
    print(f"Method: {method}, Plan: {plan_key}")
    
    # Validate plan_key
    if plan_key not in PLANS:
        print(f"Invalid plan: {plan_key}")
        await query.edit_message_text("❌ Invalid plan. Please go back and select a plan again.")
        return
    
    # Validate method
    if method not in PAYMENT_METHODS:
        print(f"Invalid method: {method}")
        await query.edit_message_text("❌ Invalid payment method. Please go back and try again.")
        return
    
    plan = PLANS[plan_key]
    method_info = PAYMENT_METHODS[method]
    address = WALLET_ADDRESSES.get(method, "NOT_CONFIGURED")
    
    if address == "NOT_CONFIGURED":
        await query.edit_message_text(f"❌ {method.upper()} payment is not configured yet. Please contact @{SUPPORT_USERNAME}")
        return
    
    text = f"""
💳 Complete Your Payment

Plan: {plan['name']} (${plan['price']})
Method: {method_info['symbol']} {method_info['name']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Send exactly ${plan['price']} in {method_info['name']} to:

{address}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After sending your payment:

1. Take a screenshot of the transaction
2. Click the "Upload Proof" button below
3. Send the screenshot directly in this chat

We will verify and activate your subscription within 15-30 minutes.
"""
    
    keyboard = [
        [InlineKeyboardButton("📸 Upload Payment Proof", callback_data=f"upload_proof_{method}_{plan_key}")],
        [InlineKeyboardButton("🔙 Back to Plans", callback_data="buy_vip")],
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)
    print(f"Payment details shown for {method} - {plan['name']}")

async def upload_proof_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    """Handle upload proof button - asks user to send screenshot"""
    query = update.callback_query
    
    parts = data.split("_")
    if len(parts) >= 3:
        method = parts[1]
        plan_key = parts[2]
        plan = PLANS.get(plan_key, {"name": "Unknown", "price": "Unknown"})
        method_info = PAYMENT_METHODS.get(method, {"name": method.upper()})
        
        print(f"Upload proof - Method: {method}, Plan Key: {plan_key}")  # Debug
        
        # Store payment info in context
        context.user_data['pending_payment'] = {
            'method': method,
            'plan_key': plan_key,
            'plan_name': plan['name'],
            'price': plan['price'],
            'method_name': method_info['name']
        }
        
        text = f"""
📸 Send Your Payment Proof

Please send a screenshot of your {method_info['name']} payment for the {plan['name']} plan (${plan['price']}).

Instructions:
1. Take a clear screenshot showing the transaction
2. Send it as a PHOTO in this chat
3. Our support will review and activate your subscription

You will receive confirmation within 15-30 minutes.
"""
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="buy_vip")],
            [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof photos sent by users"""
    user = update.effective_user
    photo = update.message.photo[-1]
    
    # Get pending payment info from context
    pending = context.user_data.get('pending_payment', {})
    
    print(f"Pending payment data: {pending}")  # Debug
    
    if not pending:
        await update.message.reply_text(
            "❌ Please use the bot buttons to make a payment first.\n\n"
            "Send /start to begin."
        )
        return
    
    plan_key = pending.get('plan_key', '1week')
    print(f"Plan key to save: {plan_key}")  # Debug
    
    # Store payment record in database
    try:
        add_payment_record(
            user_id=user.id,
            plan_key=plan_key,
            amount=pending.get('price', 0),
            method=pending.get('method', 'unknown'),
            transaction_id=f"photo_proof_{datetime.now().timestamp()}"
        )
        print("✅ Payment record added successfully!")
    except Exception as e:
        print(f"❌ Error adding payment record: {e}")
        await update.message.reply_text(f"❌ Error recording payment. Please contact @{SUPPORT_USERNAME}")
        return
    
    # Prepare message for admin/support
    caption = f"""
📸 NEW PAYMENT PROOF RECEIVED!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 User Info:
   • Name: {user.first_name} {user.last_name or ''}
   • Username: @{user.username if user.username else 'N/A'}
   • User ID: {user.id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Payment Details:
   • Plan: {pending.get('plan_name', 'Unknown')}
   • Amount: ${pending.get('price', 'Unknown')}
   • Method: {pending.get('method_name', 'Unknown').upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶️ To activate: /verify {user.id} {plan_key}
"""
    
    # Send to owner (you)
    await context.bot.send_photo(
        chat_id=OWNER_ID,
        photo=photo.file_id,
        caption=caption,
        parse_mode=None
    )
    
    # Also forward to support username
    if SUPPORT_USERNAME:
        try:
            await context.bot.send_photo(
                chat_id=f"@{SUPPORT_USERNAME}",
                photo=photo.file_id,
                caption=f"Payment proof from @{user.username or user.first_name}",
                parse_mode=None
            )
        except Exception as e:
            print(f"Could not send to support username: {e}")
    
    # Confirm to user
    await update.message.reply_text(
        f"✅ Payment proof received! 📸\n\n"
        f"Our support team will verify your payment for the {pending.get('plan_name', '')} plan.\n\n"
        f"⏱️ Expected verification time: 15-30 minutes\n\n"
        f"Once verified, you will receive the VIP channel link.\n\n"
        f"📞 For questions: @{SUPPORT_USERNAME}"
    )
    
    # Clear pending payment from context
    context.user_data['pending_payment'] = {}
    
    # Notify admin with a separate text message
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"🔔 Payment proof received from @{user.username or user.first_name}\nUse /verify {user.id} {plan_key} to activate",
        parse_mode=None
    )

async def show_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user account information"""
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)
    is_active = is_subscription_active(user_id)
    
    if is_active and user:
        expiry = user["subscription_expiry"]
        expiry_text = datetime.fromisoformat(expiry).strftime("%Y-%m-%d") if expiry else "Never"
        text = f"""
👤 My Account

✅ Status: Active
📅 Plan: {user['subscription_plan']}
⏰ Expires: {expiry_text}
"""
    else:
        text = """
👤 My Account

❌ Status: Inactive

💡 No active subscription found.

Click BUY VIP to get started!
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    query = update.callback_query
    active_count = get_active_subscribers()
    
    text = f"""
📊 Bot Statistics

📈 Total Signals Sent: 1,247
✅ Success Rate (30d): 78.5%
🎯 Avg Profit per Signal: +12.4%
👥 Active Subscribers: {active_count}
⭐ Average Rating: 4.8/5
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show support information"""
    query = update.callback_query
    
    text = f"""
🆘 Support Center

📱 Telegram: @{SUPPORT_USERNAME}
⏰ Response Time: 15-30 minutes (24/7)

FAQs:
How do I get signals after payment?
→ Send payment proof through the bot after selecting your plan

What payment methods?
→ BTC, USDT, LTC, DOGE
"""
    
    keyboard = [
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection"""
    query = update.callback_query
    
    text = "🌐 Select Language:"
    
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("Español 🇪🇸", callback_data="lang_es")],
        [InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    
    keyboard = [
        [
            InlineKeyboardButton("🛒 BUY VIP", callback_data="buy_vip"),
            InlineKeyboardButton("👤 My Account", callback_data="my_account")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("🆘 Support", callback_data="support")
        ],
        [
            InlineKeyboardButton("🌐 Languages", callback_data="languages")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
📈 Welcome to Signal Bot! 📈

Get ready to elevate your trading game. I provide HIGH-QUALITY premium signals.

✅ VIP Subscription Includes:
✅ High-Quality Premium Signals
✅ Success Rate +75%
✅ 30+ Signals Daily
✅ Entry – Targets – StopLoss – Leverage

📦 Available Plans (Limited Offer):
▫️ 1 Week — $49 (was $100)
▫️ 3 Months — $149 (was $300)
▫️ Lifetime — $249 (was $1,000)
"""
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode=None)

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to verify payment and activate subscription"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /verify <user_id> <plan_key>\n\n"
            "Plan keys: 1week, 3months, lifetime\n\n"
            "Example: /verify 123456789 1week"
        )
        return
    
    try:
        target_user_id = int(args[0])
        plan_key = args[1]
        
        if plan_key not in PLANS:
            await update.message.reply_text("Invalid plan key. Use: 1week, 3months, lifetime")
            return
        
        # Activate subscription
        activate_subscription(target_user_id, plan_key)
        
        invite_link = "https://t.me/+H2P5IxWkaHgxOTk5"
        
        user_text = f"""
🎉 Congratulations! Your VIP Subscription is ACTIVE! 🎉

✅ Plan: {PLANS[plan_key]['name']}
🔗 Join your VIP channel here:
{invite_link}

Welcome to the club! 🚀

You will now receive premium signals daily.
"""
        await context.bot.send_message(chat_id=target_user_id, text=user_text, parse_mode=None)
        await update.message.reply_text(f"✅ Subscription activated for user {target_user_id} with {PLANS[plan_key]['name']} plan!")
        
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to view pending payments"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    payments = get_pending_payments()
    
    if not payments:
        await update.message.reply_text("✅ No pending payments.")
        return
    
    text = "⏳ Pending Payments:\n\n"
    for payment in payments:
        text += f"👤 User: {payment[7] or payment[1]}\n"
        text += f"📅 Plan: {payment[2]}\n"
        text += f"💰 Amount: ${payment[3]}\n"
        text += f"💳 Method: {payment[4].upper()}\n"
        text += f"🆔 TXID: {payment[5]}\n"
        text += f"🔧 Verify: /verify {payment[1]} {payment[2].lower().replace(' ', '')}\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n"
    
    await update.message.reply_text(text, parse_mode=None)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to see bot statistics"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    active_count = get_active_subscribers()
    pending_payments = get_pending_payments()
    
    text = f"""
📊 Bot Statistics

👥 Active Subscribers: {active_count}
⏳ Pending Payments: {len(pending_payments)}
📋 Available Plans: 1 Week, 3 Months, Lifetime
"""
    await update.message.reply_text(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    await update.message.reply_text("Please use the buttons to navigate. Send /start to see the menu.")

def main():
    """Start the bot"""
    print("=" * 50)
    print("Starting Signal Bot...")
    print(f"Bot Token: {BOT_TOKEN[:15]}...")
    print(f"Owner ID: {OWNER_ID}")
    print(f"Support: @{SUPPORT_USERNAME}")
    print("=" * 50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_proof))
    
    print("Bot is running! Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
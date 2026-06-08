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

# ==================== TRANSLATIONS ====================
TEXTS = {
    'en': {
        'welcome': "📈 *Welcome to Signal Bot, {name}!* 📈\n\nGet ready to elevate your trading game. I provide *HIGH-QUALITY* premium signals.\n\n✅ *VIP Subscription Includes:*\n✅ High-Quality Premium Signals\n✅ Success Rate +75%\n✅ 30+ Signals Daily\n✅ Entry – Targets – StopLoss – Leverage\n\n📦 *Available Plans (Limited Offer):*\n▫️ 1 Week — $49 (was $100)\n▫️ 3 Months — $149 (was $300)\n▫️ Lifetime — $249 (was $1,000)\n\n🛡️ *Disclaimer: Trading involves risk. Past performance does not guarantee future results.*",
        'buy_vip': "🛒 BUY VIP",
        'my_account': "👤 My Account",
        'stats': "📊 Stats",
        'support': "🆘 Support",
        'languages': "🌐 Languages",
        'back': "🔙 Back",
        'plans_title': "💎 VIP Subscription Plans\n\nChoose the plan that works best for you:",
        'plan_1week': "📅 1 Week - $49",
        'plan_3months': "📆 3 Months - $149",
        'plan_lifetime': "♾️ Lifetime - $249",
        'payment_for': "💰 Payment for {plan} Plan\n\nAmount: ${price}",
        'select_method': "Select your payment method below:",
        'complete_payment': "💳 Complete Your Payment\n\nPlan: {plan} (${price})\nMethod: {symbol} {method}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nSend exactly ${price} in {method} to:\n\n{address}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nAfter sending your payment:\n1. Take a screenshot\n2. Click 'Upload Proof'\n3. Send the screenshot\n\nWe will verify within 15-30 minutes.",
        'upload_proof': "📸 Upload Payment Proof",
        'contact_support': "📞 Contact Support",
        'send_proof': "📸 Send Your Payment Proof\n\nPlease send a screenshot of your {method} payment for the {plan} plan (${price}).\n\nInstructions:\n1. Take a clear screenshot\n2. Send it as a PHOTO\n3. Our support will review and activate your subscription.\n\nYou will receive confirmation within 15-30 minutes.",
        'cancel': "❌ Cancel",
        'proof_received': "✅ Payment proof received! 📸\n\nOur support team will verify your payment for the {plan} plan.\n\n⏱️ Expected time: 15-30 minutes\n\nOnce verified, you will receive the VIP channel link.\n\n📞 For questions: @{support}",
        'account_active': "👤 My Account\n\n✅ Status: Active\n📅 Plan: {plan}\n⏰ Expires: {expiry}",
        'account_inactive': "👤 My Account\n\n❌ Status: Inactive\n\n💡 No active subscription found.\n\nClick BUY VIP to get started!",
        'stats_text': "📊 Bot Statistics\n\n📈 Total Signals Sent: 1,247\n✅ Success Rate (30d): 78.5%\n🎯 Avg Profit per Signal: +12.4%\n👥 Active Subscribers: {active}\n⭐ Average Rating: 4.8/5",
        'support_text': "🆘 Support Center\n\n📱 Telegram: @{support}\n⏰ Response Time: 15-30 minutes (24/7)\n\nFAQs:\nHow do I get signals after payment?\n→ Send payment proof through the bot after selecting your plan\n\nWhat payment methods?\n→ BTC, USDT, LTC, DOGE",
        'lang_set': "✅ Language set to {lang}. You will now receive messages in {lang}.",
        'error_plan': "❌ Invalid plan. Please go back and select a plan again.",
        'error_method': "❌ Invalid payment method. Please go back and try again.",
        'error_address': "❌ {method} payment is not configured yet. Please contact @{support}",
    },
    'es': {
        'welcome': "📈 *¡Bienvenido a Signal Bot, {name}!* 📈\n\nPrepárate para mejorar tu trading. Proporciono señales premium de *ALTA CALIDAD*.\n\n✅ *La suscripción VIP incluye:*\n✅ Señales premium de alta calidad\n✅ Tasa de éxito +75%\n✅ 30+ señales diarias\n✅ Entrada – Objetivos – StopLoss – Apalancamiento\n\n📦 *Planes disponibles (oferta limitada):*\n▫️ 1 semana — $49 (antes $100)\n▫️ 3 meses — $149 (antes $300)\n▫️ Vitalicio — $249 (antes $1,000)\n\n🛡️ *Aviso: El trading implica riesgo. El rendimiento pasado no garantiza resultados futuros.*",
        'buy_vip': "🛒 COMPRAR VIP",
        'my_account': "👤 Mi Cuenta",
        'stats': "📊 Estadísticas",
        'support': "🆘 Soporte",
        'languages': "🌐 Idiomas",
        'back': "🔙 Atrás",
        'plans_title': "💎 Planes de Suscripción VIP\n\nElige el plan que mejor se adapte a ti:",
        'plan_1week': "📅 1 semana - $49",
        'plan_3months': "📆 3 meses - $149",
        'plan_lifetime': "♾️ Vitalicio - $249",
        'payment_for': "💰 Pago para el plan {plan}\n\nMonto: ${price}",
        'select_method': "Selecciona tu método de pago a continuación:",
        'complete_payment': "💳 Completa tu pago\n\nPlan: {plan} (${price})\nMétodo: {symbol} {method}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nEnvía exactamente ${price} en {method} a:\n\n{address}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nDespués de enviar tu pago:\n1. Toma una captura de pantalla\n2. Haz clic en 'Subir Comprobante'\n3. Envía la captura\n\nVerificaremos en 15-30 minutos.",
        'upload_proof': "📸 Subir Comprobante",
        'contact_support': "📞 Contactar Soporte",
        'send_proof': "📸 Envía tu comprobante de pago\n\nPor favor, envía una captura de pantalla de tu pago en {method} para el plan {plan} (${price}).\n\nInstrucciones:\n1. Toma una captura clara\n2. Envíala como FOTO\n3. Nuestro soporte revisará y activará tu suscripción.\n\nRecibirás confirmación en 15-30 minutos.",
        'cancel': "❌ Cancelar",
        'proof_received': "✅ ¡Comprobante de pago recibido! 📸\n\nNuestro equipo verificará tu pago para el plan {plan}.\n\n⏱️ Tiempo estimado: 15-30 minutos\n\nUna vez verificado, recibirás el enlace del canal VIP.\n\n📞 Para preguntas: @{support}",
        'account_active': "👤 Mi Cuenta\n\n✅ Estado: Activo\n📅 Plan: {plan}\n⏰ Expira: {expiry}",
        'account_inactive': "👤 Mi Cuenta\n\n❌ Estado: Inactivo\n\n💡 No se encontró suscripción activa.\n\n¡Haz clic en COMPRAR VIP para comenzar!",
        'stats_text': "📊 Estadísticas del Bot\n\n📈 Señales enviadas: 1,247\n✅ Tasa de éxito (30d): 78.5%\n🎯 Ganancia promedio por señal: +12.4%\n👥 Suscriptores activos: {active}\n⭐ Calificación promedio: 4.8/5",
        'support_text': "🆘 Centro de Soporte\n\n📱 Telegram: @{support}\n⏰ Tiempo de respuesta: 15-30 minutos (24/7)\n\nPreguntas frecuentes:\n¿Cómo recibo las señales después del pago?\n→ Envía el comprobante a través del bot después de seleccionar tu plan\n\n¿Qué métodos de pago?\n→ BTC, USDT, LTC, DOGE",
        'lang_set': "✅ Idioma configurado a {lang}. Recibirás los mensajes en {lang}.",
        'error_plan': "❌ Plan inválido. Por favor, regresa y selecciona un plan nuevamente.",
        'error_method': "❌ Método de pago inválido. Por favor, regresa e intenta de nuevo.",
        'error_address': "❌ El pago en {method} no está configurado aún. Por favor contacta a @{support}",
    },
    'ru': {
        'welcome': "📈 *Добро пожаловать в Signal Bot, {name}!* 📈\n\nПовысьте свою торговлю. Я предоставляю *ВЫСОКОКАЧЕСТВЕННЫЕ* премиум-сигналы.\n\n✅ *VIP-подписка включает:*\n✅ Высококачественные премиум-сигналы\n✅ Успешность +75%\n✅ 30+ сигналов ежедневно\n✅ Вход – Цели – Стоп-лосс – Плечо\n\n📦 *Доступные планы (ограниченное предложение):*\n▫️ 1 неделя — $49 (было $100)\n▫️ 3 месяца — $149 (было $300)\n▫️ Бессрочно — $249 (было $1,000)\n\n🛡️ *Отказ от ответственности: Торговля сопряжена с риском. Прошлые результаты не гарантируют будущих.*",
        'buy_vip': "🛒 КУПИТЬ VIP",
        'my_account': "👤 Мой аккаунт",
        'stats': "📊 Статистика",
        'support': "🆘 Поддержка",
        'languages': "🌐 Языки",
        'back': "🔙 Назад",
        'plans_title': "💎 VIP-планы подписки\n\nВыберите подходящий план:",
        'plan_1week': "📅 1 неделя - $49",
        'plan_3months': "📆 3 месяца - $149",
        'plan_lifetime': "♾️ Бессрочно - $249",
        'payment_for': "💰 Оплата плана {plan}\n\nСумма: ${price}",
        'select_method': "Выберите способ оплаты:",
        'complete_payment': "💳 Завершите оплату\n\nПлан: {plan} (${price})\nСпособ: {symbol} {method}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nОтправьте ровно ${price} в {method} на:\n\n{address}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nПосле отправки:\n1. Сделайте скриншот\n2. Нажмите 'Загрузить подтверждение'\n3. Отправьте скриншот\n\nМы проверим в течение 15-30 минут.",
        'upload_proof': "📸 Загрузить подтверждение",
        'contact_support': "📞 Связаться с поддержкой",
        'send_proof': "📸 Отправьте подтверждение оплаты\n\nПожалуйста, отправьте скриншот вашего платежа в {method} для плана {plan} (${price}).\n\nИнструкции:\n1. Сделайте четкий скриншот\n2. Отправьте его как ФОТО\n3. Наша поддержка проверит и активирует подписку.\n\nВы получите подтверждение в течение 15-30 минут.",
        'cancel': "❌ Отмена",
        'proof_received': "✅ Подтверждение оплаты получено! 📸\n\nНаша команда проверит ваш платеж для плана {plan}.\n\n⏱️ Ожидаемое время: 15-30 минут\n\nПосле проверки вы получите ссылку на VIP-канал.\n\n📞 Вопросы: @{support}",
        'account_active': "👤 Мой аккаунт\n\n✅ Статус: Активен\n📅 План: {plan}\n⏰ Истекает: {expiry}",
        'account_inactive': "👤 Мой аккаунт\n\n❌ Статус: Неактивен\n\n💡 Нет активной подписки.\n\nНажмите КУПИТЬ VIP, чтобы начать!",
        'stats_text': "📊 Статистика бота\n\n📈 Всего сигналов: 1,247\n✅ Успешность (30д): 78.5%\n🎯 Средняя прибыль на сигнал: +12.4%\n👥 Активных подписчиков: {active}\n⭐ Средний рейтинг: 4.8/5",
        'support_text': "🆘 Центр поддержки\n\n📱 Telegram: @{support}\n⏰ Время ответа: 15-30 минут (24/7)\n\nЧасто задаваемые вопросы:\nКак получить сигналы после оплаты?\n→ Отправьте подтверждение через бота после выбора плана\n\nКакие способы оплаты?\n→ BTC, USDT, LTC, DOGE",
        'lang_set': "✅ Язык установлен на {lang}. Вы будете получать сообщения на {lang}.",
        'error_plan': "❌ Неверный план. Пожалуйста, вернитесь и выберите план снова.",
        'error_method': "❌ Неверный способ оплаты. Пожалуйста, вернитесь и попробуйте снова.",
        'error_address': "❌ Оплата в {method} еще не настроена. Пожалуйста, свяжитесь с @{support}",
    },
    'ar': {
        'welcome': "📈 *مرحبًا بك في Signal Bot، {name}!* 📈\n\nاستعد لرفع مستوى تداولك. أقدم إشارات متميزة *عالية الجودة*.\n\n✅ *تشمل الاشتراك VIP:*\n✅ إشارات عالية الجودة\n✅ نسبة نجاح +75%\n✅ 30+ إشارة يوميًا\n✅ الدخول – الأهداف – وقف الخسارة – الرافعة المالية\n\n📦 *الخطط المتاحة (عرض محدود):*\n▫️ أسبوع واحد — $49 (كان $100)\n▫️ 3 أشهر — $149 (كان $300)\n▫️ مدى الحياة — $249 (كان $1,000)\n\n🛡️ *إخلاء مسؤولية: التداول ينطوي على مخاطر. الأداء السابق لا يضمن النتائج المستقبلية.*",
        'buy_vip': "🛒 شراء VIP",
        'my_account': "👤 حسابي",
        'stats': "📊 إحصائيات",
        'support': "🆘 الدعم",
        'languages': "🌐 اللغات",
        'back': "🔙 رجوع",
        'plans_title': "💎 خطط الاشتراك VIP\n\nاختر الخطة التي تناسبك:",
        'plan_1week': "📅 أسبوع واحد - $49",
        'plan_3months': "📆 3 أشهر - $149",
        'plan_lifetime': "♾️ مدى الحياة - $249",
        'payment_for': "💰 دفع لخطة {plan}\n\nالمبلغ: ${price}",
        'select_method': "اختر طريقة الدفع أدناه:",
        'complete_payment': "💳 أكمل دفعتك\n\nالخطة: {plan} (${price})\nالطريقة: {symbol} {method}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nأرسل بالضبط ${price} بعملة {method} إلى:\n\n{address}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nبعد إرسال دفعتك:\n1. التقط لقطة شاشة\n2. اضغط 'رفع الإثبات'\n3. أرسل لقطة الشاشة\n\nسنقوم بالتحقق في غضون 15-30 دقيقة.",
        'upload_proof': "📸 رفع الإثبات",
        'contact_support': "📞 اتصل بالدعم",
        'send_proof': "📸 أرسل إثبات الدفع\n\nيرجى إرسال لقطة شاشة لدفعتك بعملة {method} لخطة {plan} (${price}).\n\nالتعليمات:\n1. التقط لقطة شاشة واضحة\n2. أرسلها كصورة\n3. سيقوم فريق الدعم بالتحقق وتفعيل اشتراكك.\n\nستتلقى تأكيدًا خلال 15-30 دقيقة.",
        'cancel': "❌ إلغاء",
        'proof_received': "✅ تم استلام إثبات الدفع! 📸\n\nسيتحقق فريقنا من دفعتك لخطة {plan}.\n\n⏱️ الوقت المتوقع: 15-30 دقيقة\n\nبعد التحقق، ستتلقى رابط قناة VIP.\n\n📞 للاستفسارات: @{support}",
        'account_active': "👤 حسابي\n\n✅ الحالة: نشط\n📅 الخطة: {plan}\n⏰ ينتهي: {expiry}",
        'account_inactive': "👤 حسابي\n\n❌ الحالة: غير نشط\n\n💡 لا يوجد اشتراك نشط.\n\nانقر على شراء VIP للبدء!",
        'stats_text': "📊 إحصائيات البوت\n\n📈 إجمالي الإشارات المرسلة: 1,247\n✅ نسبة النجاح (30 يومًا): 78.5%\n🎯 متوسط الربح لكل إشارة: +12.4%\n👥 المشتركين النشطين: {active}\n⭐ متوسط التقييم: 4.8/5",
        'support_text': "🆘 مركز الدعم\n\n📱 تيليجرام: @{support}\n⏰ وقت الاستجابة: 15-30 دقيقة (24/7)\n\nالأسئلة الشائعة:\nكيف أحصل على الإشارات بعد الدفع؟\n→ أرسل إثبات الدفع عبر البوت بعد اختيار خطتك\n\nما هي طرق الدفع؟\n→ BTC, USDT, LTC, DOGE",
        'lang_set': "✅ تم تعيين اللغة إلى {lang}. ستتلقى الرسائل باللغة {lang}.",
        'error_plan': "❌ خطة غير صالحة. يرجى الرجوع واختيار خطة مرة أخرى.",
        'error_method': "❌ طريقة دفع غير صالحة. يرجى الرجوع والمحاولة مرة أخرى.",
        'error_address': "❌ الدفع بـ {method} لم يتم تكوينه بعد. يرجى الاتصال بـ @{support}",
    }
}

# ==================== HELPER FUNCTIONS ====================
async def get_text(update: Update, key: str, **kwargs):
    """Get translated text for user's language"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    text = TEXTS.get(lang, TEXTS['en']).get(key, TEXTS['en'][key])
    return text.format(**kwargs) if kwargs else text

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with main menu"""
    user = update.effective_user
    user_id = user.id
    
    db_user = get_user(user_id)
    if not db_user:
        create_user(user_id, user.username, user.first_name)
    
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    keyboard = [
        [
            InlineKeyboardButton(texts['buy_vip'], callback_data="buy_vip"),
            InlineKeyboardButton(texts['my_account'], callback_data="my_account")
        ],
        [
            InlineKeyboardButton(texts['stats'], callback_data="stats"),
            InlineKeyboardButton(texts['support'], callback_data="support")
        ],
        [
            InlineKeyboardButton(texts['languages'], callback_data="languages")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = texts['welcome'].format(name=user.first_name)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
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
    elif data.startswith("lang_"):
        await set_language(update, context, data)
    else:
        print(f"Unknown callback: {data}")

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show subscription plans"""
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    keyboard = [
        [
            InlineKeyboardButton(texts['plan_1week'], callback_data="plan_1week"),
            InlineKeyboardButton(texts['plan_3months'], callback_data="plan_3months")
        ],
        [
            InlineKeyboardButton(texts['plan_lifetime'], callback_data="plan_lifetime")
        ],
        [InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(texts['plans_title'], reply_markup=reply_markup, parse_mode=None)

async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE, plan_callback):
    """Show payment methods for selected plan"""
    query = update.callback_query
    plan_key = plan_callback.replace("plan_", "")
    plan = PLANS[plan_key]
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
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
        [InlineKeyboardButton(texts['back'], callback_data="buy_vip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = texts['payment_for'].format(plan=plan['name'], price=plan['price']) + "\n\n" + texts['select_method']
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    """Process payment method selection"""
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    parts = data.split("_")
    if len(parts) < 3:
        await query.edit_message_text("❌ Invalid payment option. Please go back and try again.")
        return
    
    method = parts[1]
    plan_key = parts[2]
    
    if plan_key not in PLANS:
        await query.edit_message_text(texts['error_plan'])
        return
    if method not in PAYMENT_METHODS:
        await query.edit_message_text(texts['error_method'])
        return
    
    plan = PLANS[plan_key]
    method_info = PAYMENT_METHODS[method]
    address = WALLET_ADDRESSES.get(method, "NOT_CONFIGURED")
    
    if address == "NOT_CONFIGURED":
        await query.edit_message_text(texts['error_address'].format(method=method.upper(), support=SUPPORT_USERNAME))
        return
    
    text = texts['complete_payment'].format(
        plan=plan['name'], price=plan['price'], 
        symbol=method_info['symbol'], method=method_info['name'],
        address=address
    )
    
    keyboard = [
        [InlineKeyboardButton(texts['upload_proof'], callback_data=f"upload_proof_{method}_{plan_key}")],
        [InlineKeyboardButton(texts['back'], callback_data="buy_vip")],
        [InlineKeyboardButton(texts['contact_support'], url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def upload_proof_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    """Handle upload proof button - asks user to send screenshot"""
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    parts = data.split("_")
    if len(parts) >= 3:
        method = parts[1]
        plan_key = parts[2]
        plan = PLANS.get(plan_key, {"name": "Unknown", "price": "Unknown"})
        method_info = PAYMENT_METHODS.get(method, {"name": method.upper()})
        
        context.user_data['pending_payment'] = {
            'method': method,
            'plan_key': plan_key,
            'plan_name': plan['name'],
            'price': plan['price'],
            'method_name': method_info['name']
        }
        
        text = texts['send_proof'].format(method=method_info['name'], plan=plan['name'], price=plan['price'])
        
        keyboard = [
            [InlineKeyboardButton(texts['cancel'], callback_data="buy_vip")],
            [InlineKeyboardButton(texts['contact_support'], url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof photos sent by users"""
    user = update.effective_user
    photo = update.message.photo[-1]
    user_id = user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    pending = context.user_data.get('pending_payment', {})
    
    if not pending:
        await update.message.reply_text("❌ Please use the bot buttons to make a payment first.\n\nSend /start to begin.")
        return
    
    plan_key = pending.get('plan_key', '1week')
    
    try:
        add_payment_record(
            user_id=user.id,
            plan_key=plan_key,
            amount=pending.get('price', 0),
            method=pending.get('method', 'unknown'),
            transaction_id=f"photo_proof_{datetime.now().timestamp()}"
        )
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(f"❌ Error recording payment. Please contact @{SUPPORT_USERNAME}")
        return
    
    caption = f"""
📸 NEW PAYMENT PROOF RECEIVED!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 User: {user.first_name} (@{user.username or 'N/A'})
🆔 ID: {user.id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Plan: {pending.get('plan_name', 'Unknown')} (${pending.get('price', 'Unknown')})
💳 Method: {pending.get('method_name', 'Unknown').upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶️ To activate: /verify {user.id} {plan_key}
"""
    
    await context.bot.send_photo(chat_id=OWNER_ID, photo=photo.file_id, caption=caption)
    
    if SUPPORT_USERNAME:
        try:
            await context.bot.send_photo(chat_id=f"@{SUPPORT_USERNAME}", photo=photo.file_id, caption=f"Payment proof from @{user.username or user.first_name}")
        except:
            pass
    
    await update.message.reply_text(texts['proof_received'].format(plan=pending.get('plan_name', ''), support=SUPPORT_USERNAME))
    context.user_data['pending_payment'] = {}
    await context.bot.send_message(chat_id=OWNER_ID, text=f"🔔 Proof from @{user.username or user.first_name}\n/verify {user.id} {plan_key}")

async def show_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user account information"""
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)
    is_active = is_subscription_active(user_id)
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    if is_active and user:
        expiry = user["subscription_expiry"]
        expiry_text = datetime.fromisoformat(expiry).strftime("%Y-%m-%d") if expiry else "Never"
        text = texts['account_active'].format(plan=user['subscription_plan'], expiry=expiry_text)
    else:
        text = texts['account_inactive']
    
    keyboard = [[InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    query = update.callback_query
    active_count = get_active_subscribers()
    lang = get_user_language(query.from_user.id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    text = texts['stats_text'].format(active=active_count)
    keyboard = [[InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show support information"""
    query = update.callback_query
    lang = get_user_language(query.from_user.id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    text = texts['support_text'].format(support=SUPPORT_USERNAME)
    keyboard = [
        [InlineKeyboardButton(texts['contact_support'], url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection menu"""
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("Español 🇪🇸", callback_data="lang_es")],
        [InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🌐 Select your language / Elige tu idioma / Выберите язык / اختر لغتك:", reply_markup=reply_markup, parse_mode=None)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    """Set user's language preference"""
    query = update.callback_query
    user_id = query.from_user.id
    lang_code = data.split("_")[1]
    
    set_user_language(user_id, lang_code)
    
    lang_names = {
        'en': 'English', 'es': 'Español', 'ru': 'Русский', 'ar': 'العربية'
    }
    
    await query.answer()
    text = TEXTS.get(lang_code, TEXTS['en'])['lang_set'].format(lang=lang_names.get(lang_code, lang_code))
    await query.edit_message_text(text, reply_markup=None, parse_mode=None)
    
    # Return to main menu after 2 seconds
    await asyncio.sleep(2)
    await back_to_menu(update, context)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    
    keyboard = [
        [
            InlineKeyboardButton(texts['buy_vip'], callback_data="buy_vip"),
            InlineKeyboardButton(texts['my_account'], callback_data="my_account")
        ],
        [
            InlineKeyboardButton(texts['stats'], callback_data="stats"),
            InlineKeyboardButton(texts['support'], callback_data="support")
        ],
        [
            InlineKeyboardButton(texts['languages'], callback_data="languages")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = texts['welcome'].format(name=user['first_name'] if user else "")
    await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== ADMIN COMMANDS ====================
async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to verify payment and activate subscription"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /verify <user_id> <plan_key>")
        return
    
    try:
        target_user_id = int(args[0])
        plan_key = args[1]
        if plan_key not in PLANS:
            await update.message.reply_text("Invalid plan key. Use: 1week, 3months, lifetime")
            return
        
        activate_subscription(target_user_id, plan_key)
        invite_link = "https://t.me/+H2P5IxWkaHgxOTk5"
        
        user_text = f"🎉 Congratulations! Your VIP Subscription is ACTIVE! 🎉\n\n✅ Plan: {PLANS[plan_key]['name']}\n🔗 Join: {invite_link}\n\nWelcome!"
        await context.bot.send_message(chat_id=target_user_id, text=user_text)
        await update.message.reply_text(f"✅ Activated user {target_user_id} with {PLANS[plan_key]['name']} plan!")
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
    for p in payments:
        text += f"👤 User: {p[7] or p[1]}\n📅 Plan: {p[2]}\n💰 Amount: ${p[3]}\n💳 Method: {p[4].upper()}\n🔧 Verify: /verify {p[1]} {p[2].lower().replace(' ', '')}\n━━━━━━━━━━━━━━━━━━━\n"
    await update.message.reply_text(text, parse_mode=None)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to see bot statistics"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    active = get_active_subscribers()
    pending = len(get_pending_payments())
    await update.message.reply_text(f"📊 Bot Stats\n👥 Active: {active}\n⏳ Pending: {pending}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    await update.message.reply_text("Please use the buttons. Send /start to see the menu.")

# ==================== MAIN ====================
def main():
    print("=" * 50)
    print("Starting Signal Bot...")
    print(f"Bot Token: {BOT_TOKEN[:15]}...")
    print(f"Owner ID: {OWNER_ID}")
    print(f"Support: @{SUPPORT_USERNAME}")
    print("=" * 50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_proof))
    
    print("Bot is running!")
    application.run_polling()

if __name__ == "__main__":
    main()
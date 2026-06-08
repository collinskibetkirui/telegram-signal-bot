import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from config import *
from database import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

init_db()

# ==================== TRANSLATIONS WITH EYE‑CATCHING FORMATTING ====================
TEXTS = {
    'en': {
        'welcome': (
            "✨ *WELCOME TO SIGNAL BOT* ✨\n\n"
            "🚀 *The Ultimate Trading Signals Provider*\n"
            "───────────────────────────────\n"
            "✅ *VIP Features:*\n"
            "• High‑Quality Premium Signals\n"
            "• Success Rate +75%\n"
            "• 30+ Signals Daily\n"
            "• Entry | Targets | StopLoss | Leverage\n"
            "───────────────────────────────\n"
            "🔥 *LIMITED OFFER – SAVE UP TO 75%*\n"
            "▫️ 1 Week    ~~$100~~ → **$49**\n"
            "▫️ 3 Months  ~~$300~~ → **$149**\n"
            "▫️ Lifetime  ~~$1,000~~ → **$249**\n"
            "───────────────────────────────\n"
            "🛡️ *Risk Disclaimer:* Trading involves risk.\n"
            "Past performance does not guarantee future results."
        ),
        'buy_vip': "💎 BUY VIP",
        'my_account': "👤 MY ACCOUNT",
        'stats': "📊 STATS",
        'support': "🆘 SUPPORT",
        'languages': "🌐 LANGUAGES",
        'back': "🔙 BACK",
        'plans_title': "💎 *VIP SUBSCRIPTION PLANS*\n\nChoose your plan – the more months, the more you save!",
        'plan_1week': "📅 1 WEEK → $49",
        'plan_3months': "📆 3 MONTHS → $149",
        'plan_lifetime': "♾️ LIFETIME → $249",
        'payment_for': "💰 *Payment for {plan}*  \n💵 Amount: `${price}`",
        'select_method': "👇 *Select your preferred crypto:*",
        'complete_payment': (
            "💳 *COMPLETE YOUR PAYMENT*\n\n"
            "📌 *Plan:* {plan}\n"
            "💲 *Amount:* `${price}`\n"
            "🔹 *Method:* {symbol} {method}\n"
            "───────────────────────────────\n"
            "📤 *Send exactly* `${price}` *in* `{method}` *to:*\n"
            "`{address}`\n"
            "───────────────────────────────\n"
            "📸 *After sending:*\n"
            "1. Take a screenshot\n"
            "2. Click *'Upload Proof'* below\n"
            "3. Send the image here\n"
            "⏱️ Verification within 15–30 min."
        ),
        'upload_proof': "📸 UPLOAD PROOF",
        'contact_support': "📞 CONTACT SUPPORT",
        'send_proof': (
            "📸 *SEND YOUR PAYMENT PROOF*\n\n"
            "Please send a clear screenshot of your `{method}` payment for the *{plan}* plan (${price}).\n\n"
            "🖼️ *Instructions:*\n"
            "• Take a screenshot showing the transaction\n"
            "• Send it as a *PHOTO* in this chat\n"
            "• Our support will verify and activate your subscription\n\n"
            "⏱️ You'll receive confirmation within 15–30 minutes."
        ),
        'cancel': "❌ CANCEL",
        'proof_received': (
            "✅ *PAYMENT PROOF RECEIVED!*\n\n"
            "Thank you for your payment for the *{plan}* plan.\n\n"
            "🛂 Our support team will verify your transaction and activate your VIP access.\n"
            "⏱️ Estimated time: 15–30 minutes.\n\n"
            "📞 For urgent questions: @{support}"
        ),
        'account_active': (
            "👤 *MY ACCOUNT*\n\n"
            "✅ *Status:* `ACTIVE`\n"
            "📅 *Plan:* {plan}\n"
            "⏰ *Expires:* {expiry}\n"
            "───────────────────────────────\n"
            "🔔 You will receive signals automatically."
        ),
        'account_inactive': (
            "👤 *MY ACCOUNT*\n\n"
            "❌ *Status:* `INACTIVE`\n\n"
            "💡 No active subscription found.\n"
            "👉 Click *BUY VIP* to get started!"
        ),
        'stats_text': (
            "📊 *BOT STATISTICS*\n\n"
            "📈 Total signals sent: `1,247`\n"
            "✅ Success rate (30d): `78.5%`\n"
            "🎯 Avg profit per signal: `+12.4%`\n"
            "👥 Active subscribers: `{active}`\n"
            "⭐ Average rating: `4.8/5`\n"
            "───────────────────────────────\n"
            "*Last 30 days performance*"
        ),
        'support_text': (
            "🆘 *SUPPORT CENTER*\n\n"
            "📱 Telegram: @{support}\n"
            "⏰ Response time: 15–30 min (24/7)\n\n"
            "📌 *FAQs*\n"
            "❓ How do I get signals after payment?\n"
            "→ Send payment proof through the bot after selecting your plan.\n\n"
            "❓ What payment methods?\n"
            "→ BTC, USDT, LTC, DOGE"
        ),
        'lang_set': "✅ Language set to *{lang}*. You will now receive messages in {lang}.",
        'error_plan': "❌ Invalid plan. Please go back and choose again.",
        'error_method': "❌ Invalid payment method. Please try again.",
        'error_address': "❌ {method} payments are not configured yet. Contact @{support}",
    },
    'es': {
        'welcome': (
            "✨ *BIENVENIDO A SIGNAL BOT* ✨\n\n"
            "🚀 *El mejor proveedor de señales de trading*\n"
            "───────────────────────────────\n"
            "✅ *Características VIP:*\n"
            "• Señales premium de alta calidad\n"
            "• Tasa de éxito +75%\n"
            "• 30+ señales diarias\n"
            "• Entrada | Objetivos | StopLoss | Apalancamiento\n"
            "───────────────────────────────\n"
            "🔥 *OFERTA LIMITADA – AHORRA HASTA 75%*\n"
            "▫️ 1 semana    ~~$100~~ → **$49**\n"
            "▫️ 3 meses     ~~$300~~ → **$149**\n"
            "▫️ Vitalicio   ~~$1,000~~ → **$249**\n"
            "───────────────────────────────\n"
            "🛡️ *Advertencia:* El trading implica riesgo.\n"
            "El rendimiento pasado no garantiza resultados futuros."
        ),
        'buy_vip': "💎 COMPRAR VIP",
        'my_account': "👤 MI CUENTA",
        'stats': "📊 ESTADÍSTICAS",
        'support': "🆘 SOPORTE",
        'languages': "🌐 IDIOMAS",
        'back': "🔙 ATRÁS",
        'plans_title': "💎 *PLANES DE SUSCRIPCIÓN VIP*\n\nElige tu plan – ¡cuantos más meses, más ahorras!",
        'plan_1week': "📅 1 SEMANA → $49",
        'plan_3months': "📆 3 MESES → $149",
        'plan_lifetime': "♾️ VITALICIO → $249",
        'payment_for': "💰 *Pago para {plan}*  \n💵 Monto: `${price}`",
        'select_method': "👇 *Selecciona tu criptomoneda:*",
        'complete_payment': (
            "💳 *COMPLETA TU PAGO*\n\n"
            "📌 *Plan:* {plan}\n"
            "💲 *Monto:* `${price}`\n"
            "🔹 *Método:* {symbol} {method}\n"
            "───────────────────────────────\n"
            "📤 *Envía exactamente* `${price}` *en* `{method}` *a:*\n"
            "`{address}`\n"
            "───────────────────────────────\n"
            "📸 *Después de enviar:*\n"
            "1. Toma una captura de pantalla\n"
            "2. Haz clic en *'Subir Comprobante'*\n"
            "3. Envía la imagen aquí\n"
            "⏱️ Verificación en 15–30 min."
        ),
        'upload_proof': "📸 SUBIR COMPROBANTE",
        'contact_support': "📞 CONTACTAR SOPORTE",
        'send_proof': (
            "📸 *ENVÍA TU COMPROBANTE DE PAGO*\n\n"
            "Envía una captura clara de tu pago en `{method}` para el plan *{plan}* (${price}).\n\n"
            "🖼️ *Instrucciones:*\n"
            "• Captura de pantalla que muestre la transacción\n"
            "• Envíala como *FOTO* en este chat\n"
            "• Nuestro soporte verificará y activará tu suscripción\n\n"
            "⏱️ Recibirás confirmación en 15–30 minutos."
        ),
        'cancel': "❌ CANCELAR",
        'proof_received': (
            "✅ *¡COMPROBANTE RECIBIDO!*\n\n"
            "Gracias por tu pago del plan *{plan}*.\n\n"
            "🛂 Nuestro equipo verificará tu transacción y activará tu acceso VIP.\n"
            "⏱️ Tiempo estimado: 15–30 minutos.\n\n"
            "📞 Preguntas urgentes: @{support}"
        ),
        'account_active': (
            "👤 *MI CUENTA*\n\n"
            "✅ *Estado:* `ACTIVO`\n"
            "📅 *Plan:* {plan}\n"
            "⏰ *Expira:* {expiry}\n"
            "───────────────────────────────\n"
            "🔔 Recibirás señales automáticamente."
        ),
        'account_inactive': (
            "👤 *MI CUENTA*\n\n"
            "❌ *Estado:* `INACTIVO`\n\n"
            "💡 No hay suscripción activa.\n"
            "👉 Haz clic en *COMPRAR VIP* para empezar."
        ),
        'stats_text': (
            "📊 *ESTADÍSTICAS DEL BOT*\n\n"
            "📈 Señales enviadas: `1,247`\n"
            "✅ Tasa de éxito (30d): `78.5%`\n"
            "🎯 Ganancia media por señal: `+12.4%`\n"
            "👥 Suscriptores activos: `{active}`\n"
            "⭐ Calificación media: `4.8/5`\n"
            "───────────────────────────────\n"
            "*Rendimiento de los últimos 30 días*"
        ),
        'support_text': (
            "🆘 *CENTRO DE SOPORTE*\n\n"
            "📱 Telegram: @{support}\n"
            "⏰ Tiempo de respuesta: 15–30 min (24/7)\n\n"
            "📌 *PREGUNTAS FRECUENTES*\n"
            "❓ ¿Cómo recibo las señales después del pago?\n"
            "→ Envía el comprobante a través del bot después de seleccionar tu plan.\n\n"
            "❓ ¿Qué métodos de pago?\n"
            "→ BTC, USDT, LTC, DOGE"
        ),
        'lang_set': "✅ Idioma configurado a *{lang}*. Recibirás los mensajes en {lang}.",
        'error_plan': "❌ Plan inválido. Por favor, regresa y elige de nuevo.",
        'error_method': "❌ Método de pago inválido. Intenta de nuevo.",
        'error_address': "❌ Los pagos con {method} aún no están configurados. Contacta a @{support}",
    },
    'ru': {
        'welcome': (
            "✨ *ДОБРО ПОЖАЛОВАТЬ В SIGNAL BOT* ✨\n\n"
            "🚀 *Лучший поставщик торговых сигналов*\n"
            "───────────────────────────────\n"
            "✅ *VIP-возможности:*\n"
            "• Высококачественные премиум-сигналы\n"
            "• Успешность +75%\n"
            "• 30+ сигналов ежедневно\n"
            "• Вход | Цели | StopLoss | Плечо\n"
            "───────────────────────────────\n"
            "🔥 *ОГРАНИЧЕННОЕ ПРЕДЛОЖЕНИЕ – ЭКОНОМИЯ ДО 75%*\n"
            "▫️ 1 неделя    ~~$100~~ → **$49**\n"
            "▫️ 3 месяца    ~~$300~~ → **$149**\n"
            "▫️ Бессрочно   ~~$1,000~~ → **$249**\n"
            "───────────────────────────────\n"
            "🛡️ *Предупреждение:* Торговля связана с риском.\n"
            "Прошлые результаты не гарантируют будущих."
        ),
        'buy_vip': "💎 КУПИТЬ VIP",
        'my_account': "👤 МОЙ АККАУНТ",
        'stats': "📊 СТАТИСТИКА",
        'support': "🆘 ПОДДЕРЖКА",
        'languages': "🌐 ЯЗЫКИ",
        'back': "🔙 НАЗАД",
        'plans_title': "💎 *VIP-ПЛАНЫ ПОДПИСКИ*\n\nВыберите план – чем больше месяцев, тем больше экономия!",
        'plan_1week': "📅 1 НЕДЕЛЯ → $49",
        'plan_3months': "📆 3 МЕСЯЦА → $149",
        'plan_lifetime': "♾️ БЕССРОЧНО → $249",
        'payment_for': "💰 *Оплата плана {plan}*  \n💵 Сумма: `${price}`",
        'select_method': "👇 *Выберите криптовалюту:*",
        'complete_payment': (
            "💳 *ЗАВЕРШИТЕ ОПЛАТУ*\n\n"
            "📌 *План:* {plan}\n"
            "💲 *Сумма:* `${price}`\n"
            "🔹 *Метод:* {symbol} {method}\n"
            "───────────────────────────────\n"
            "📤 *Отправьте ровно* `${price}` *в* `{method}` *на:*\n"
            "`{address}`\n"
            "───────────────────────────────\n"
            "📸 *После отправки:*\n"
            "1. Сделайте скриншот\n"
            "2. Нажмите *'Загрузить подтверждение'*\n"
            "3. Отправьте изображение сюда\n"
            "⏱️ Проверка займёт 15–30 мин."
        ),
        'upload_proof': "📸 ЗАГРУЗИТЬ ПОДТВЕРЖДЕНИЕ",
        'contact_support': "📞 СВЯЗАТЬСЯ С ПОДДЕРЖКОЙ",
        'send_proof': (
            "📸 *ОТПРАВЬТЕ ПОДТВЕРЖДЕНИЕ ОПЛАТЫ*\n\n"
            "Пришлите чёткий скриншот вашего платежа в `{method}` для плана *{plan}* (${price}).\n\n"
            "🖼️ *Инструкции:*\n"
            "• Скриншот, показывающий транзакцию\n"
            "• Отправьте как *ФОТО* в этот чат\n"
            "• Наша поддержка проверит и активирует подписку\n\n"
            "⏱️ Вы получите подтверждение через 15–30 минут."
        ),
        'cancel': "❌ ОТМЕНА",
        'proof_received': (
            "✅ *ПОДТВЕРЖДЕНИЕ ПОЛУЧЕНО!*\n\n"
            "Спасибо за оплату плана *{plan}*.\n\n"
            "🛂 Наша команда проверит транзакцию и активирует VIP-доступ.\n"
            "⏱️ Ожидаемое время: 15–30 минут.\n\n"
            "📞 Для срочных вопросов: @{support}"
        ),
        'account_active': (
            "👤 *МОЙ АККАУНТ*\n\n"
            "✅ *Статус:* `АКТИВЕН`\n"
            "📅 *План:* {plan}\n"
            "⏰ *Истекает:* {expiry}\n"
            "───────────────────────────────\n"
            "🔔 Сигналы будут приходить автоматически."
        ),
        'account_inactive': (
            "👤 *МОЙ АККАУНТ*\n\n"
            "❌ *Статус:* `НЕАКТИВЕН`\n\n"
            "💡 Нет активной подписки.\n"
            "👉 Нажмите *КУПИТЬ VIP*, чтобы начать."
        ),
        'stats_text': (
            "📊 *СТАТИСТИКА БОТА*\n\n"
            "📈 Всего сигналов: `1,247`\n"
            "✅ Успешность (30д): `78.5%`\n"
            "🎯 Средняя прибыль: `+12.4%`\n"
            "👥 Активных подписчиков: `{active}`\n"
            "⭐ Средняя оценка: `4.8/5`\n"
            "───────────────────────────────\n"
            "*Результаты за последние 30 дней*"
        ),
        'support_text': (
            "🆘 *ЦЕНТР ПОДДЕРЖКИ*\n\n"
            "📱 Telegram: @{support}\n"
            "⏰ Время ответа: 15–30 мин (24/7)\n\n"
            "📌 *ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ*\n"
            "❓ Как получить сигналы после оплаты?\n"
            "→ Отправьте подтверждение через бота после выбора плана.\n\n"
            "❓ Какие способы оплаты?\n"
            "→ BTC, USDT, LTC, DOGE"
        ),
        'lang_set': "✅ Язык установлен на *{lang}*. Теперь вы будете получать сообщения на {lang}.",
        'error_plan': "❌ Неверный план. Пожалуйста, вернитесь и выберите снова.",
        'error_method': "❌ Неверный способ оплаты. Попробуйте снова.",
        'error_address': "❌ Платежи в {method} ещё не настроены. Свяжитесь с @{support}",
    },
    'ar': {
        'welcome': (
            "✨ *مرحباً بك في بوت الإشارات* ✨\n\n"
            "🚀 *أفضل مزود لإشارات التداول*\n"
            "───────────────────────────────\n"
            "✅ *مميزات VIP:*\n"
            "• إشارات متميزة عالية الجودة\n"
            "• نسبة نجاح +75%\n"
            "• 30+ إشارة يومياً\n"
            "• الدخول | الأهداف | وقف الخسارة | الرافعة\n"
            "───────────────────────────────\n"
            "🔥 *عرض محدود – وفر حتى 75%*\n"
            "▫️ أسبوع واحد    ~~$100~~ → **$49**\n"
            "▫️ 3 أشهر        ~~$300~~ → **$149**\n"
            "▫️ مدى الحياة    ~~$1,000~~ → **$249**\n"
            "───────────────────────────────\n"
            "🛡️ *تنويه:* التداول ينطوي على مخاطر.\n"
            "الأداء السابق لا يضمن النتائج المستقبلية."
        ),
        'buy_vip': "💎 شراء VIP",
        'my_account': "👤 حسابي",
        'stats': "📊 إحصائيات",
        'support': "🆘 دعم",
        'languages': "🌐 اللغات",
        'back': "🔙 رجوع",
        'plans_title': "💎 *خطط الاشتراك VIP*\n\nاختر خطتك – كلما زادت الأشهر، وفرت أكثر!",
        'plan_1week': "📅 أسبوع واحد → $49",
        'plan_3months': "📆 3 أشهر → $149",
        'plan_lifetime': "♾️ مدى الحياة → $249",
        'payment_for': "💰 *دفع لخطة {plan}*  \n💵 المبلغ: `${price}`",
        'select_method': "👇 *اختر عملتك المشفرة:*",
        'complete_payment': (
            "💳 *أكمل دفعتك*\n\n"
            "📌 *الخطة:* {plan}\n"
            "💲 *المبلغ:* `${price}`\n"
            "🔹 *الطريقة:* {symbol} {method}\n"
            "───────────────────────────────\n"
            "📤 *أرسل بالضبط* `${price}` *بواسطة* `{method}` *إلى:*\n"
            "`{address}`\n"
            "───────────────────────────────\n"
            "📸 *بعد الإرسال:*\n"
            "1. التقط لقطة شاشة\n"
            "2. اضغط *'رفع الإثبات'* أدناه\n"
            "3. أرسل الصورة هنا\n"
            "⏱️ التحقق خلال 15–30 دقيقة."
        ),
        'upload_proof': "📸 رفع الإثبات",
        'contact_support': "📞 اتصل بالدعم",
        'send_proof': (
            "📸 *أرسل إثبات دفعتك*\n\n"
            "يرجى إرسال لقطة شاشة واضحة لدفعتك بعملة `{method}` لخطة *{plan}* (${price}).\n\n"
            "🖼️ *التعليمات:*\n"
            "• لقطة شاشة تظهر المعاملة\n"
            "• أرسلها كـ *صورة* في هذه الدردشة\n"
            "• سيتحقق فريق الدعم ويفعّل اشتراكك\n\n"
            "⏱️ ستتلقى تأكيداً خلال 15–30 دقيقة."
        ),
        'cancel': "❌ إلغاء",
        'proof_received': (
            "✅ *تم استلام إثبات الدفع!*\n\n"
            "شكراً لدفعك لخطة *{plan}*.\n\n"
            "🛂 سيتحقق فريقنا من المعاملة ويفعّل وصولك VIP.\n"
            "⏱️ الوقت المتوقع: 15–30 دقيقة.\n\n"
            "📞 للأسئلة العاجلة: @{support}"
        ),
        'account_active': (
            "👤 *حسابي*\n\n"
            "✅ *الحالة:* `نشط`\n"
            "📅 *الخطة:* {plan}\n"
            "⏰ *تنتهي:* {expiry}\n"
            "───────────────────────────────\n"
            "🔔 ستتلقى الإشارات تلقائياً."
        ),
        'account_inactive': (
            "👤 *حسابي*\n\n"
            "❌ *الحالة:* `غير نشط`\n\n"
            "💡 لا يوجد اشتراك نشط.\n"
            "👉 اضغط *شراء VIP* للبدء."
        ),
        'stats_text': (
            "📊 *إحصائيات البوت*\n\n"
            "📈 إجمالي الإشارات: `1,247`\n"
            "✅ نسبة النجاح (30 يوماً): `78.5%`\n"
            "🎯 متوسط الربح لكل إشارة: `+12.4%`\n"
            "👥 المشتركين النشطين: `{active}`\n"
            "⭐ متوسط التقييم: `4.8/5`\n"
            "───────────────────────────────\n"
            "*أداء آخر 30 يوماً*"
        ),
        'support_text': (
            "🆘 *مركز الدعم*\n\n"
            "📱 تيليجرام: @{support}\n"
            "⏰ وقت الرد: 15–30 دقيقة (24/7)\n\n"
            "📌 *الأسئلة الشائعة*\n"
            "❓ كيف أحصل على الإشارات بعد الدفع؟\n"
            "→ أرسل إثبات الدفع عبر البوت بعد اختيار خطتك.\n\n"
            "❓ ما هي طرق الدفع؟\n"
            "→ BTC, USDT, LTC, DOGE"
        ),
        'lang_set': "✅ تم تعيين اللغة إلى *{lang}*. ستتلقى الرسائل باللغة {lang}.",
        'error_plan': "❌ خطة غير صالحة. يرجى الرجوع والاختيار مرة أخرى.",
        'error_method': "❌ طريقة دفع غير صالحة. حاول مرة أخرى.",
        'error_address': "❌ المدفوعات بـ {method} لم يتم تكوينها بعد. اتصل بـ @{support}",
    }
}

# Helper to get translated text
async def get_text(update: Update, key: str, **kwargs):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    text = TEXTS.get(lang, TEXTS['en']).get(key, TEXTS['en'][key])
    return text.format(**kwargs) if kwargs else text

# ==================== HANDLERS (same as before, but using the new TEXTS) ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    db_user = get_user(user_id)
    if not db_user:
        create_user(user_id, user.username, user.first_name)
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    keyboard = [
        [InlineKeyboardButton(texts['buy_vip'], callback_data="buy_vip"), InlineKeyboardButton(texts['my_account'], callback_data="my_account")],
        [InlineKeyboardButton(texts['stats'], callback_data="stats"), InlineKeyboardButton(texts['support'], callback_data="support")],
        [InlineKeyboardButton(texts['languages'], callback_data="languages")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_msg = texts['welcome']
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    keyboard = [
        [InlineKeyboardButton(texts['plan_1week'], callback_data="plan_1week"), InlineKeyboardButton(texts['plan_3months'], callback_data="plan_3months")],
        [InlineKeyboardButton(texts['plan_lifetime'], callback_data="plan_lifetime")],
        [InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(texts['plans_title'], reply_markup=reply_markup, parse_mode="Markdown")

async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE, plan_callback):
    query = update.callback_query
    plan_key = plan_callback.replace("plan_", "")
    plan = PLANS[plan_key]
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    context.user_data['selected_plan'] = plan_key
    keyboard = [
        [InlineKeyboardButton("₿ BTC", callback_data=f"pay_btc_{plan_key}"), InlineKeyboardButton("💲 USDT", callback_data=f"pay_usdt_{plan_key}")],
        [InlineKeyboardButton("Ł LTC", callback_data=f"pay_ltc_{plan_key}"), InlineKeyboardButton("Ð DOGE", callback_data=f"pay_doge_{plan_key}")],
        [InlineKeyboardButton(texts['back'], callback_data="buy_vip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = texts['payment_for'].format(plan=plan['name'], price=plan['price']) + "\n\n" + texts['select_method']
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    parts = data.split("_")
    if len(parts) < 3:
        await query.edit_message_text("❌ Invalid option.")
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
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def upload_proof_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
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
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    user_id = user.id
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    pending = context.user_data.get('pending_payment', {})
    if not pending:
        await update.message.reply_text("❌ Please use the bot buttons first. Send /start.")
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
        await update.message.reply_text(f"❌ Error. Contact @{SUPPORT_USERNAME}")
        return
    caption = f"""
📸 *NEW PAYMENT PROOF*

👤 `{user.first_name}` (@{user.username or 'N/A'})
🆔 `{user.id}`
📅 *Plan:* {pending.get('plan_name', 'Unknown')} (${pending.get('price', 'Unknown')})
💳 *Method:* {pending.get('method_name', 'Unknown').upper()}
⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

👉 /verify {user.id} {plan_key}
"""
    await context.bot.send_photo(chat_id=OWNER_ID, photo=photo.file_id, caption=caption, parse_mode="Markdown")
    if SUPPORT_USERNAME:
        try:
            await context.bot.send_photo(chat_id=f"@{SUPPORT_USERNAME}", photo=photo.file_id, caption=f"Proof from @{user.username or user.first_name}")
        except:
            pass
    await update.message.reply_text(texts['proof_received'].format(plan=pending.get('plan_name', ''), support=SUPPORT_USERNAME), parse_mode="Markdown")
    context.user_data['pending_payment'] = {}
    await context.bot.send_message(chat_id=OWNER_ID, text=f"🔔 Proof from @{user.username or user.first_name}\n/verify {user.id} {plan_key}")

async def show_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    active_count = get_active_subscribers()
    lang = get_user_language(query.from_user.id)
    texts = TEXTS.get(lang, TEXTS['en'])
    text = texts['stats_text'].format(active=active_count)
    keyboard = [[InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = get_user_language(query.from_user.id)
    texts = TEXTS.get(lang, TEXTS['en'])
    text = texts['support_text'].format(support=SUPPORT_USERNAME)
    keyboard = [
        [InlineKeyboardButton(texts['contact_support'], url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🌐 *Select your language* / *Elige tu idioma* / *Выберите язык* / *اختر لغتك*", reply_markup=reply_markup, parse_mode="Markdown")

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    query = update.callback_query
    user_id = query.from_user.id
    lang_code = data.split("_")[1]
    set_user_language(user_id, lang_code)
    lang_names = {'en': 'English', 'es': 'Español', 'ru': 'Русский', 'ar': 'العربية'}
    await query.answer()
    text = TEXTS.get(lang_code, TEXTS['en'])['lang_set'].format(lang=lang_names.get(lang_code, lang_code))
    await query.edit_message_text(text, parse_mode="Markdown")
    await asyncio.sleep(2)
    await back_to_menu(update, context)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)
    lang = get_user_language(user_id)
    texts = TEXTS.get(lang, TEXTS['en'])
    keyboard = [
        [InlineKeyboardButton(texts['buy_vip'], callback_data="buy_vip"), InlineKeyboardButton(texts['my_account'], callback_data="my_account")],
        [InlineKeyboardButton(texts['stats'], callback_data="stats"), InlineKeyboardButton(texts['support'], callback_data="support")],
        [InlineKeyboardButton(texts['languages'], callback_data="languages")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_msg = texts['welcome']
    await query.edit_message_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== ADMIN COMMANDS (unchanged but using markdown) ====================
async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: `/verify <user_id> <plan_key>`\nPlan keys: `1week`, `3months`, `lifetime`", parse_mode="Markdown")
        return
    try:
        target_user_id = int(args[0])
        plan_key = args[1]
        if plan_key not in PLANS:
            await update.message.reply_text("Invalid plan key.")
            return
        activate_subscription(target_user_id, plan_key)
        invite_link = "https://t.me/+H2P5IxWkaHgxOTk5"
        user_text = f"🎉 *VIP ACTIVATED!* 🎉\n\n✅ Plan: *{PLANS[plan_key]['name']}*\n🔗 [Join VIP Channel]({invite_link})\n\nWelcome to the club! 🚀"
        await context.bot.send_message(chat_id=target_user_id, text=user_text, parse_mode="Markdown")
        await update.message.reply_text(f"✅ Activated user `{target_user_id}` with *{PLANS[plan_key]['name']}* plan.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    payments = get_pending_payments()
    if not payments:
        await update.message.reply_text("✅ No pending payments.")
        return
    text = "⏳ *Pending Payments*\n\n"
    for p in payments:
        text += f"👤 `{p[7] or p[1]}`\n📅 {p[2]}\n💰 `${p[3]}`\n💳 {p[4].upper()}\n🔧 `/verify {p[1]} {p[2].lower().replace(' ', '')}`\n━━━━━━━━━━━━━━━━━━━\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    active = get_active_subscribers()
    pending = len(get_pending_payments())
    await update.message.reply_text(f"📊 *Bot Stats*\n👥 Active: `{active}`\n⏳ Pending: `{pending}`", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Please use the buttons. Send /start to see the menu.")

# ==================== MAIN ====================
def main():
    print("=" * 50)
    print("✨ Starting Signal Bot (Enhanced UI) ✨")
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
    print("🚀 Bot is running! Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
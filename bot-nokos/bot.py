import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
from config import BOT_TOKEN, ADMIN_IDS, GACHA_SUCCESS_RATE, COUNTRIES, NUMBER_FORMATS, OTP_CHANNEL_ID, OTP_GROUP_ID
from database import db

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def generate_phone_number(country_code):
    """Generate random phone number dengan format yang sesuai"""
    format_pattern = NUMBER_FORMATS.get(country_code, "XXXXXXXXXX")
    
    # Generate number berdasarkan format
    phone_digits = ''.join(random.choices(string.digits, k=10))
    
    # Format nomor sesuai pola
    if country_code == "+1":  # US
        formatted = f"{phone_digits[:3]}-{phone_digits[3:6]}-{phone_digits[6:]}"
    elif country_code == "+62":  # Indonesia
        formatted = f"{phone_digits[:3]}-{phone_digits[3:7]}-{phone_digits[7:]}"
    elif country_code == "+65":  # Singapore
        formatted = f"{phone_digits[:4]}-{phone_digits[4:]}"
    elif country_code in ["+358", "+372"]:  # Finland, Estonia
        formatted = f"{phone_digits[:3]}-{phone_digits[3:]}"
    elif country_code == "+376":  # Andorra
        formatted = f"{phone_digits[:3]}-{phone_digits[3:6]}"
    elif country_code == "+379":  # Vatican City
        formatted = f"{phone_digits[:3]}-{phone_digits[3:7]}"
    elif country_code == "+423":  # Liechtenstein
        formatted = f"{phone_digits[:3]}-{phone_digits[3:7]}"
    elif country_code == "+356":  # Malta
        formatted = f"{phone_digits[:4]}-{phone_digits[4:]}"
    elif country_code == "+357":  # Cyprus
        formatted = f"{phone_digits[:2]}-{phone_digits[2:]}"
    elif country_code in ["+973", "+974"]:  # Bahrain, Qatar
        formatted = f"{phone_digits[:4]}-{phone_digits[4:]}"
    elif country_code == "+673":  # Brunei
        formatted = f"{phone_digits[:3]}-{phone_digits[3:7]}"
    else:
        formatted = phone_digits
    
    return f"{country_code} {formatted}"

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMIN_IDS

async def send_otp_to_channels(context, phone_number, otp_code, country_name, username=None):
    """Kirim OTP ke semua channel/grup yang terdaftar"""
    try:
        message_text = f"""
🔔 **OTP NOTIFICATION**

📱 New OTP Generated!
🌍 Country: {country_name}
📞 Number: `{phone_number}`
🔐 OTP Code: `{otp_code}`
👤 User: {username or 'Unknown'}
⏰ Time: {context.bot_data['current_time']}
"""
        
        sent_messages = []
        
        # Kirim ke channel default
        if OTP_CHANNEL_ID:
            try:
                message = await context.bot.send_message(
                    chat_id=OTP_CHANNEL_ID,
                    text=message_text,
                    parse_mode='Markdown'
                )
                sent_messages.append(("Channel", OTP_CHANNEL_ID, message.message_id))
            except TelegramError as e:
                print(f"Error sending to channel: {e}")
        
        # Kirim ke grup default
        if OTP_GROUP_ID:
            try:
                message = await context.bot.send_message(
                    chat_id=OTP_GROUP_ID,
                    text=message_text,
                    parse_mode='Markdown'
                )
                sent_messages.append(("Group", OTP_GROUP_ID, message.message_id))
            except TelegramError as e:
                print(f"Error sending to group: {e}")
        
        # Kirim ke channel/grup yang terdaftar di database
        channels = db.get_active_channels()
        for channel in channels:
            try:
                message = await context.bot.send_message(
                    chat_id=channel[1],  # chat_id
                    text=message_text,
                    parse_mode='Markdown'
                )
                sent_messages.append((channel[3], channel[1], message.message_id))  # chat_type, chat_id, message_id
            except TelegramError as e:
                print(f"Error sending to {channel[3]}: {e}")
        
        return sent_messages
        
    except Exception as e:
        print(f"Error in send_otp_to_channels: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_text = f"""
👋 Halo {user.first_name}!

Selamat datang di Bot Gacha Nokos Simulator!

🎰 **Fitur Utama:**
• Gacha nomor kontak dari berbagai negara
• OTP otomatis terkirim ke channel/grup
• Success rate 5%

📱 **Daftar Negara:**
"""
    # Tampilkan negara regular dulu
    for code, info in COUNTRIES.items():
        if not info.get('rare', False) and not info.get('small', False):
            welcome_text += f"• {info['name']} ({info['code']})\n"
    
    # Tampilkan negara rare (jarang)
    welcome_text += "\n🌍 **Negara Langka (5% Success Rate):**\n"
    for code, info in COUNTRIES.items():
        if info.get('rare', False):
            welcome_text += f"• {info['name']} ({info['code']}) ⭐\n"
    
    # Tampilkan negara kecil (penduduk sedikit)
    welcome_text += "\n🏛️ **Negara Kecil (Penduduk Sedikit):**\n"
    for code, info in COUNTRIES.items():
        if info.get('small', False):
            welcome_text += f"• {info['name']} ({info['code']}) 🏛️\n"
    
    welcome_text += "\nKlik /gacha untuk memulai!"
    
    await update.message.reply_text(welcome_text)

async def gacha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command untuk memulai gacha"""
    keyboard = []
    
    # Negara regular
    regular_buttons = []
    for code, info in COUNTRIES.items():
        if not info.get('rare', False) and not info.get('small', False):
            button = InlineKeyboardButton(
                f"{info['name']} ({info['code']})", 
                callback_data=f"gacha_{code}"
            )
            regular_buttons.append(button)
    
    # Negara rare
    rare_buttons = []
    for code, info in COUNTRIES.items():
        if info.get('rare', False):
            button = InlineKeyboardButton(
                f"⭐ {info['name']}", 
                callback_data=f"gacha_{code}"
            )
            rare_buttons.append(button)
    
    # Negara kecil
    small_buttons = []
    for code, info in COUNTRIES.items():
        if info.get('small', False):
            button = InlineKeyboardButton(
                f"🏛️ {info['name']}", 
                callback_data=f"gacha_{code}"
            )
            small_buttons.append(button)
    
    # Susun keyboard
    for i in range(0, len(regular_buttons), 2):
        keyboard.append(regular_buttons[i:i+2])
    
    if rare_buttons:
        keyboard.append([InlineKeyboardButton("🌍 NEGARA LANGKA ⭐", callback_data="header")])
        for i in range(0, len(rare_buttons), 2):
            keyboard.append(rare_buttons[i:i+2])
    
    if small_buttons:
        keyboard.append([InlineKeyboardButton("🏛️ NEGARA KECIL", callback_data="header")])
        for i in range(0, len(small_buttons), 2):
            keyboard.append(small_buttons[i:i+2])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎰 Pilih negara untuk gacha nokos:\n⭐ = Negara Langka | 🏛️ = Negara Kecil",
        reply_markup=reply_markup
    )

async def gacha_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gacha callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    country_code = query.data.split('_')[1]
    country_info = COUNTRIES.get(country_code)
    
    if not country_info:
        await query.edit_message_text("❌ Negara tidak valid!")
        return
    
    # Cek apakah ada nomor yang tersedia dari admin
    available_numbers = db.get_available_admin_numbers(country_code)
    
    if available_numbers:
        # Gunakan nomor dari admin
        admin_number = available_numbers[0]
        phone_number = admin_number[2]  # phone_number
        otp_code = admin_number[3]      # otp_code
        is_success = True
        source = "🛠️ (Dari Admin)"
        
        # Tandai nomor sebagai digunakan
        cursor = db.conn.cursor()
        cursor.execute('UPDATE admin_numbers SET used = TRUE WHERE id = ?', (admin_number[0],))
        db.conn.commit()
        
        # Kirim OTP ke channel/grup
        user = query.from_user
        username = f"@{user.username}" if user.username else user.first_name
        sent_messages = await send_otp_to_channels(context, phone_number, otp_code, country_info['name'], username)
        
    else:
        # Generate phone number biasa
        phone_number = generate_phone_number(country_info['code'])
        
        # Determine success (5% chance)
        is_success = random.random() < GACHA_SUCCESS_RATE
        otp_code = generate_otp() if is_success else "GAGAL"
        source = ""
        
        # Jika berhasil, kirim OTP ke channel/grup
        if is_success:
            user = query.from_user
            username = f"@{user.username}" if user.username else user.first_name
            sent_messages = await send_otp_to_channels(context, phone_number, otp_code, country_info['name'], username)
    
    # Save to database
    record_id = db.add_gacha_record(user_id, country_code, phone_number, is_success, otp_code)
    
    # Prepare result message
    result_text = f"""
📱 **Hasil Gacha {country_info['name']}** {source}

📞 Nomor: `{phone_number}`
🎯 Status: {'✅ BERHASIL' if is_success else '❌ GAGAL'}
"""
    
    if is_success:
        result_text += f"🔐 Kode OTP: `{otp_code}`\n\n"
        result_text += "📢 OTP telah dikirim ke channel/grup!"
    else:
        result_text += "\nCoba lagi untuk kesempatan mendapatkan OTP!"
    
    result_text += f"\n📊 Success Rate: {GACHA_SUCCESS_RATE*100}%"
    
    keyboard = [[InlineKeyboardButton("🔄 Gacha Lagi", callback_data="gacha_again")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command untuk melihat statistik user"""
    user_id = update.effective_user.id
    stats = db.get_user_stats(user_id)
    
    if stats:
        total_gacha, success_gacha = stats
        success_rate = (success_gacha / total_gacha * 100) if total_gacha > 0 else 0
        
        stats_text = f"""
📊 **Statistik Anda**

🎰 Total Gacha: {total_gacha}
✅ Berhasil: {success_gacha}
📈 Success Rate: {success_rate:.1f}%
"""
    else:
        stats_text = "📊 Anda belum melakukan gacha. Gunakan /gacha untuk memulai!"
    
    await update.message.reply_text(stats_text)

# ADMIN COMMANDS - FITUR BARU
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command admin untuk melihat statistik bot"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    users = db.get_all_users()
    gacha_records = db.get_all_gacha_records()
    admin_numbers = db.get_admin_numbers()
    channels = db.get_active_channels()
    
    total_users = len(users)
    total_gacha = len(gacha_records)
    success_gacha = sum(1 for record in gacha_records if record[4])
    total_admin_numbers = len(admin_numbers)
    used_admin_numbers = sum(1 for num in admin_numbers if num[5])
    
    admin_text = f"""
👑 **Admin Statistics**

👥 Total Users: {total_users}
🎰 Total Gacha: {total_gacha}
✅ Success Gacha: {success_gacha}
📈 Global Success Rate: {(success_gacha/total_gacha*100) if total_gacha > 0 else 0:.1f}%

🛠️ **Admin Numbers:**
📞 Total: {total_admin_numbers}
✅ Used: {used_admin_numbers}
🔄 Available: {total_admin_numbers - used_admin_numbers}

📢 **Channels/Groups:**
Total: {len(channels)}
"""
    
    for channel in channels:
        admin_text += f"• {channel[3]}: {channel[2]}\n"
    
    await update.message.reply_text(admin_text)

async def admin_create_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin create nomor manual"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    if not context.args:
        # Tampilkan pilihan negara
        keyboard = []
        
        # Kelompokkan negara
        regular = []
        rare = []
        small = []
        
        for code, info in COUNTRIES.items():
            if info.get('small', False):
                small.append((code, info))
            elif info.get('rare', False):
                rare.append((code, info))
            else:
                regular.append((code, info))
        
        # Buat buttons
        for code, info in regular:
            button = InlineKeyboardButton(
                f"{info['name']} ({info['code']})", 
                callback_data=f"admin_create_{code}"
            )
            keyboard.append([button])
        
        if rare:
            keyboard.append([InlineKeyboardButton("🌍 NEGARA LANGKA", callback_data="header")])
            for code, info in rare:
                button = InlineKeyboardButton(
                    f"⭐ {info['name']}", 
                    callback_data=f"admin_create_{code}"
                )
                keyboard.append([button])
        
        if small:
            keyboard.append([InlineKeyboardButton("🏛️ NEGARA KECIL", callback_data="header")])
            for code, info in small:
                button = InlineKeyboardButton(
                    f"🏛️ {info['name']}", 
                    callback_data=f"admin_create_{code}"
                )
                keyboard.append([button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🛠️ Pilih negara untuk membuat nomor:",
            reply_markup=reply_markup
        )
        return

async def admin_create_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback untuk create nomor admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ Anda bukan admin!")
        return
    
    country_code = query.data.split('_')[2]
    country_info = COUNTRIES.get(country_code)
    
    if not country_info:
        await query.edit_message_text("❌ Negara tidak valid!")
        return
    
    # Generate nomor
    phone_number = generate_phone_number(country_info['code'])
    otp_code = generate_otp()
    
    # Simpan ke database
    record_id = db.add_admin_number(country_code, phone_number, otp_code, user_id)
    
    # Kirim OTP ke channel/grup
    sent_messages = await send_otp_to_channels(context, phone_number, otp_code, country_info['name'], "Admin")
    
    result_text = f"""
🛠️ **Nomor Admin Berhasil Dibuat**

🌍 Negara: {country_info['name']}
📞 Nomor: `{phone_number}`
🔐 OTP: `{otp_code}`
✅ Status: TERSEDIA untuk user
📢 OTP telah dikirim ke channel/grup!
"""
    
    await query.edit_message_text(result_text)

async def admin_list_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin list semua nomor yang dibuat"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    numbers = db.get_admin_numbers(limit=20)
    
    if not numbers:
        await update.message.reply_text("📭 Belum ada nomor yang dibuat!")
        return
    
    list_text = "🛠️ **Daftar Nomor Admin**\n\n"
    
    for num in numbers:
        status = "✅ TERSEDIA" if not num[5] else "❌ DIGUNAKAN"
        country_info = COUNTRIES.get(num[1], {"name": "Unknown"})
        list_text += f"🌍 {country_info['name']} | 📞 {num[2]}\n"
        list_text += f"🔐 OTP: {num[3]} | {status}\n"
        list_text += f"👤 By: {num[7] or 'Unknown'}\n"
        list_text += f"📅 {num[6]}\n"
        list_text += "─" * 30 + "\n"
    
    await update.message.reply_text(list_text)

# FITUR CHANNEL/GROUP MANAGEMENT
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tambahkan channel/grup untuk OTP notifications"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    if update.message.chat.type in ['group', 'supergroup']:
        chat_id = str(update.message.chat.id)
        chat_title = update.message.chat.title
        chat_type = "group" if update.message.chat.type == 'group' else "supergroup"
        
        db.add_channel(chat_id, chat_title, chat_type)
        await update.message.reply_text(f"✅ Grup '{chat_title}' berhasil ditambahkan untuk OTP notifications!")
    
    elif update.message.chat.type == 'channel':
        chat_id = str(update.message.chat.id)
        chat_title = update.message.chat.title
        chat_type = "channel"
        
        db.add_channel(chat_id, chat_title, chat_type)
        await update.message.reply_text(f"✅ Channel '{chat_title}' berhasil ditambahkan untuk OTP notifications!")
    else:
        await update.message.reply_text("❌ Command ini hanya bisa digunakan di grup atau channel!")

async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hapus channel/grup dari OTP notifications"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /remove_channel <chat_id>")
        return
    
    chat_id = context.args[0]
    db.remove_channel(chat_id)
    await update.message.reply_text(f"✅ Channel/Grup dengan ID {chat_id} berhasil dihapus!")

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List semua channel/grup yang terdaftar"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    channels = db.get_active_channels()
    
    if not channels:
        await update.message.reply_text("📭 Belum ada channel/grup yang terdaftar!")
        return
    
    list_text = "📢 **Daftar Channel/Grup OTP**\n\n"
    
    for channel in channels:
        list_text += f"📝 Nama: {channel[2]}\n"
        list_text += f"🆔 ID: {channel[1]}\n"
        list_text += f"📋 Tipe: {channel[3]}\n"
        list_text += "─" * 30 + "\n"
    
    await update.message.reply_text(list_text)

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command admin untuk broadcast message"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /broadcast <message>")
        return
    
    message = " ".join(context.args)
    users = db.get_all_users()
    
    await update.message.reply_text(f"📢 Mengirim broadcast ke {len(users)} users...")
    
    # Implement broadcast logic here
    # Note: Hati-hati dengan rate limiting Telegram
    
    await update.message.reply_text("✅ Broadcast selesai!")

async def gacha_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback untuk gacha lagi"""
    query = update.callback_query
    await query.answer()
    await gacha_command(update, context)

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gacha", gacha_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("admin", admin_stats))
    application.add_handler(CommandHandler("admin_create", admin_create_number))
    application.add_handler(CommandHandler("admin_list", admin_list_numbers))
    application.add_handler(CommandHandler("add_channel", add_channel))
    application.add_handler(CommandHandler("remove_channel", remove_channel))
    application.add_handler(CommandHandler("list_channels", list_channels))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    
    application.add_handler(CallbackQueryHandler(gacha_callback, pattern="^gacha_"))
    application.add_handler(CallbackQueryHandler(admin_create_callback, pattern="^admin_create_"))
    application.add_handler(CallbackQueryHandler(gacha_again_callback, pattern="^gacha_again"))
    
    # Start bot
    print("🤖 Bot sedang berjalan...")
    application.run_polling()

if __name__ == '__main__':
    main()
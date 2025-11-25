import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError,
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError
)
import config

# -------------------------
# Messages & Buttons
# -------------------------
ask_ques = "**♪ قم بالضغط علي زر بيروجرام  🚦⚡ .**"
buttons_ques = [[InlineKeyboardButton("بيروجرام", callback_data="pyrogram")]]
gen_button = [[InlineKeyboardButton("♪ استخراج جلسه  🚦⚡ .", callback_data="generate")]]

# -------------------------
# Cancel / Restart Handler
# -------------------------
async def cancelled(msg: Message):
    text = msg.text.lower()
    if "/cancel" in text or text.startswith("/"):
        await msg.reply("**» تم الغاء عملية استخراج الجلسة!**", reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    elif "/restart" in text:
        await msg.reply("**» تم اعادة تشغيل البوت بنجاح!**", reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    elif "/skip" in text:
        return False
    return False

# -------------------------
# Main Command
# -------------------------
@Client.on_message(filters.private & ~filters.forwarded & filters.command(["استخراج جلسه", ": استخراج جلسه :"], ""))
async def main(_, msg: Message):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))

# -------------------------
# Session Generator
# -------------------------
async def generate_session(bot: Client, msg: Message, telethon=False, is_bot: bool = False):
    user_id = msg.chat.id
    ty = "Telethon" if telethon else "Pyrogram"
    if is_bot:
        ty += " BOT"

    await msg.reply(f"**♪ انت الان سوف تستخرج جلسه {ty} 🚦⚡ .**")
    
    # --- API_ID ---
    try:
        api_id_msg = await bot.ask(user_id, "**♪ ارسل الان : api_id الخاص بالحساب 🚦⚡ .**", filters=filters.text)
        if await cancelled(api_id_msg):
            return
        api_id = config.API_ID if api_id_msg.text.lower() == "تخطي" else int(api_id_msg.text)
    except ValueError:
        await msg.reply("**ᴀᴩɪ_ɪᴅ يجب ان يكون رقم صحيح**", reply_markup=InlineKeyboardMarkup(gen_button))
        return

    # --- API_HASH ---
    try:
        api_hash_msg = await bot.ask(user_id, "**♪ ارسل الان : api_hash الخاص بالحساب 🚦⚡ .**", filters=filters.text)
        if await cancelled(api_hash_msg):
            return
        api_hash = config.API_HASH if api_hash_msg.text.lower() == "تخطي" else api_hash_msg.text
    except Exception:
        await msg.reply("حدث خطأ في قراءة api_hash", reply_markup=InlineKeyboardMarkup(gen_button))
        return

    # --- Phone / Bot Token ---
    if not is_bot:
        t = "**♪ حسنا ارسل الان رقم حسابك 🚦⚡ .**\n♪ مثال: +201234567890"
    else:
        t = "أرسل الان توكن البوت الخاص بك  🚦⚡ ."

    phone_msg = await bot.ask(user_id, t, filters=filters.text)
    if await cancelled(phone_msg):
        return
    phone_number = phone_msg.text

    # --- Client Connect ---
    try:
        if telethon:
            client = TelegramClient(StringSession(), api_id, api_hash)
        elif is_bot:
            client = Client(name="bot", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
        else:
            client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
        await client.connect()
    except Exception as e:
        await msg.reply(f"خطأ في الاتصال: {e}", reply_markup=InlineKeyboardMarkup(gen_button))
        return

    # --- Send Code ---
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply("API_ID و API_HASH غير صحيحين.", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply("رقم الهاتف غير صحيح.", reply_markup=InlineKeyboardMarkup(gen_button))
        return

    # --- Enter Code ---
    phone_code_msg = await bot.ask(user_id, "أرسل الكود الذي وصلك عبر التليجرام 🚦⚡", filters=filters.text, timeout=600)
    if await cancelled(phone_code_msg):
        return
    phone_code = phone_code_msg.text.replace(" ", "")

    # --- Sign In ---
    try:
        if telethon:
            await client.sign_in(phone_number, phone_code)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await msg.reply("الكود غير صحيح.", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await msg.reply("الكود منتهي الصلاحية.", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        two_step_msg = await bot.ask(user_id, "أرسل كلمة المرور للحساب 🚦⚡", filters=filters.text, timeout=300)
        if await cancelled(two_step_msg):
            return
        try:
            password = two_step_msg.text
            if telethon:
                await client.sign_in(password=password)
            else:
                await client.check_password(password=password)
        except (PasswordHashInvalid, PasswordHashInvalidError):
            await two_step_msg.reply("كلمة المرور غير صحيحة.", reply_markup=InlineKeyboardMarkup(gen_button))
            return

    # --- Export Session ---
    try:
        if telethon:
            string_session = client.session.save()
        else:
            string_session = await client.export_session_string()
    except Exception as e:
        await msg.reply(f"فشل في استخراج الجلسة: {e}", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    finally:
        await client.disconnect()

    # --- Send Session to User ---
    await bot.send_message(user_id, f"**تم استخراج الجلسة بنجاح 🚦⚡**\n\n`{string_session}`\n\n**اضغط لنسخ الجلسة**", reply_markup=InlineKeyboardMarkup(gen_button))

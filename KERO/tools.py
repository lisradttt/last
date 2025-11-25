from pyrogram import Client, filters, raw, utils
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, Message
from config import logger as log, logger_mode as logm, OWNER
from KERO.info import (
    get_served_chats, get_served_users, del_served_chat, del_served_user,
    activecall, add_active_chat, add_served_call, add_active_video_chat
)
from KERO.Data import Bots
from KERO.play import logs, join_call
from KERO.Data import get_userbot, get_dev, get_call, get_group, get_channel
import aiohttp
import asyncio
from datetime import datetime
from pyrogram.errors import FloodWait
from pyrogram import enums
from typing import Union, List, Iterable

BASE = "https://batbin.me/"


async def post(url: str, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
        return data


async def base(text):
    resp = await post(f"{BASE}api/v2/paste", data=text)
    if not resp.get("success"):
        return
    link = BASE + resp["message"]
    return link


@Client.on_message(filters.command(["الاحصائيات", "• الاحصائيات •"], ""))
async def analysis(client: Client, message: Message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        chats = len(await get_served_chats(client))
        users = len(await get_served_users(client))
        await message.reply_text(f"**✅ احصائيات البوت**\n**⚡ المجموعات {chats} مجموعة  **\n**⚡ المستخدمين {users} مستخدم**")


@Client.on_message(filters.command(["• المجموعات •"], ""))
async def chats_func(client: Client, message: Message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        m = await message.reply_text("🐈‍⬛.")
        served_chats = []
        text = ""
        chats = await get_served_chats(client)
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
        count = 0
        for served_chat in served_chats:
            if f"{served_chat}" in text:
                await del_served_chat(client, served_chat)
            else:
                try:
                    chat = await client.get_chat(served_chat)
                    title = chat.title
                    username = chat.username
                    count += 1
                    txt = f"{count}:- Chat : [{title}](https://t.me/{username}) Id : `{served_chat}`\n" if username else f"{count}:- Chat : {title} Id : `{served_chat}`\n"
                    text += txt
                except Exception:
                    title = "Not Found"
                    count += 1
                    text += f"{count}:- {title} {served_chat}\n"
        if count == 0:
            await m.edit("الاحصائيات صفر 🤔")
        else:
            try:
                await message.reply_text(text, disable_web_page_preview=True)
            except:
                link = await base(text)
                await message.reply_text(link)
            await m.delete()


@Client.on_message(filters.command(["• المستخدمين •"], ""))
async def users_func(client: Client, message: Message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        m = await message.reply_text("🐈‍⬛.")
        served_users = []
        text = ""
        users = await get_served_users(client)
        for user in users:
            served_users.append(int(user["user_id"]))
        count = 0
        for served_user in served_users:
            if f"{served_user}" in text:
                await del_served_user(client, served_user)
            else:
                try:
                    chat = await client.get_chat(served_user)
                    title = chat.first_name
                    username = chat.username
                    count += 1
                    txt = f"{count}:- Chat : [{title}](https://t.me/{username}) Id : `{served_user}`\n" if username else f"{count}:- Chat : {title} Id : `{served_user}`\n"
                    text += txt
                except Exception:
                    title = "Not Found"
                    count += 1
                    text += f"{count}:- {title} {served_user}\n"
        if count == 0:
            await m.edit("الاحصائيات صفر 🤔")
        else:
            try:
                await message.reply_text(text, disable_web_page_preview=True)
            except:
                link = await base(text)
                await message.reply_text(link)
            await m.delete()


@Client.on_message(filters.command("• المكالمات النشطه •", ""))
async def geetmeactive(client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        m = await message.reply_text("**جاري جلب المكالمات النشطه ..🚦**")
        count = 0
        text = ""
        for i in activecall.get(client.me.username, []):
            try:
                chat = await client.get_chat(i)
                count += 1
                text += f"{count}- [{chat.title}](https://t.me/{chat.username}) : {chat.id}\n" if chat.username else f"{count}- {chat.title} : {chat.id}\n"
            except Exception:
                title = "Not Found"
                count += 1
                text += f"{count}:- {title} {i}\n"
        if count == 0:
            await m.edit(" لا يوجد مكالمات نشطه الان 🤔")
        else:
            try:
                await message.reply_text(text, disable_web_page_preview=True)
            except:
                link = await base(text)
                await message.reply_text(link)
            await m.delete()


@Client.on_message(filters.command(["• قسم الإذاعة •", "• رجوع •"], ""))
async def cast(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        kep = ReplyKeyboardMarkup(
            [["• اذاعه عام •"], ["• اذاعه للمجموعات •", "• اذاعه للمستخدمين •"], ["• توجيه عام •"], ["• توجيه للمجموعات •", "• توجيه للمستخدمين •"], ["• رجوع للقائمة الرئيسيه •"]],
            resize_keyboard=True
        )
        await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)


@Client.on_message(filters.command(["• اذاعه عام •", "• اذاعه للمجموعات •", "• اذاعه للمستخدمين •", "• توجيه عام •", "• توجيه للمستخدمين •", "• توجيه للمجموعات •"], ""))
async def cast1(client: Client, message):
   command = message.command[0]
   bot_username = client.me.username
   dev = await get_dev(bot_username)
   if message.chat.id == dev or message.chat.username in OWNER:
    if command == "• اذاعه عام •":
     kep = ReplyKeyboardMarkup([["• اذاعه عام بالبوت •"], ["• اذاعه عام بالمساعد •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• اذاعه للمجموعات •":
     kep = ReplyKeyboardMarkup([["• اذاعه للمجموعات بالبوت •"], ["• اذاعه للمجموعات بالمساعد •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• اذاعه للمستخدمين •":
     kep = ReplyKeyboardMarkup([["• اذاعه للمستخدمين بالبوت •"], ["• اذاعه للمستخدمين بالمساعد •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• توجيه عام •":
     kep = ReplyKeyboardMarkup([["• توجيه عام بالبوت •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• توجيه للمستخدمين •":
     kep = ReplyKeyboardMarkup([["• توجيه للمستخدمين بالبوت •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    else:
     kep = ReplyKeyboardMarkup([["• توجيه للمجموعات بالبوت •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)


@Client.on_message(filters.command(["• اذاعه عام •", "• اذاعه للمجموعات •", "• اذاعه للمستخدمين •", "• توجيه عام •", "• توجيه للمستخدمين •", "• توجيه للمجموعات •"], ""))
async def cast1(client: Client, message):
   command = message.command[0]
   bot_username = client.me.username
   dev = await get_dev(bot_username)
   if message.chat.id == dev or message.chat.username in OWNER:
    if command == "• اذاعه عام •":
     kep = ReplyKeyboardMarkup([["• اذاعه عام بالبوت •"], ["• اذاعه عام بالمساعد •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• اذاعه للمجموعات •":
     kep = ReplyKeyboardMarkup([["• اذاعه للمجموعات بالبوت •"], ["• اذاعه للمجموعات بالمساعد •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• اذاعه للمستخدمين •":
     kep = ReplyKeyboardMarkup([["• اذاعه للمستخدمين بالبوت •"], ["• اذاعه للمستخدمين بالمساعد •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• توجيه عام •":
     kep = ReplyKeyboardMarkup([["• توجيه عام بالبوت •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    elif command == "• توجيه للمستخدمين •":
     kep = ReplyKeyboardMarkup([["• توجيه للمستخدمين بالبوت •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)
    else:
     kep = ReplyKeyboardMarkup([["• توجيه للمجموعات بالبوت •"], ["• رجوع •"]], resize_keyboard=True)
     await message.reply_text("**أهلا بك عزيزي المطور **\n**هنا قسم الاذاعه تحكم بالازار**", reply_markup=kep)


@Client.on_message(filters.command(["• اذاعه عام بالبوت •", "• اذاعه عام بالمساعد •", "• اذاعه للمجموعات بالبوت •", "• اذاعه للمجموعات بالمساعد •", "• اذاعه للمستخدمين بالبوت •", "• اذاعه للمستخدمين بالمساعد •", "• توجيه عام بالبوت •", "• توجيه عام بالمساعد •", "• توجيه للمجموعات بالبوت •", "• توجيه للمجموعات بالمساعد •", "• توجيه للمستخدمين بالبوت •", "• توجيه للمستخدمين بالمساعد •"], ""))
async def cast5(client: Client, message):
  command = message.command[0]
  bot_username = client.me.username
  dev = await get_dev(bot_username)
  if message.chat.id == dev or message.chat.username in OWNER:
   kep = ReplyKeyboardMarkup([["• الغاء •"], ["• رجوع •"], ["• رجوع للقائمة الرئيسيه •"]], resize_keyboard=True)
   ask = await client.ask(message.chat.id, "قم بإرسال الاذاعه الخاصه بك", reply_markup=kep)
   x = ask.id
   y = message.chat.id
   if ask.text == "• الغاء •":
     return await ask.reply_text("**تم الالغاء بنجاح ✅**")
   pn = await client.ask(message.chat.id, "هل تريد تثبيت الاذاعه\nارسل « نعم » او « لا »")
   await message.reply_text("**جاري الاذاعه انتظر بعض الوقت ..⚡**")
   text = ask.text
   dn = 0
   fd = 0
   if command == "• اذاعه عام بالبوت •":
     chats = await get_served_chats(client)
     users = await get_served_users(client)
     chat = []
     for user in users:
         chat.append(int(user["user_id"]))
     for c in chats:
         chat.append(int(c["chat_id"]))
     for i in chat:
         try:
           m = await client.send_message(chat_id=i, text=text)
           dn += 1
           if pn.text == "نعم":
                try:
                 await m.pin(disable_notification=False)
                except:
                   continue
         except FloodWait as e:
                    flood_time = int(e.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
         except Exception as e:
                    fd += 1
                    continue
     return await message.reply_text(f"**تمت الاذاعه بنجاح .⚡**\n\n**تمت الاذاعه الي : {dn}**\n**وفشل : {fd}**")
   elif command == "• اذاعه عام بالمساعد •":
     user = await get_userbot(bot_username)
     async for i in user.get_dialogs():
         try:
           m = await user.send_message(chat_id=i.chat.id, text=text)
           dn += 1
           if pn.text == "نعم":
                try:
                 await m.pin(disable_notification=False)
                except:
                   continue
         except FloodWait as e:
                    flood_time = int(e.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
         except Exception as e:
                    fd += 1
                    continue
     return await message.reply_text(f"**تمت الاذاعه بنجاح .⚡**\n\n**تمت الاذاعه الي : {dn}**\n**وفشل : {fd}**")
   elif command == "• اذاعه للمجموعات بالبوت •":
     chats = await get_served_chats(client)
     chat = []
     for c in chats:
         chat.append(int(c["chat_id"]))
     for i in chat:
         try:
           m = await client.send_message(chat_id=i, text=text)
           dn += 1
           if pn.text == "نعم":
                try:
                 await m.pin(disable_notification=False)
                except:
                   continue
         except FloodWait as e:
                    flood_time = int(e.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
         except Exception as e:
                    fd += 1
                    continue
     return await message.reply_text(f"**تمت الاذاعه بنجاح .⚡**\n\n**تمت الاذاعه الي : {dn}**\n**وفشل : {fd}**")
   elif command == "• اذاعه للمجموعات بالمساعد •":
     user = await get_userbot(bot_username)
     async for i in user.get_dialogs():
         if not i.chat.type == enums.ChatType.PRIVATE:
          try:
           m = await user.send_message(chat_id=i.chat.id, text=text)
           dn += 1
           if pn.text == "نعم":
                try:
                 await m.pin(disable_notification=False)
                except:
                   continue
          except FloodWait as e:
                    flood_time = int(e.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
          except Exception as e:
                    fd += 1
                    continue
     return await message.reply_text(f"**تمت الاذاعه بنجاح .⚡**\n\n**تمت الاذاعه الي : {dn}**\n**وفشل : {fd}**")

# قسم التحكم ف المساعد

@Client.on_message(filters.command("• قسم التحكم في المساعد •", ""))
async def helpercn(client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    userbot = await get_userbot(bot_username)
    me = userbot.me
    i = f"@{me.username} : {me.id}" if me.username else me.id
    b = await client.get_chat(me.id)
    b = b.bio if b.bio else "لا يوجد بايو"
    if message.chat.id == dev or message.chat.username in OWNER:
        kep = ReplyKeyboardMarkup([
            ["• فحص المساعد •"],
            ["• تغير الاسم الاول •", "• تغير الاسم التاني •"],
            ["• تغير البايو •"],
            ["• تغير اسم المستخدم •"],
            ["• اضافه صوره •", "• ازالة الصور •"],
            ["• دعوه المساعد الي الانضمام •"],
            ["• رجوع للقائمة الرئيسيه •"]
        ], resize_keyboard=True)
        await message.reply_text(
            f"**أهلا بك عزيزي المطور **\n**هنا قسم الحساب المساعد**\n**{me.mention}**\n**{i}**\n**{b}**",
            reply_markup=kep
        )


@Client.on_message(filters.command("• فحص المساعد •", ""))
async def userrrrr(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        userbot = await get_userbot(bot_username)
        mm = await message.reply_text("Collecting stats")
        start = datetime.now()
        u = g = sg = c = b = a_chat = 0
        Meh = userbot.me
        usere = Meh.mention
        async for dialog in userbot.get_dialogs():
            type = dialog.chat.type
            if type == enums.ChatType.PRIVATE:
                u += 1
            elif type == enums.ChatType.BOT:
                b += 1
            elif type == enums.ChatType.GROUP:
                g += 1
            elif type == enums.ChatType.SUPERGROUP:
                sg += 1
                user_s = await dialog.chat.get_member(int(Meh.id))
                if user_s.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    a_chat += 1
            elif type == enums.ChatType.CHANNEL:
                c += 1

        end = datetime.now()
        ms = (end - start).seconds
        await mm.edit_text(
            f"""**ꜱᴛᴀᴛꜱ ꜰᴇᴀᴛᴄʜᴇᴅ ɪɴ {ms} ꜱᴇᴄᴏɴᴅꜱ ⚡**
⚡**ʏᴏᴜ ʜᴀᴠᴇ {u} ᴘʀɪᴠᴀᴛᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.**
🏷️**ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ {g} ɢʀᴏᴜᴘꜱ.**
🏷️**ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ {sg} ꜱᴜᴘᴇʀ ɢʀᴏᴜᴘꜱ.**
🏷️**ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ {c} ᴄʜᴀɴɴᴇʟꜱ.**
🏷️**ʏᴏᴜ ᴀʀᴇ ᴀᴅᴍɪɴꜱ ɪɴ {a_chat} ᴄʜᴀᴛꜱ.**
🏷️**ʙᴏᴛꜱ ɪɴ ʏᴏᴜʀ ᴘʀɪᴠᴀᴛᴇ = {b}**
⚠️**ꜰᴇᴀᴛᴄʜᴇᴅ ʙʏ ᴜꜱɪɴɢ {usere} **"""
        )


@Client.on_message(filters.command("• تغير الاسم الاول •", ""))
async def changefisrt(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        try:
            name = await client.ask(message.chat.id, "• ارسل الان الاسم الجديد •")
            client_userbot = await get_userbot(bot_username)
            await client_userbot.update_profile(first_name=name.text)
            await message.reply_text("**تم تغير اسم الحساب المساعد بنجاح .⚡**")
        except Exception as es:
            await message.reply_text(f"حدث خطأ أثناء تغير الاسم \n {es}")


@Client.on_message(filters.command("• تغير الاسم التاني •", ""))
async def changelast(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        try:
            name = await client.ask(message.chat.id, "• ارسل الان الاسم الجديد •")
            client_userbot = await get_userbot(bot_username)
            await client_userbot.update_profile(last_name=name.text)
            await message.reply_text("**تم تغير اسم الحساب المساعد بنجاح .⚡**")
        except Exception as es:
            await message.reply_text(f"حدث خطأ أثناء تغير الاسم \n {es}")


@Client.on_message(filters.command("• تغير البايو •", ""))
async def changebio(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        try:
            bio = await client.ask(message.chat.id, "• ارسل الان البايو الجديد •")
            client_userbot = await get_userbot(bot_username)
            await client_userbot.update_profile(bio=bio.text)
            await message.reply_text("**تم تغير البايو بنجاح .⚡**")
        except Exception as es:
            await message.reply_text(f"حدث خطأ أثناء تغير البايو \n {es}")


@Client.on_message(filters.command("• تغير اسم المستخدم •", ""))
async def changeusername(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        try:
            username = await client.ask(message.chat.id, "• ارسل الان اسم المستخدم الجديد •")
            client_userbot = await get_userbot(bot_username)
            await client_userbot.set_username(username.text)
            await message.reply_text("**تم تغير اسم المستخدم بنجاح .⚡**")
        except Exception as es:
            await message.reply_text(f"حدث خطأ أثناء تغير اسم المستخدم \n {es}")


@Client.on_message(filters.command(["• اضافه صوره •"], ""))
async def changephoto(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        try:
            m = await client.ask(message.chat.id, "قم بإرسال الصوره الجديده الان")
            photo = await m.download()
            client_userbot = await get_userbot(bot_username)
            await client_userbot.set_profile_photo(photo=photo)
            await message.reply_text("**تم تغير صوره الحساب المساعد بنجاح .⚡**")
        except Exception as es:
            await message.reply_text(f"حدث خطأ أثناء تغير الصوره \n {es}")


@Client.on_message(filters.command(["• ازاله صوره •"], ""))
async def changephotos(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        try:
            client_userbot = await get_userbot(bot_username)
            photos = await client_userbot.get_profile_photos("me")
            await client_userbot.delete_profile_photos([p.file_id for p in photos])
            await message.reply_text("**تم ازاله صوره بنجاح .⚡**")
        except Exception as es:
            await message.reply_text(f"حدث خطأ أثناء ازاله الصوره \n {es}")


@Client.on_message(filters.command("• دعوه المساعد الي الانضمام •", ""))
async def joined(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        try:
            link = await client.ask(message.chat.id, "• ارسل الان الرابط •")
            chat = link.text
            if "https" in chat and "+" not in chat:
                chat = chat.replace("https://t.me/", "")
            client_userbot = await get_userbot(bot_username)
            await client_userbot.join_chat(chat)
            await message.reply_text("**تم انضمام الحساب المساعد بنجاح .⚡**")
        except Exception as es:
            await message.reply_text(f"حدث خطأ أثناء الانضمام \n {es}")


# قسم سجل التشغيل

@Client.on_message(filters.command(["• تغير مكان سجل التشغيل •", "• تفعيل سجل التشغيل •", "• تعطيل سجل التشغيل •"], ""))
async def set_history(client: Client, message):
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if message.chat.id == dev or message.chat.username in OWNER:
        cmd = message.command[0]
        if cmd == "• تغير مكان سجل التشغيل •":
            ask = await client.ask(message.chat.id, "** قم بارسال يوزرنيم أو ايدي الذي تريد تعيينه **", timeout=30)
            logger = ask.text
            if "@" in logger:
                logger = logger.replace("@", "")
        Botts = Bots.find({})
        for i in Botts:
            if i["bot_username"] == bot_username:
                dev = i["dev"]
                token = i["token"]
                session = i["session"]
                loogger = i["logger"]
                logger_mode = i["logger_mode"]
                client_userbot = await get_userbot(bot_username)
                try:
                    if cmd == "• تغير مكان سجل التشغيل •":
                        if i["logger"] == logger:
                            return await ask.reply_text("**هذا هو مكان السجل بالفعل .⚡**")
                        await client.send_message(logger, "**جاري الفحص ...**")
                        await client_userbot.send_message(logger, "**جاري تغير مكان السجل ..**")
                        Bots.delete_one({"bot_username": bot_username})
                        await asyncio.sleep(2)
                        Bots.insert_one({
                            "bot_username": bot_username, "token": token, "session": session,
                            "dev": dev, "logger": logger, "logger_mode": logger_mode
                        })
                        log[bot_username] = logger
                        await ask.reply_text("**تم تغير سجل التشغيل بنجاح ✅**")
                    else:
                        mode = "ON" if cmd == "• تفعيل سجل التشغيل •" else "OFF"
                        if i["logger_mode"] == mode:
                            m = "مفعل" if cmd == "• تفعيل سجل التشغيل •" else "معطل"
                            return await message.reply_text(f"**سجل التشغيل {m} من قبل .⚡**")
                        Bots.delete_one({"bot_username": bot_username})
                        Bots.insert_one({
                            "bot_username": bot_username, "token": token, "session": session,
                            "dev": dev, "logger": loogger, "logger_mode": mode
                        })
                        logm[bot_username] = mode
                        m = "تفعيل" if cmd == "• تفعيل سجل التشغيل •" else "تعطيل"
                        await message.reply_text(f"**تم {m} سجل التشغيل بنجاح ✅**")
                except Exception:
                    await message.reply_text("**تاكد من اضافه البوت والمساعد وترقيتهم مشرف**")
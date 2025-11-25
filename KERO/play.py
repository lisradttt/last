from pyrogram import Client, filters
from youtubesearchpython.__future__ import VideosSearch
import os
import aiohttp
import requests
import random
import asyncio
import yt_dlp
from datetime import datetime, timedelta
import pytgcalls
from typing import Union
from pyrogram.errors import ChatAdminRequired, UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType, ChatMemberStatus
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall, TelegramServerError
from pytgcalls.types import (
    JoinedGroupCallParticipant, LeftGroupCallParticipant, Update,
    AudioPiped, AudioVideoPiped, StreamAudioEnded,
    HighQualityAudio, HighQualityVideo,
    LowQualityAudio, LowQualityVideo,
    MediumQualityAudio, MediumQualityVideo
)

from config import API_ID, API_HASH, MONGO_DB_URL, VIDEO, OWNER, OWNER_NAME, LOGS, GROUP, CHANNEL
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_

# استخدام VIDEO كصورة افتراضية أو قيمة افتراضية
PHOTO = VIDEO if VIDEO else "https://graph.org/file/bbe526c61648eebca422c.jpg"
from bot import bot as man
from KERO.info import db, add, is_served_call, add_active_video_chat, add_served_call, add_active_chat, gen_thumb, download, remove_active, joinch
from KERO.Data import get_logger, get_userbot, get_call, get_logger_mode, get_group, get_channel

mongodb = _mongo_client_(MONGO_DB_URL)

# ==================== وظائف مساعدة ====================
async def join_assistant(client, chat_id, message_id, userbot, file_path):
    join = None
    try:
        user = userbot.me
        user_id = user.id
        get = await client.get_chat_member(chat_id, user_id)
        if get.status == ChatMemberStatus.BANNED:
            await client.send_message(
                chat_id,
                f"**قم بالغاء الحظر عن الحساب المساعد لتفعيل البوت**.\n\n @{user.username} : **الحساب المساعد **⚡.\n** قم بتنظيف قايمه المستدخمين ⚡.**\n\n** @e2zzz | @ISIIQ : او تواصل مع المطور من هنا ⚡.**",
                reply_to_message_id=message_id
            )
        else:
            join = True
    except UserNotParticipant:
        chat = await client.get_chat(chat_id)
        try:
            invitelink = chat.invite_link or await client.export_chat_invite_link(chat_id)
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
            await userbot.join_chat(invitelink)
            join = True
        except UserAlreadyParticipant:
            join = True
        except ChatAdminRequired:
            return await client.send_message(chat_id, f"**قم اعطاء البوت صلاحيه اضافه المستخدمين عبر الرابط .⚡**", reply_to_message_id=message_id)
        except Exception:
            await client.send_message(chat_id, f"** حدث خطأ حاول مرا آخري لاحقا**\n**{GROUP} : او تواصل مع الدعم من هنا .⚡**", reply_to_message_id=message_id)
    return join        

async def join_call(client, message_id, chat_id, bot_username, file_path, link, vid: Union[bool, str] = None):
    userbot = await get_userbot(bot_username)
    Done = None
    try:
        call = await get_call(bot_username)
    except:
        return Done
    audio_stream_quality = MediumQualityAudio()
    video_stream_quality = MediumQualityVideo()
    stream = AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality) if vid else AudioPiped(file_path, audio_parameters=audio_stream_quality)
    try:
        await call.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        Done = True
    except NoActiveGroupCall:
        h = await join_assistant(client, chat_id, message_id, userbot, file_path)
        if h:
            try:
                await call.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
                Done = True
            except Exception:
                await client.send_message(chat_id, "**قم بتشغيل المكالمة أولاً .🚦**", reply_to_message_id=message_id)
    except AlreadyJoinedError:
        await client.send_message(chat_id, "**قم بإعادة تشغيل المكالمة ..🚦**", reply_to_message_id=message_id)
    except TelegramServerError:
        await client.send_message(chat_id, "**قم بإعادة تشغيل المكالمة ..🚦**", reply_to_message_id=message_id)
    except Exception as a:
        print(a)
    return Done

def seconds_to_min(seconds):
    if seconds is not None:
        seconds = int(seconds)
        d, h, m, s = (seconds // (3600 * 24), seconds // 3600 % 24, seconds % 3600 // 60, seconds % 60)
        if d > 0:
            return "{:02d}:{:02d}:{:02d}:{:02d}".format(d, h, m, s)
        elif h > 0:
            return "{:02d}:{:02d}:{:02d}".format(h, m, s)
        elif m > 0:
            return "{:02d}:{:02d}".format(m, s)
        elif s > 0:
            return "00:{:02d}".format(s)
    return "-"

async def logs(bot_username, client, message):
    try:
        if await get_logger_mode(bot_username) == "OFF":
            return
        logger = await get_logger(bot_username)
        log = LOGS
        chat = f"[{message.chat.title}](t.me/{message.chat.username})" if message.chat.username else message.chat.title
        if message.chat.type == ChatType.CHANNEL:
            name = message.author_signature or chat
            text = f"**Playing History **\n\n**Chat : {chat}**\n**Chat Id : {message.chat.id}**\n**User Name : {name}**\n\n**Played : {message.text}**"
        else:
            user = f"User Username : @{message.from_user.username}" if message.from_user.username else f"User Id : {message.from_user.id}"
            text = f"**Playing History **\n\n**Chat : {chat}**\n**Chat Id : {message.chat.id}**\n**User Name : {message.from_user.mention}**\n**{user}**\n\n**Played : {message.text}**"
        await client.send_message(logger, text=text, disable_web_page_preview=True)
        await man.send_message(log, text=f"[ @{bot_username} ]\n{text}", disable_web_page_preview=True)
    except:
        pass

# ==================== تشغيل عشوائي ====================
@Client.on_message(filters.command(["عشوائي", "تشغيل عشوائي"], ""))
async def aii(client: Client, message):
    if await joinch(message):
        return
    try:
        chat_id = message.chat.id
        bot_username = client.me.username
        rep = await message.reply_text("**جاري اختيار تشغيل عشوائي ♻️**")
        call = await get_call(bot_username)
        try:
            await call.get_call(message.chat.id)
        except pytgcalls.exceptions.GroupCallNotFound:
            await remove_active(bot_username, chat_id)
        message_id = message.id
        user = await get_userbot(bot_username)
        req = message.from_user.mention if message.from_user else message.chat.title
        raw_list = []
        async for msg in user.get_chat_history("ELNQYBMUSIC"):
            if msg.audio:
                raw_list.append(msg)
        x = random.choice(raw_list)
        file_path = await x.download()
        file_name = x.audio.title
        title = file_name
        dur = x.audio.duration
        duration = seconds_to_min(dur)
        photo = PHOTO
        vid = True if x.video else None
        user_id = message.from_user.id if message.from_user else "ISIIQ"
        videoid = None
        link = None
        await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
        if not await is_served_call(client, message.chat.id): 
            await add_active_chat(chat_id)
            await add_served_call(client, chat_id)
            if vid:
                await add_active_video_chat(chat_id)
            await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
        await rep.delete()
        gr = await get_group(bot_username)
        ch = await get_channel(bot_username)
        button = [
            [InlineKeyboardButton(text="END", callback_data="stop"),
             InlineKeyboardButton(text="RESUME", callback_data="resume"),
             InlineKeyboardButton(text="PAUSE", callback_data="pause")],
            [InlineKeyboardButton(text="{قنـاه الــسوري}", url=f"{ch}"),
             InlineKeyboardButton(text="{جــروب الـدعم}", url=f"{gr}")],
            [InlineKeyboardButton(text=f"{OWNER_NAME}", url=f"https://t.me/{OWNER[0]}")],
            [InlineKeyboardButton(text="• اضفني الي مجموعتك 🐈‍⬛", url=f"https://t.me/{bot_username}?startgroup=True")]
        ]
        await message.reply_photo(photo=photo, caption=f"**Started Stream Random **\n\n**Song Name : {title}**\n**Duration Time : {duration}**\n**Requests By : {req}**", reply_markup=InlineKeyboardMarkup(button))
        await logs(bot_username, client, message)
        await asyncio.sleep(4)
        os.remove(file_path)
    except Exception:
        pass

#النص للتاني 
@Client.on_message(filters.command(["/play", "play", "/vplay", "شغل", "تشغيل", "فيد", "فيديو"], ""))
async def play(client: Client, message):
    if await joinch(message):
        return
    KERO = message
    bot_username = client.me.username
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else "ISIIQ"
    message_id = message.id
    gr = await get_group(bot_username)
    ch = await get_channel(bot_username)
    button = [
        [InlineKeyboardButton(text="End", callback_data="stop"),
         InlineKeyboardButton(text="Resume", callback_data="resume"),
         InlineKeyboardButton(text="Pause", callback_data="pause")],
        [InlineKeyboardButton(text="{قــناه الســورس}", url=f"{ch}"),
         InlineKeyboardButton(text="{جــروب الـدعم}", url=f"{gr}")],
        [InlineKeyboardButton(text=f"{OWNER_NAME}", url="https://t.me/ISIIQ")],
        [InlineKeyboardButton(text="أضفني لـ جروبك 🐾.", url=f"https://t.me/{bot_username}?startgroup=True")]
    ]
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "**♪ لا يمكنك التشغيل هنا للأسف 💎 .\n♪ قم بإضافة البوت لمجموعتك للتشغيل 💎 .**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("أضفني لـ جروبك 🐾.", url=f"https://t.me/{bot_username}?startgroup=True")]])
        )
    if message.sender_chat and message.chat.type != ChatType.CHANNEL:
        return await message.reply_text("**♪ يمكنك التشغيل بحسابك الخاص فقط 💎 .**")
    if not len(message.command) == 1:
        rep = await message.reply_text("**♪ جاري التشغيل انتظر قليلا 💎 .**")
    else:
        rep = await message.reply_text("**♪ جاري التشغيل انتظر قليلا 💎 .**")
    
    try:
        call = await get_call(bot_username)
    except:
        await remove_active(bot_username, chat_id)
    
    try:
        await call.get_call(message.chat.id)
    except pytgcalls.exceptions.GroupCallNotFound:
        await remove_active(bot_username, chat_id)
    
    # التعامل مع الرسائل بدون reply
    if not message.reply_to_message:
        if len(message.command) == 1:
            if message.chat.type == ChatType.CHANNEL:
                return await message.reply_text("**♪ قم كتابة شيئ لتشغيلة 💎 .**")
            try:
                name_msg = await client.ask(
                    message.chat.id,
                    text="**♪ ارسل اسم او رابط الي تريد تشغيله 💎 .**",
                    reply_to_message_id=message.id,
                    filters=filters.user(message.from_user.id),
                    timeout=200
                )
                name = name_msg.text
            except:
                return
        else:
            name = message.text.split(None, 1)[1]

        try:
            results = await VideosSearch(name, limit=1).next()
        except Exception:
            return await rep.edit("**♪ لم يتم العثور علي نتائج 💎 .**")
        
        result = results["result"][0]
        title = result["title"]
        duration = result.get("duration", "00:00")
        videoid = result["id"]
        yturl = result["link"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vid = True if any(x in message.command[0] for x in ["v", "ف"]) else None
        
        await rep.edit("**♪ جاري التشغيل انتظر قليلا ⚡ .**")
        link = yturl
        
        if await is_served_call(client, message.chat.id):
            chat_id = message.chat.id
            file_path = None
            await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            chatname = f"[{message.chat.title}](https://t.me/{message.chat.username})" if message.chat.username else message.chat.title
            chatname = message.author_signature if message.author_signature else chatname
            requester = chatname if getattr(KERO, "views", False) else f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            photo = PHOTO
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Add Track To Playlist : 🥁 .\n\n♪ Song Name : {title[:18]} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)
        else:
            chat_id = message.chat.id
            await add_active_chat(chat_id)
            await add_served_call(client, chat_id)
            if vid:
                await add_active_video_chat(chat_id)
            file_path = await download(bot_username, link, vid)
            await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
            if not c:
                await remove_active(bot_username, chat_id)
                return await rep.delete()
            requester = message.from_user.mention if message.from_user else chatname
            photo = await gen_thumb(videoid, PHOTO)
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Startling Playing Now 🥁 .\n\n♪ Song Name : {title[:18]} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)
        await rep.delete()
    
    else:
        # التعامل مع reply
        if not message.reply_to_message.media:
            return
        rep = await message.reply_text("**♪ جاري تشغيل الملف انتظر قليلا 🚦 .**")
        file_path = await message.reply_to_message.download()
        if hasattr(message.reply_to_message, "audio"):
            file_name = message.reply_to_message.audio
        elif hasattr(message.reply_to_message, "voice"):
            file_name = message.reply_to_message.voice
        elif hasattr(message.reply_to_message, "video"):
            file_name = message.reply_to_message.video
        else:
            file_name = message.reply_to_message.document
        title = getattr(file_name, "file_name", "Unknown")
        duration = seconds_to_min(getattr(file_name, "duration", 0))
        vid = True if getattr(message.reply_to_message, "video", None) or getattr(message.reply_to_message, "document", None) else None
        link = None
        
        if await is_served_call(client, message.chat.id):
            chat_id = message.chat.id
            videoid = None
            await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            position = len(db.get(f"{bot_username}{chat_id}", [])) - 1
            requester = message.from_user.mention if message.from_user else message.chat.title
            photo = PHOTO
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Add Track To Playlist : {position} 🥁 .\n\n♪ Song Name : {title} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)
        else:
            chat_id = message.chat.id
            videoid = None
            await add_active_chat(chat_id)
            await add_served_call(client, chat_id)
            if vid:
                await add_active_video_chat(chat_id)
            await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
            if not c:
                await remove_active(bot_username, chat_id)
                return await rep.delete()
            requester = message.from_user.mention if message.from_user else message.chat.title
            photo = await gen_thumb(videoid, PHOTO)
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Startling Playing Now 🥁 .\n\n♪ Song Name : {title} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)
    
    try:
        os.remove(file_path)
    except:
        pass
    await rep.delete()
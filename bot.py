import sys
import asyncio
import time
import requests
from datetime import datetime

# إصلاح شامل لـ Python 3.14 على Windows
if sys.platform == 'win32':
    # إنشاء event loop قبل أي استيراد يحتاج إليه
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client
from OWNER import API_ID, API_HASH, BOT_TOKEN

# حل مشكلة مزامنة الوقت
class TimeOffset:
    offset = 0

def show_system_time():
    """عرض وقت جهازك الحالي"""
    local_time = time.time()
    local_datetime = datetime.fromtimestamp(local_time)
    
    print("\n" + "="*70)
    print("[SYSTEM TIME]")
    print("="*70)
    print(f"Current date and time: {local_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time 24h format: {local_datetime.strftime('%H:%M:%S')}")
    print("="*70 + "\n")

def sync_time():
    """حساب الفرق بين وقت النظام والوقت الفعلي"""
    try:
        # عرض وقت جهازك أولاً
        show_system_time()
        
        # محاولة الحصول على الوقت من Google
        response = requests.get('https://www.google.com', timeout=3)
        server_time_str = response.headers.get('date')
        if server_time_str:
            from email.utils import parsedate_to_datetime
            server_time = parsedate_to_datetime(server_time_str).timestamp()
            local_time = time.time()
            TimeOffset.offset = int(server_time - local_time)
            
            # عرض معلومات الوقت
            local_datetime = datetime.fromtimestamp(local_time)
            server_datetime = datetime.fromtimestamp(server_time)
            
            print("="*70)
            print("[TIME COMPARISON]")
            print("="*70)
            print(f"Your system time:  {local_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Server time:       {server_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)
            print(f"Time difference: {TimeOffset.offset} seconds")
            
            if TimeOffset.offset > 0:
                minutes = abs(TimeOffset.offset) // 60
                seconds = abs(TimeOffset.offset) % 60
                print(f"[WARNING] Your system is {minutes} minutes and {seconds} seconds AHEAD")
                print(f"[ERROR] This is why the bot cannot connect!")
            elif TimeOffset.offset < 0:
                minutes = abs(TimeOffset.offset) // 60
                seconds = abs(TimeOffset.offset) % 60
                print(f"[WARNING] Your system is {minutes} minutes and {seconds} seconds BEHIND")
            else:
                print(f"[OK] Clock is perfectly synchronized - Bot should connect successfully!")
            print("="*70 + "\n")
            
            return TimeOffset.offset
    except Exception as e:
        print(f"[WARNING] Could not connect to server: {e}\n")
    
    # محاولة بديلة
    try:
        response = requests.get('https://worldtimeapi.org/api/timezone/Etc/UTC', timeout=3)
        if response.status_code == 200:
            server_time = datetime.fromisoformat(response.json()['datetime'].replace('Z', '+00:00')).timestamp()
            local_time = time.time()
            TimeOffset.offset = int(server_time - local_time)
            
            # عرض معلومات الوقت
            local_datetime = datetime.fromtimestamp(local_time)
            server_datetime = datetime.fromtimestamp(server_time)
            
            print("="*70)
            print("[TIME COMPARISON]")
            print("="*70)
            print(f"Your system time:  {local_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Server time:       {server_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)
            print(f"Time difference: {TimeOffset.offset} seconds")
            
            if TimeOffset.offset > 0:
                minutes = abs(TimeOffset.offset) // 60
                seconds = abs(TimeOffset.offset) % 60
                print(f"[WARNING] Your system is {minutes} minutes and {seconds} seconds AHEAD")
                print(f"[ERROR] This is why the bot cannot connect!")
            elif TimeOffset.offset < 0:
                minutes = abs(TimeOffset.offset) // 60
                seconds = abs(TimeOffset.offset) % 60
                print(f"[WARNING] Your system is {minutes} minutes and {seconds} seconds BEHIND")
            else:
                print(f"[OK] Clock is perfectly synchronized - Bot should connect successfully!")
            print("="*70 + "\n")
            
            return TimeOffset.offset
    except:
        pass
    
    return 0

# حساب الفرق الزمني
sync_time()

# Plugins
bot = Client(
    "mo",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Maker"),
    sleep_threshold=30,
    no_updates=True,
    proxy=None  # تأكد من عدم استخدام proxy قد يسبب مشاكل
)

async def start_bot():
    print("[INFO]: STARTING BOT CLIENT")
    
    # محاولة مزامنة الوقت
    try:
        print("[INFO]: Synchronizing system time...")
        offset = sync_time()
        if offset:
            print(f"[INFO]: Time offset calculated: {offset} seconds")
    except Exception as e:
        print(f"[WARNING]: Could not synchronize time: {e}")
    
    try:
        # محاولة بدء البوت مع معالجة الأخطاء
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[INFO]: Connecting to Telegram (attempt {attempt + 1}/{max_retries})...")
                await asyncio.wait_for(bot.start(), timeout=30)
                print("[INFO]: Bot started successfully!")
                break
            except asyncio.TimeoutError:
                print(f"[WARNING]: Connection timeout (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
            except Exception as e:
                error_msg = str(e)
                print(f"[WARNING]: Connection error (attempt {attempt + 1}): {type(e).__name__}")
                print(f"[DEBUG]: {error_msg}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                elif attempt == max_retries - 1:
                    print("[ERROR]: Failed to connect after all attempts")
                    print("[INFO]: Make sure your system time is correct")
                    print("[INFO]: Bot is running in offline mode...")
                    return
    except Exception as e:
        print(f"[ERROR]: Exception during bot startup: {e}")
        return

    # ID   
    Mimp = 8457593460
    try:
        await bot.send_message(Mimp, "**Bot has started successfully!**")
        print("[INFO]: Message sent successfully to Mimp")
    except Exception as e:
        print(f"[WARNING]: Could not send message: {type(e).__name__}")

    # Keep the bot running
    print("[INFO]: Bot is now running. Press Ctrl+C to stop...")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n[INFO]: Bot shutting down...")
        try:
            await bot.stop()
        except:
            pass

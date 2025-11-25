import sys
import asyncio

# إصلاح شامل لـ Python 3.14 على Windows
if sys.platform == 'win32':
    # إنشاء event loop قبل أي استيراد يحتاج إليه
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

from bot import start_bot

async def main():
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())

import re
from datetime import datetime, timedelta
import asyncio
from telethon import TelegramClient, events

# Telegram API ma'lumotlari
api_id = '28482100'  # my.telegram.org dan olingan api_id
api_hash = 'f45816c3036557491783dc5a6d8d843f'  # my.telegram.org dan olingan api_hash
phone = '+998888082511'  # Telefon raqamingiz (+998901234567 formatida)

# Telethon clientni yaratish
client = TelegramClient('session_name', api_id, api_hash)

# Taymer patterni
TIMER_PATTERN = r'#taymer_(\d{2})_(\d{2})_(\d{2})'

@client.on(events.NewMessage(pattern=TIMER_PATTERN))
async def handle_timer(event):
    # Xabardan vaqtni olish
    match = re.match(TIMER_PATTERN, event.raw_text)
    if not match:
        return

    hours, minutes, seconds = map(int, match.groups())

    # Vaqtni tekshirish
    if hours > 23 or minutes > 59 or seconds > 59:
        await event.reply("Noto'g'ri vaqt formati! Iltimos, HH:MM:SS formatida 00:00:00 dan 23:59:59 gacha kiriting.")
        return

    # Joriy vaqt va maqsad vaqtni olish
    now = datetime.now()
    start_time = now
    target_time = now.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)

    # Agar maqsad vaqt o'tgan bo'lsa, keyingi kun uchun hisoblaymiz
    if target_time <= now:
        target_time += timedelta(days=1)

    # Boshlanish va stop vaqtlarini formatlash
    start_time_str = start_time.strftime("%H:%M:%S")
    stop_time_str = target_time.strftime("%H:%M:%S")

    # Dastlabki xabarni yuborish
    message = await event.reply("Taymer boshlandi! Hisoblayman...")

    while True:
        now = datetime.now()
        if now >= target_time:
            await message.edit(f"Taymer tugadi!\nStop vaqti: {stop_time_str}")
            break

        # Qolgan vaqtni hisoblash
        delta = target_time - now
        total_seconds = int(delta.total_seconds())

        # Qolgan vaqtni formatlash
        hours_left = total_seconds // 3600
        minutes_left = (total_seconds % 3600) // 60
        seconds_left = total_seconds % 60

        if total_seconds > 3600:
            time_str = f"{hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}"
        else:
            time_str = f"{total_seconds} sekund"

        try:
            await message.edit(f"Qoldi: {time_str}\nStop vaqti: {stop_time_str}")
        except Exception as e:
            print(f"Xabarni tahrirlashda xato: {e}")
            break

        # 5 soniya kutish
        await asyncio.sleep(5)

async def main():
    # Clientni ishga tushirish
    await client.start(phone=phone)
    print("Client ishga tushdi. #taymer_HH_MM_SS formatida xabar yuboring.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
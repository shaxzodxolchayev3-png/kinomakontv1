import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# --- SOZLAMALAR ---
TOKEN = "8797934477:AAHWCJED5DJKpSO7XjiazZZo4AZJYJrNhMk"
ADMIN_ID = 7433354101  # O'zingizning ID raqamingiz

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- BAZANI SOZLASH ---
def init_db():
    conn = sqlite3.connect("movies_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            code TEXT PRIMARY KEY,
            file_id TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Salom! Kino kodini yuboring yoki admin bo'lsangiz yangi kino qo'shing.")

# --- ADMIN: KINO QO'SHISH ---
@dp.message(Command("add"), F.from_user.id == ADMIN_ID)
async def add_movie(message: types.Message):
    # Reply qilingan xabarda video yoki fayl borligini tekshiramiz
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.answer("⚠️ Videoga reply qilib /add kod deb yozing!")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Kodni kiritmadingiz! Masalan: /add 101")
        return

    kino_kodi = args[1]
    
    # Videoning file_id sini olish
    if message.reply_to_message.video:
        f_id = message.reply_to_message.video.file_id
    else:
        f_id = message.reply_to_message.document.file_id

    conn = sqlite3.connect("movies_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO movies (code, file_id) VALUES (?, ?)", (kino_kodi, f_id))
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ Tayyor! Endi {kino_kodi} deb yozilsa, ushbu video yuboriladi.")

# --- FOYDALANUVCHI: KINO QIDIRISH ---
@dp.message(F.text)
async def get_movie(message: types.Message):
    code = message.text
    
    conn = sqlite3.connect("movies_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM movies WHERE code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # file_id orqali videoni qayta yuboramiz
        await bot.send_video(chat_id=message.chat.id, video=result[0], caption=f"Kodingiz bo'yicha kino: {code}")
    else:
        if not code.startswith("/"):
            await message.answer("😔 Afsus, bu kod bilan kino topilmadi.")

async def main():
    print("Bot kanalga bog'lanmasdan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

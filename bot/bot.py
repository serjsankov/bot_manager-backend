from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import asyncio
from config import BOT_TOKEN, FRONTEND_URLS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# @dp.message(Command("start"))
# async def start_handler(message: types.Message):
#     kb = InlineKeyboardMarkup(inline_keyboard=[[
#         InlineKeyboardButton(
#             text="Открыть MiniApp 🚀", 
#             web_app=WebAppInfo(url=FRONTEND_URL)
#         )
#     ]])
#     await message.answer("Добро пожаловать! Открой мини‑приложение:", reply_markup=kb)
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать! Мини-приложение пока отключено, откройте фронт в браузере.")

@dp.message(Command("add"))
async def handle_group_message(msg: types.Message):
    # Проверяем, что сообщение из группы
    if msg.chat.type in ("group", "supergroup"):
        user_id = msg.from_user.id
        username = msg.from_user.full_name if hasattr(msg.from_user, 'full_name') else msg.from_user.username
        chat_name = msg.chat.title
        chat_id = msg.chat.id

        # Проверяем, есть ли username у группы
        if msg.chat.username:
            chat_link = f"https://t.me/{msg.chat.username}"
        else:
            try:
                invite_link = await bot.create_chat_invite_link(chat_id=chat_id)
                chat_link = invite_link.invite_link
            except Exception as e:
                chat_link = "Не удалось получить ссылку"
                print(f"Ошибка при создании ссылки для {chat_id}: {e}")

        text = (
            f"Здравствуй, {username}! Вы добавляете новый чат.\n\n"
            f"🗂 Имя чата: {chat_name}\n"
            f"🆔 ID чата: {chat_id}\n"
            f"🔗 Ссылка на чат: {chat_link}"
        )

        try:
            # Отправляем личное сообщение пользователю
            await bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            print(f"Не удалось отправить личное сообщение пользователю {user_id}: {e}")

async def start_polling():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_polling())
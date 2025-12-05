from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, BotCommand
from db.chats import add_chat_to_db
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
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="data", description="Показать мои данные"),
        BotCommand(command="add", description="Добавить группу в систему"),
    ]
    await bot.set_my_commands(commands)
    
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать! Откройте miniApp!")

@dp.message(Command("data"))
async def user_data(msg: types.Message):
    user_id = msg.from_user.id
    username = msg.from_user.username

    if not username:
        text = "⚠️ У вас нет username. Добавьте его в настройках Telegram, чтобы использовать MiniApp."
    else:
        text = (
            f"⚠ Ваши данные:\n"
            f"🆔 tg_id: {user_id}\n"
            f"👤 username: @{username}"
        )

    await msg.answer(text)

@dp.message(Command("add"))
async def handle_group_message(msg: types.Message):
    if msg.chat.type in ("group", "supergroup"):
        user_id = msg.from_user.id
        username = msg.from_user.full_name if hasattr(msg.from_user, 'full_name') else msg.from_user.username
        chat_name = msg.chat.title
        chat_id = msg.chat.id

        # Получаем ссылку на чат
        if msg.chat.username:
            chat_link = f"https://t.me/{msg.chat.username}"
        else:
            try:
                invite_link = await bot.create_chat_invite_link(chat_id=chat_id)
                chat_link = invite_link.invite_link
            except Exception as e:
                chat_link = "Не удалось получить ссылку"
                print(f"Ошибка при создании ссылки для {chat_id}: {e}")

        # Добавляем чат в БД и получаем результат
        added = await add_chat_to_db(group_id=chat_id, value=chat_name, link=chat_link, tg_id=user_id)

        # Формируем сообщение пользователю
        if added:
            text = (
                f"✅ Чат успешно добавлен в систему!\n\n"
                f"🗂 Имя чата: {chat_name}\n"
                f"🆔 ID чата: {chat_id}\n"
                f"🔗 Ссылка на чат: {chat_link}\n\n"
                f"Для добавления сотрудников откройте miniApp"
            )
        else:
            text = (
                f"⚠️ Этот чат уже был добавлен ранее.\n\n"
                f"🗂 Имя чата: {chat_name}\n"
                f"🆔 ID чата: {chat_id}\n"
                f"🔗 Ссылка на чат: {chat_link}"
            )

        # Отправляем личное сообщение пользователю
        try:
            await bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            print(f"Не удалось отправить личное сообщение пользователю {user_id}: {e}")


async def start_polling():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_polling())
# backend/services/telegram.py
from bot.bot import bot
from aiogram.exceptions import TelegramAPIError

async def notify_manager(tg_id: int, full_name: str, role: str, department: str):
    text = (
        f"👤 Новый сотрудник зарегистрировался:\n"
        f"ФИО: {full_name}\n"
        f"Должность: {role}\n"
        f"Отдел: {department}"
    )
    try:
        await bot.send_message(chat_id=tg_id, text=text)
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")

async def check_bot_in_chat(chat_id_or_link: str) -> bool:
    """
    Проверяет, добавлен ли бот в указанный чат (по ID или ссылке).
    Возвращает True, если бот имеет доступ, иначе False.
    """
    try:
        chat = await bot.get_chat(chat_id_or_link)
        # Можно вывести chat.type, chat.title и т.д. при необходимости
        print(f"✅ Бот имеет доступ к чату: {chat.id} ({chat.title if hasattr(chat, 'title') else '—'})")
        return True
    except TelegramAPIError as e:
        print(f"❌ Бот не имеет доступа к чату {chat_id_or_link}: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Ошибка при проверке доступа к чату {chat_id_or_link}: {e}")
        return False
    
# ✅ Новая функция: изменение названия чата
async def update_chat_title(group_id: int, new_title: str):
    """
    Меняет название телеграм-группы по её настоящему group_id.
    """
    try:
        print(f"🔧 Меняю название TG-чата {group_id} → '{new_title}'")
        await bot.set_chat_title(group_id, new_title)
        print(f"✅ Название успешно обновлено")
    except TelegramAPIError as e:
        print(f"❌ Ошибка Telegram API при смене названия: {e}")
    except Exception as e:
        print(f"⚠️ Не удалось обновить название для {group_id}: {e}")


# ✅ Улучшенная функция с логами
async def notify_user_about_group(user_id: int, group_name: str):
    try:
        print(f"📩 Пытаюсь отправить сообщение пользователю {user_id}")
        await bot.send_message(int(user_id), f"✅ Вас добавили в группу: {group_name}")
        print(f"✅ Сообщение отправлено пользователю {user_id}")
    except TelegramAPIError as e:
        print(f"❌ Telegram API Error для {user_id}: {e}")
    except Exception as e:
        print(f"⚠️ Не удалось отправить уведомление пользователю {user_id}: {e}")

async def notify_user_about_removal(user_id: int, group_name: str):
    """
    Уведомляет пользователя, что его удалили из группы
    """
    try:
        await bot.send_message(user_id, f"❌ Вас исключили из группы: {group_name}")
        print(f"📩 Отправлено уведомление об удалении пользователю {user_id}")
    except Exception as e:
        print(f"⚠️ Не удалось отправить уведомление об удалении пользователю {user_id}: {e}")

# async def send_message_manager_remove(user_id: int, user_name: str):
#     try:
#         await bot.send_message(int(user_id), f"Пользователь {user_name} уволен и удалён из чатов")
#     except Exception as e:
#         print(f"⚠️ Не удалось отправить уведомление об удалении пользователю {user_id}: {e}")
async def notify_manager_fired(tg_id: int, full_name: str, role: str, department: str):
    """
    Уведомляет директора о том, что сотрудник уволен
    """
    text = (
        f"⚠ Сотрудник уволен:\n"
        f"ФИО: {full_name}\n"
        f"Должность: {role}\n"
        f"Отдел: {department}"
    )
    try:
        await bot.send_message(chat_id=tg_id, text=text)
        print(f"✅ Уведомление директору {tg_id} отправлено")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления директору {tg_id}: {e}")
        

async def add_user_to_chat(tg_id: int, group_id: int, group_link: str, group_name: str):
    """
    Пытаемся добавить пользователя в Telegram-группу по group_id.
    Если не удалось, отправляем ссылку на группу в личку.
    """
    try:
        # Пробуем добавить пользователя в чат
        await bot.add_chat_members(chat_id=group_id, user_ids=[tg_id])
        # Уведомляем, что добавлен
        text = f"✅ Вы были добавлены в группу: {group_name}"
        if group_link:
            text += f"\nСсылка на группу: {group_link}"
        await bot.send_message(tg_id, text)
        print(f"✅ Пользователь {tg_id} добавлен в чат {group_id}")
    except TelegramAPIError as e:
        # Если не удалось добавить, отправляем ссылку
        print(f"⚠ Не удалось добавить {tg_id} в чат {group_id}: {e}")
        if group_link:
            try:
                await bot.send_message(tg_id, f"✅ Вы были приглашены в группу {group_name}.\nСсылка: {group_link}")
                print(f"✅ Отправлена ссылка пользователю {tg_id}")
            except Exception as e2:
                print(f"❌ Не удалось отправить ссылку пользователю {tg_id}: {e2}")
    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя {tg_id} в чат {group_id}: {e}")


async def remove_user_from_chat(group_id: int, user_tg_id: int):
    """
    Удаляет пользователя из Telegram-группы.
    """
    try:
        await bot.ban_chat_member(group_id, user_tg_id)
        await bot.unban_chat_member(group_id, user_tg_id)
        print(f"✅ Пользователь {user_tg_id} удалён из чата {group_id}")
    except TelegramAPIError as e:
        print(f"❌ Telegram API ошибка удаления: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка удаления {user_tg_id} из чата {group_id}: {e}")

async def notify_user_approved(tg_id: int):
    try:
        await bot.send_message(
            tg_id,
            "✅ Ваша заявка одобрена! Добро пожаловать в команду 🚀"
        )
        print(f"✅ Уведомление о принятии отправлено пользователю {tg_id}")
    except Exception as e:
        print(f"⚠ Не удалось отправить уведомление пользователю {tg_id}: {e}")
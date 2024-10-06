"""
Роутер для авторизации. В случае нашего бота - просим ввести пользователя контуровскую почту.
"""
import logging

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from configs.settings import CommonSettings
from helpers import staffhelper
from service_layer import service
from tg import strings
from tg.filters import filters

router = Router()
router.message.filter(filters.NotAuthFilter())


@router.message(StateFilter(None))
async def auth(message: Message, state: FSMContext) -> None:
    username = message.from_user.username
    if not username:
        await message.answer(strings.should_be_username_msg)
        return
    emails = await staffhelper.search_emails(username)
    if emails is None:
        await message.answer(strings.unexpected_action_msg)
        logging.warning(f"Ошибка при запросе в Стафф для пользователя {username}")
        return
    if len(emails) == 0:
        await message.answer(strings.no_telegram_in_staff_msg)
        logging.info(f"В Стаффе не найден телеграм пользователя {username}")
        return
    if len(emails) > 1:
        logging.warning(f"Для {username} найдено несколько почт: " + ", ".join(emails))
    user_email = emails[0]
    is_admin = user_email in CommonSettings().ADMINS.split()
    user = await service.auth(user_email, message.from_user.id, is_admin, message.chat.id, username)
    await state.clear()
    await message.answer(
        text=strings.auth_message(user.email, user.is_admin),
        reply_markup=ReplyKeyboardRemove()
    )

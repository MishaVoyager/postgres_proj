import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from arq import cron

from adapters import dbhelper
from configs.settings import CommonSettings, RedisConfig
from helpers.helpers import format_interval, format_date, get_time_now, get_word_ending
from service_layer.records_helper import get_visitor, get_resource_by_name
from service_layer.service import get_all_expired_records, delete_records, get_all_expiring_records

initialized = False


async def remind_about_return_time(ctx: Any) -> None:
    global initialized
    if not initialized:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        await dbhelper.start_db_async()
        initialized = True
    bot = Bot(token=CommonSettings().TOKEN)
    expired_records = await get_all_expired_records()
    for expired_record in expired_records:
        logging.info("Началась обработка expired records")
        visitor = await get_visitor(expired_record.email)
        if visitor.external_id is None:
            continue
        resource = await get_resource_by_name(expired_record.resource_name)
        try:
            await bot.send_message(
                chat_id=visitor.external_id,
                text=f"{resource.name} был автоматически освобожден. Ваша запись {format_interval(expired_record.take_date, expired_record.return_date, True)} закончилась"
            )
        except TelegramBadRequest:
            await bot.session.close()
            continue
    await delete_records(expired_records)
    for expiring_record in await get_all_expiring_records():
        logging.info("Началась обработка expiring records")
        visitor = await get_visitor(expiring_record.email)
        if visitor.external_id is None:
            continue
        resource = await get_resource_by_name(expiring_record.resource_name)
        days_to_expire = (expiring_record.return_date.date() - get_time_now().date()).days
        try:
            when = "сегодня" if days_to_expire == 0 else f"через {days_to_expire} {get_word_ending(days_to_expire, ['день', 'дня', 'дней'])}"
            message = f"Напоминание: {when} надо будет освободить {resource.name}"
            await bot.send_message(
                chat_id=visitor.external_id,
                text=message
            )
        except TelegramBadRequest:
            await bot.session.close()
            continue




class WorkerSettings:
    redis_settings = RedisConfig().get_pool_settings()
    cron_jobs = [
        cron(
            name="reminder",
            coroutine=remind_about_return_time,
            run_at_startup=False,
            keep_result=True,
            keep_result_forever=False,
            weekday={0, 1, 2, 3, 4},
            hour=7,
            minute=0
        )
        # cron(
        #     name="reminder",
        #     coroutine=remind_about_return_time,
        #     run_at_startup=False,
        #     keep_result=True,
        #     keep_result_forever=False,
        # )
    ]

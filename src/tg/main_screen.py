import datetime
from datetime import timedelta as td, datetime as dt, timezone as tz
from re import Match
from typing import List

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import helpers.helpers
from domain.models import Record, Visitor
from helpers.helpers import get_time_now, format_interval
from service_layer.records_helper import get_take_and_future_records, get_visitor_by_external_id, get_resource_by_name
from service_layer.service import get_stage_info_for_visitor, return_resource, take_resource
from tg import tghelper
from tg.aiogram_calendar.simple_calendar import SimpleCalendarCallback
from tg.tghelper import get_stages_dashboard, get_take_keyboard, get_calendar_ru

router = Router()


class ReservationOnCalendar(StatesGroup):
    choose_take_date = State()
    choose_return_date = State()
    confirm_reservation = State()


@router.message(Command("start"))
@router.message(Command("all"))
async def get_all_handler(message: Message) -> None:
    await get_all(message, message.from_user.id)


async def get_all(message: Message, visitor_external_id: int) -> None:
    visitor = await get_visitor_by_external_id(visitor_external_id)
    info = await get_stage_info_for_visitor(visitor.email)
    keyboard = get_stages_dashboard(info)
    await message.answer("Занятость стейджей", reply_markup=keyboard)


@router.callback_query(F.data.regexp(r"^calendar_(\w+)$").as_("match"))
async def choose_date_on_calendar_handler(call: CallbackQuery, state: FSMContext, match: Match[str]) -> None:
    await call.answer()
    await state.set_state(ReservationOnCalendar.choose_take_date)
    resource_name = match.group(1)
    await state.update_data(resource_name=resource_name)
    await call.message.delete()
    await call.message.answer(
        "Выберите дату начала бронирования",
        reply_markup=await get_calendar_ru().start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(ReservationOnCalendar.choose_take_date))
async def choose_take_date_from_calendar_hanlder(call: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await call.answer()
    calendar = get_calendar_ru()
    selected, date = await calendar.process_selection(call, callback_data)
    if not selected:
        return
    take_date = helpers.helpers.reduce_datetime_to_date_utc(date)
    if take_date.date() < get_time_now().date():
        await call.message.delete()
        await call.message.answer(
            "Вы выбрали дату из прошлого. Выберите другую",
            reply_markup=await calendar.start_calendar()
        )
        return
    await state.update_data(take_date=take_date)
    await state.set_state(ReservationOnCalendar.choose_return_date)
    await call.message.delete()
    await call.message.answer(
        "Выберите дату окончания бронирования",
        reply_markup=await calendar.start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(ReservationOnCalendar.choose_return_date))
async def choose_return_date_from_calendar_handler(call: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await call.answer()
    calendar = get_calendar_ru()
    selected, date = await calendar.process_selection(call, callback_data)
    if not selected:
        return
    return_date = helpers.helpers.reduce_datetime_to_date_utc(date)
    data = await state.get_data()
    take_date = data["take_date"]
    if return_date < take_date:
        await call.message.delete()
        await call.message.answer(
            "Дата окончания должна быть больше даты начала! Выберите другую дату окончания брони",
            reply_markup=await calendar.start_calendar()
        )
        return
    await state.update_data(return_date=return_date)
    await state.set_state(ReservationOnCalendar.confirm_reservation)
    resource_name = data["resource_name"]
    await call.message.delete()
    await call.message.answer(
        f"Точно записать на вас {resource_name} {format_interval(take_date, date, True)}?",
        reply_markup=tghelper.get_inline_keyboard(["Да", "Нет"], "confirm")
    )


@router.callback_query(StateFilter(ReservationOnCalendar.confirm_reservation))
async def confirm_reservation_on_calendar(call: CallbackQuery, state: FSMContext):
    await call.answer()
    answer = call.data.split()[1]
    if answer == "Да":
        data = await state.get_data()
        resource_name = data["resource_name"]
        take_date = dt.combine(data["take_date"].date(), datetime.time.min, tz.utc)
        return_date = dt.combine(data["return_date"].date(), datetime.time.max, tz.utc)
        resource, record, conflict_record = await take_resource(resource_name, call.from_user.id, take_date,
                                                                return_date)
        if record is None:
            await call.message.delete()
            await call.message.answer(
                f"Не удалось забронировать: {resource_name} занят {format_interval(conflict_record.take_date, conflict_record.return_date, True)} пользователем {conflict_record.email}"
            )
        else:
            await call.message.delete()
            await call.message.answer(
                f"Вы успешно забронировали {resource_name} {format_interval(take_date, return_date, True)}"
            )
    else:
        await call.message.delete()
        await call.message.answer("Бронирование отменено")
    await state.clear()
    await get_all(call.message, call.from_user.id)


@router.callback_query(F.data.regexp(r"^take_(\w+)$").as_("match"))
async def start_reservation_handler(call: CallbackQuery, match: Match[str]) -> None:
    await call.answer()
    resource_name = match.group(1)
    keyboard = get_take_keyboard(resource_name)
    await call.message.answer(
        text="На какой период занять стейдж? Укажите количество дней (1 = на сегодня) или выберите даты в календаре",
        reply_markup=keyboard)


@router.callback_query(F.data.regexp(r"^change_take_date_(\w+)_(\d+)$").as_("match"))
async def choose_return_date_handler(call: CallbackQuery, match: Match[str]) -> None:
    await call.answer()
    resource_name = match.group(1)
    number = int(match.group(2))
    keyboard = get_take_keyboard(resource_name, number)
    await call.message.edit_reply_markup(reply_markup=keyboard)


def format_notes(stage_name: str, visitor: Visitor, records: List[Record]) -> str:
    """Возвращает список записей с командой отмены для своих записей"""
    message = f"Список записей на {stage_name}:\r\n\r\n"
    for record in records:
        visitor_can_cancel = visitor.is_admin or record.email == visitor.email
        message += f"{format_interval(record.take_date, record.return_date, False)} на {record.email}"
        message += f". Снять бронь: /cancel{record.record_id}\r\n\r\n" if visitor_can_cancel else "\r\n\r\n"
    return message


@router.message(F.text.regexp(r"^\/cancel(\d+)$").as_("match"))
async def cancel_reservation_handler(message: Message, match: Match[str]) -> None:
    record_id = int(match.group(1))
    record, resource = await return_resource(record_id, message.from_user.id)
    if record is None:
        await message.answer("Не удалось отменить бронь. Запросите актуальный список записей и попробуйте снова")
        return
    await message.answer(
        f"Вы отменили бронь {resource.name}! Запись была {format_interval(record.take_date, record.return_date, True)}"
    )
    await get_all(message, message.from_user.id)


@router.callback_query(F.data.regexp(r"^confirm_days_(\w+)_(\d+)$").as_("match"))
async def confirm_reservation_handler(call: CallbackQuery, match: Match[str]) -> None:
    await call.answer()
    resource_name = match.group(1)
    number = int(match.group(2))
    take_date = dt.combine(get_time_now().date(), datetime.time.min, tz.utc)
    return_date = dt.combine(get_time_now() + td(days=number - 1), datetime.time.max, tz.utc)
    resource, record, conflict_record = await take_resource(resource_name, call.from_user.id, take_date, return_date)
    if record is None:
        await call.message.answer(f"Не удалось забронировать: {resource_name} занят в указанное время")
        await call.message.delete()
        await get_all(call.message, call.from_user.id)
        return
    await call.message.answer(
        f"Вы забронировали {resource_name} {format_interval(record.take_date, record.return_date, True)}"
    )
    await call.message.delete()
    await get_all(call.message, call.from_user.id)


@router.callback_query(F.data.regexp(r"^records_(\w+)$").as_("match"))
async def describe_stage_records_handler(call: CallbackQuery, match: Match[str]) -> None:
    await call.answer()
    resource_name = match.group(1)
    visitor = await get_visitor_by_external_id(call.from_user.id)
    records = list()
    take_record, future_records = await get_take_and_future_records(resource_name)
    if take_record is not None:
        records.append(take_record)
    records += future_records
    if len(records) == 0:
        await call.message.answer(f"На {resource_name} нет ни одной записи, занимайте на любое время")
        return
    message = format_notes(resource_name, visitor, records)
    await call.message.answer(text=message)


@router.callback_query(F.data.regexp(r"^resource_name_(\w+)$").as_("match"))
async def describe_stage_handler(call: CallbackQuery, match: Match[str]) -> None:
    await call.answer()
    resource_name = match.group(1)
    resource = await get_resource_by_name(resource_name)
    if resource.comment is None:
        await call.message.answer(f"Про {resource.name} нет никакой дополнительной информации")
        return
    await call.message.answer(f"{resource.name}\r\n\r\n{resource.comment}")


@router.callback_query(F.data.regexp(r"^cancel_take_(\w+)$").as_("match"))
async def describe_stage_handler(call: CallbackQuery, match: Match[str]) -> None:
    await call.answer()
    resource_name = match.group(1)
    await call.message.delete()
    await call.message.answer(f"Вы отменили бронирование ресурса {resource_name}")

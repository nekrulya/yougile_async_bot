from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from pathlib import Path
import re

import app.database.requests as rq

import app.services.yougile_api as yg

import app.keyboards as kb
from app.database.requests import get_user_by_tg_id
from app.services.AttachmentSaver import AttachmentSaver

from bot import bot
from config import SAVE_PATH

router = Router()
attachment_saver = AttachmentSaver(bot)


class TaskAdding(StatesGroup):
    topic = State()
    title = State()
    description = State()
    extras = State()
    editing = State()
    deadline = State()
    image = State()
    document = State()


@router.message(F.text == "📝Добавить задачу")
async def add_task(message: Message, state=FSMContext):
    await state.set_state(TaskAdding.topic)
    await message.answer("Введите тематику задачи:", reply_markup=kb.task_topics)

@router.message(TaskAdding.topic)
async def task_title(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await state.set_state(TaskAdding.title)
    await message.answer("Введите название задачи:")

@router.message(TaskAdding.title)
async def task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(TaskAdding.description)
    if (await state.get_data()).get('topic') == 'Проблемы в проекте':
        await message.answer(
            "Укажите:\n1. Проект\n2. Вид\n3. id элемента\n4. Дополнительное описание (уточнения, ссылки)")
    else:
        await message.answer("Введите описание задачи:")

@router.message(TaskAdding.description)
async def task_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(TaskAdding.extras)
    await message.answer(text="Все готово?", reply_markup=kb.task_adding_tools)

@router.message(F.text == "✏️Редактировать описание", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    current_description = (await state.get_data()).get('description')
    await message.answer(text=f'Вот текущее описание (нужно скопировать и отправить заново):')
    await message.answer(text=f'{current_description}')
    await state.set_state(TaskAdding.editing)

@router.message(TaskAdding.editing)
async def task_editing(message: Message, state: FSMContext):
    new_description = message.text
    await state.update_data(description=new_description)
    await state.set_state(TaskAdding.extras)
    await message.answer('Новое описание принято!', reply_markup=kb.task_adding_tools)

@router.message(F.text == "🕐Добавить дедлайн", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    await message.answer(
        text=f'Выберите дату',
        reply_markup=await SimpleCalendar(locale=await get_user_locale(message.from_user)).start_calendar())
    await state.set_state(TaskAdding.deadline)

@router.callback_query(TaskAdding.deadline, SimpleCalendarCallback.filter())
async def task_deadline(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=False
    )
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Дедлайн установлен: {date.strftime("%d.%m.%Y")}',
                                            reply_markup=kb.task_adding_tools)
        await state.update_data(deadline=date.timestamp() * 1000 + 10 * 60 * 60 * 1000)
        await state.set_state(TaskAdding.extras)

@router.message(F.text == "🖼Прикрепить картинку", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    await state.set_state(TaskAdding.image)
    await message.answer(text="⬇️Отправьте картинку⬇️")

@router.message(F.photo, TaskAdding.image)
async def task_image(message: Message, state: FSMContext):
    image = message.photo[-1]
    file_info = await bot.get_file(image.file_id)
    file_path = file_info.file_path

    # запоминаем пути изображений
    current_data = await state.get_data()
    current_data.setdefault('image_paths', []).append(file_path)
    await state.update_data(current_data)

    await state.set_state(TaskAdding.extras)
    await message.reply(f"Фото сохранено!", reply_markup=kb.task_adding_tools)

@router.message(F.text == "📄Прикрепить документ", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    await state.set_state(TaskAdding.document)
    await message.answer(text="⬇️Отправьте документ⬇️")

@router.message(F.document, TaskAdding.document)
async def task_document(message: Message, state: FSMContext):
    document = message.document
    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path

    # запоминаем пути документов
    current_data = await state.get_data()
    current_data.setdefault('document_paths', []).append(file_path)
    await state.update_data(current_data)

    await state.set_state(TaskAdding.extras)
    await message.reply("Файл сохранен!", reply_markup=kb.task_adding_tools)

@router.message(F.text == "✉️Отправить задачу", TaskAdding.extras)
async def task_extras(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user_by_tg_id(message.from_user.id)
    column_id = await rq.get_column(user.id)

    topic, title, description, deadline, images = (data.get("topic"), data.get('title'),
                                           data.get('description'), data.get('deadline'), data.get('images', []))

    # добавляем тему в начало описания
    description = f"{topic}\n{description}"

    # форматируем ссылки
    link_pattern = r"https?://(?:www\.)?[^\s/$.?#].[^\s]*"
    links = re.findall(link_pattern, description)
    for link in links:
        description = description.replace(link, f'<a href="{link}">{link}</a>')

    # сохраняем изображения
    attachment_folder = await attachment_saver.save(state)
    if attachment_folder:
        description += f"\n{attachment_folder}"

    # подписываем описание ником телеграма
    if message.from_user.username:
        description += f'\n<a href="https://t.me/{message.from_user.username}">@{message.from_user.username}</a>'
    else:
        description += f'\nTelegram: {message.from_user.first_name}'

    try:
        # пытаемся добавить задачу в yougile
        new_task_id = await yg.set_task(title=title,
                                        description=description.replace('\n', '<br>'),
                                        column_id=column_id,
                                        deadline=deadline)
        # запоминаем задачу в бд
        await rq.set_task(user.id, title=title, description=description, task_id=new_task_id)
    except Exception as e:
        await message.answer(text="При отправке задачи произошла ошибка")
    await state.clear()
    await message.answer(text=f'Задача "{title}" отправлена!', reply_markup=kb.main)

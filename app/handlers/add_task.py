from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
import re
import logging

import app.database.requests as rq

import app.services.yougile_api as yg

import app.keyboards as kb
from app.database.requests import get_user_by_tg_id
from app.services.AttachmentSaver import AttachmentSaver

from bot import bot
from config import *

router = Router() # нужен для обработки запросов
attachment_saver = AttachmentSaver(bot) # для сохранения файлов и изображений
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s [%(levelname)s] %(message)s",  # Формат сообщения
)


class TaskAdding(StatesGroup):
    """класс - перечисение состояний пользователя"""
    topic = State() # выбор темы
    title = State() # ввод названия
    description = State() # ввод описания
    extras = State() # дополнительно (дедлайн, файлы)
    editing = State() # редактирование описания
    deadline = State() # установка дедлайна
    image = State() # добавление картинок
    document = State() # добавления докуметов

async def get_user_locale(user):
    """затычка для библиотеки календаря (с оригинальным кодом не работает на windows-server)"""
    return CUSTOM_LOCALE


@router.message(F.text == "📝Добавить задачу")
async def add_task(message: Message, state=FSMContext):
    """Обработка нажатия главной кнопки"""
    await state.set_state(TaskAdding.topic)
    await message.answer("Введите тематику задачи:", reply_markup=kb.task_topics)


@router.message(F.text, TaskAdding.topic)
async def task_title(message: Message, state: FSMContext):
    """Обработка ввода названия задачи"""
    await state.update_data(topic=message.text)
    await state.set_state(TaskAdding.title)
    await message.answer("Введите название задачи:")


@router.message(TaskAdding.topic)
async def task_title(message: Message, state: FSMContext):
    """Проверка, что название задачи указано текстом"""
    await message.answer("Введите название задачи текстом!")


@router.message(F.text, TaskAdding.title)
async def task_title(message: Message, state: FSMContext):
    """Запуск ввода описания"""
    await state.update_data(title=message.text)
    await state.set_state(TaskAdding.description)
    if (await state.get_data()).get('topic') == 'Проблемы в проекте':
        await message.answer(
            "Укажите:\n1. Проект\n2. Вид/Лист\n3. id элемента\n4. Дополнительное описание (уточнения, ссылки)")
    else:
        await message.answer("Введите описание задачи:")


@router.message(TaskAdding.title)
async def task_title(message: Message, state: FSMContext):
    """Обработка ввода названия задачи"""
    await message.answer("Введите название задачи текстом!")


@router.message(F.text, TaskAdding.description)
async def task_description(message: Message, state: FSMContext):
    """Выбор между дополнительными опциями и отправкой задачи"""
    await state.update_data(description=message.text)
    await state.set_state(TaskAdding.extras)
    await message.answer(text="Все готово?", reply_markup=kb.task_adding_tools)


@router.message(TaskAdding.description)
async def task_description(message: Message, state: FSMContext):
    """Обработка ввода описания задачи"""
    await message.answer(text="Введите описание текстом!")


@router.message(F.text == "✏️Редактировать описание", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    """редактирование описания задачи"""
    current_description = (await state.get_data()).get('description')
    await message.answer(text=f'Вот текущее описание (нужно скопировать и отправить заново):')
    await message.answer(text=f'{current_description}')
    await state.set_state(TaskAdding.editing)


@router.message(F.text, TaskAdding.editing)
async def task_editing(message: Message, state: FSMContext):
    """Получение нового описания"""
    new_description = message.text
    await state.update_data(description=new_description)
    await state.set_state(TaskAdding.extras)
    await message.answer('Новое описание принято!', reply_markup=kb.task_adding_tools)


@router.message(TaskAdding.editing)
async def task_editing(message: Message, state: FSMContext):
    """Проверка ввода нового описания"""
    await message.answer('Введите описание текстом!')


@router.message(F.text == "🕐Добавить дедлайн", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    """Отправка календаря для выбора дедлайна"""
    await message.answer(
        text=f'Выберите дату',
        reply_markup=await SimpleCalendar(locale=await get_user_locale(message.from_user)).start_calendar())
    await state.set_state(TaskAdding.deadline)


@router.callback_query(TaskAdding.deadline, SimpleCalendarCallback.filter())
async def task_deadline(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    """Обработка нажатий на дату в календаре """
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=False
    )
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Дедлайн установлен: {date.strftime("%d.%m.%Y")}',
                                            reply_markup=kb.task_adding_tools)
        await state.update_data(deadline=date.timestamp() * 1000 + 10 * 60 * 60 * 1000)
        await state.set_state(TaskAdding.extras)


@router.message(TaskAdding.deadline)
async def task_deadline(message: Message, state: FSMContext):
    """Проверка ввода дедлайна"""
    await message.answer(
        text=f'Нажимайте кнопочки!',
        reply_markup=await SimpleCalendar(locale=await get_user_locale(message.from_user)).start_calendar())


@router.message(F.text == "🖼Прикрепить картинку", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    """Запуск прикрепления картинок"""
    await state.set_state(TaskAdding.image)
    await message.answer(text="⬇️Отправьте картинку⬇️")


@router.message(F.photo, TaskAdding.image)
async def task_image(message: Message, state: FSMContext):
    """Добавление картинок"""
    image = message.photo[-1] # картинка в лучшем качестве
    file_info = await bot.get_file(image.file_id) # информация о картинке
    file_path = file_info.file_path # путь к картинке

    # запоминаем пути изображений
    current_data = await state.get_data()
    current_data.setdefault('image_paths', []).append(file_path)
    await state.update_data(current_data)

    await state.set_state(TaskAdding.extras)
    await message.reply(f"Фото сохранено!", reply_markup=kb.task_adding_tools)


@router.message(TaskAdding.image)
async def task_image(message: Message, state: FSMContext):
    # проверка добавления картинок
    await message.reply(f"Отправьте изображение!", reply_markup=kb.task_adding_tools)


@router.message(F.text == "📄Прикрепить документ", TaskAdding.extras)
async def task_edit(message: Message, state: FSMContext):
    """Прикрепление документа"""
    await state.set_state(TaskAdding.document)
    await message.answer(text="⬇️Отправьте документ⬇️")


@router.message(F.document, TaskAdding.document)
async def task_document(message: Message, state: FSMContext):
    document = message.document
    file_info = await bot.get_file(document.file_id)
    file_name = document.file_name
    file_path = file_info.file_path

    # запоминаем пути документов
    current_data = await state.get_data()
    current_data.setdefault('document_paths', []).append((file_path, file_name))
    await state.update_data(current_data)

    await state.set_state(TaskAdding.extras)
    await message.reply("Файл сохранен!", reply_markup=kb.task_adding_tools)


@router.message(TaskAdding.document)
async def task_document(message: Message, state: FSMContext):
    """Проверка названия документа"""
    await message.reply("Отправьте файл!", reply_markup=kb.task_adding_tools)


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
    elif message.from_user.first_name and message.from_user.last_name:
        description += f'\nTelegram: {message.from_user.first_name} {message.from_user.last_name}'
    elif message.from_user.first_name:
        description += f'\nTelegram: {message.from_user.first_name}'
    else:
        description += f'\nTelegram: anonim'

    try:
        # пытаемся добавить задачу в yougile
        new_task_id = await yg.set_task(title=title,
                                        description=description.replace('\n', '<br>'),
                                        column_id=column_id,
                                        deadline=deadline)
        # запоминаем задачу в бд
        await rq.set_task(user.id, title=title, description=description, task_id=new_task_id)

        logging.info(f"Добавлена задача: {user.id=}, {title=}, {description=}")



        await state.clear()
        await message.answer(text=f'Задача "{title}" отправлена!', reply_markup=kb.main)

    except Exception as e:
        await message.answer(text="При отправке задачи произошла ошибка")
        logging.warning(f"Ошибка при добавлении задача: {user.id=}, {title=}, {description=}\n{e=}")

    try:
        # отправка уведомления о добавлении задачи
        for admin_id in ADMIN_TELEGRAM_IDS:
            if admin_id:
                if message.from_user.username:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=f"Новая задача от {message.from_user.username}\nТема: {topic}\nНазвание: {title}")
                else:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=f"Новая задача от {message.from_user.first_name}\nТема: {topic}\nНазвание: {title}")
    except Exception as e:
        logging.warning(f"Произошла ошибка при отправке уведомления {e=}")


@router.message()
async def add_task(message: Message, state=FSMContext):
    await message.answer("Неизвестное сообщение!", reply_markup=kb.main)
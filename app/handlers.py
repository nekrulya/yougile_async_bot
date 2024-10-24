import json

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
import re

import app.database.requests as rq

import app.services.yougile_api as yg

import app.keyboards as kb
from app.database.requests import get_user_by_tg_id

router = Router()

class TaskAdding(StatesGroup):
    title = State()
    description = State()
    extras = State()
    editing = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(f"hello {message.from_user.first_name}", reply_markup=kb.main)

@router.message(F.text == "📝Добавить задачу")
async def add_task(message: Message, state=FSMContext):
    await state.set_state(TaskAdding.title)
    await message.answer("Введите название задачи:")

@router.message(TaskAdding.title)
async def task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(TaskAdding.description)
    await message.answer("Введите описание задачи")

@router.message(TaskAdding.description)
async def task_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(TaskAdding.extras)
    await message.answer(text="Все готово?", reply_markup=kb.task_adding_tools)

@router.message(F.text == "✏️Отредактировать", TaskAdding.extras)
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

@router.message(F.text == "✉️Отправить задачу", TaskAdding.extras)
async def task_extras(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user_by_tg_id(message.from_user.id)
    column_id = await rq.get_column(user.id)

    title, description = data['title'], data['description']
    link_pattern = r"https?://(?:www\.)?[^\s/$.?#].[^\s]*"
    links = re.findall(link_pattern, description)
    for link in links:
        description = description.replace(link, f'<a href="{link}">{link}</a>')

    new_task_id = await yg.set_task(title=title, description=description.replace('\n', '<br>'), column_id=column_id)
    await rq.set_task(user.id, title=title, description=description, task_id=new_task_id)
    await state.clear()
    await message.answer(text=f'Задача "{title}" отправлена!', reply_markup=kb.main)


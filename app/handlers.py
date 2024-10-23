from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup

import app.database.requests as rq

import app.services.yougile_api as yg

import app.keyboards as kb
from app.database.requests import get_user_by_tg_id

router = Router()

class TaskAdding(StatesGroup):
    title = State()
    description = State()

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
    data = await state.get_data()

    user = await get_user_by_tg_id(message.from_user.id)
    title, description = data['title'], data['description']
    column_id = await rq.get_column(user.id)

    new_task_id = await yg.set_task(title=title, description=description, column_id=column_id)
    await rq.set_task(user.id, title=title, description=description, task_id=new_task_id)
    await state.clear()


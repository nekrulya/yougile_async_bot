from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup

import app.database.requests as rq

import app.keyboards as kb

router = Router()

class TaskAdding(StatesGroup):
    topic = State()
    title = State()
    description = State()
    extras = State()
    editing = State()
    deadline = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(f"hello {message.from_user.first_name}", reply_markup=kb.main)



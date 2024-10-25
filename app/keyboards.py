from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝Добавить задачу")]
], resize_keyboard=True, one_time_keyboard=True)

task_topics = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Разработка семейств ")],
    [KeyboardButton(text="Проблемы в проекте")],
    [KeyboardButton(text="Другое")]
], resize_keyboard=True, one_time_keyboard=True)

task_adding_tools = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✏️Отредактировать описание"), KeyboardButton(text="🕐Добавить дедлайн")],
    [KeyboardButton(text="🖼Прикрепить картинку"), KeyboardButton(text="📄Прикрепить документ")],
    [KeyboardButton(text="✉️Отправить задачу")],
], resize_keyboard=True, one_time_keyboard=True)

async def task_list(tasks: list):
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text=task.name, callback_data=task.id))

    return keyboard.as_markup()
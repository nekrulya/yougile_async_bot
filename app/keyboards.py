from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝Добавить задачу"), KeyboardButton(text="📋Посмотреть активные")],
    [KeyboardButton(text="✅Отметить выполненной"), KeyboardButton(text="✍️Редактировать")]
], resize_keyboard=True, one_time_keyboard=True)
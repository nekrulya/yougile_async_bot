from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝Добавить задачу"), KeyboardButton(text="📋Посмотреть активные")],
    [KeyboardButton(text="✅Отметить выполненной"), KeyboardButton(text="✍️Редактировать")]
], resize_keyboard=True, one_time_keyboard=True)

task_topics = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Разработка семейств "), KeyboardButton(text="Проблемы в проекте")],
], resize_keyboard=True, one_time_keyboard=True)

task_adding_tools = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✏️Отредактировать описание"), KeyboardButton(text="🕐Добавить дедлайн")],
    [KeyboardButton(text="✉️Отправить задачу")],
], resize_keyboard=True, one_time_keyboard=True)
import asyncio
from aiogram import Bot, Dispatcher

from app.handlers.main_handlers import router as main_router
from app.handlers.add_task import router as task_router

from app.database.models import async_main
from bot import bot

async def main():
    await async_main() # создание баз данных
    dp = Dispatcher() # диспетчер для обработки "путей" запросов
    dp.include_router(main_router) # роутер команды /start
    dp.include_router(task_router) # роутер добавления команды
    await dp.start_polling(bot) # запуск бесконечной работы бота

if __name__ == '__main__':
    print('Bot is running')
    try:
        asyncio.run(main()) # запуск асинхронного loop'а
    except KeyboardInterrupt:
        print('Exit')
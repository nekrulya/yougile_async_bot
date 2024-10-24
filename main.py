import asyncio
from aiogram import Bot, Dispatcher

from app.handlers.main_handlers import router as main_router
from app.handlers.add_task import router as task_router

from app.database.models import async_main
from bot import bot

async def main():
    await async_main()
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.include_router(task_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Bot is running')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
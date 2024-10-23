from app.database.models import async_session
from app.database.models import User, Location, Task
from sqlalchemy import select

from config import DEFAULT_COMPANY, DEFAULT_PROJECT, DEFAULT_BOARD, DEFAULT_COLUMN

async def set_location(user_id: int, company: str, project: str, board: str, column: str) -> None:
    async with async_session() as session:
        session.add(Location(user_id=user_id, company=company, project=project, board=board, column=column))

async def get_user_by_tg_id(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user

async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await get_user_by_tg_id(tg_id)
        if not user:
            session.add(User(tg_id=tg_id))
            new_user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            default_location = Location(
                user_id=new_user_id,
                company=DEFAULT_COMPANY,
                project=DEFAULT_PROJECT,
                board=DEFAULT_BOARD,
                column=DEFAULT_COLUMN
            )
            session.add(default_location)
            await session.commit()

async def set_task(user_id: int, title: str, description: str, task_id: str) -> None:
    async with async_session() as session:
        new_task = Task(title=title, description=description, user_id=user_id, yougile_task_id=task_id)
        session.add(new_task)
        await session.commit()


async def get_column(user_id: int) -> str:
    async with async_session() as session:
        column = await session.scalar(select(Location.column).where(Location.user_id == user_id))
        return column
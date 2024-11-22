from sqlalchemy import Column, BigInteger, String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3') # асинхронное подключение к sqlite

async_session = async_sessionmaker(engine) # создаем фабрику сессий

class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для асинхронного ORM подхода
    """
    pass

class User(Base):
    """
    Пользователь для связки внутреннго id с телеграм-id
    """
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

class Location(Base):
    """
    "Локация" - к какой доске привязан пользователь
    """
    __tablename__ = 'locations'
    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(255)) # yougile uuid
    project: Mapped[str] = mapped_column(String(255)) # yougile uuid
    board: Mapped[str] = mapped_column(String(255)) # yougile uuid
    column: Mapped[str] = mapped_column(String(255)) # yougile uuid
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id')) # внутренний id пользователя

class Task(Base):
    """
    Одна конкретная задача
    """
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255)) # мелнькое название
    description: Mapped[str] = mapped_column(Text()) # большое описание
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id')) # id создателя
    yougile_task_id: Mapped[str] = mapped_column(String(255)) # yougile uuid, получается при добавлении задачи


async def async_main():
    """Создание таблиц в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


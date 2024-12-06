import os
from datetime import date


os.environ['ENVIRONMENT'] = 'test'
from typing import AsyncGenerator

import pytest
from config.database import Base, get_db
from httpx import ASGITransport, AsyncClient
from main import app
from models import Place, SocialAccount, User
from settings import get_settings
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


settings = get_settings()

engine_test = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)

async_session_maker = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, future=True
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session"""
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_async_session


@pytest.fixture(autouse=True, scope='function')
async def init_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        yield client


@pytest.fixture(scope='session')
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope='function')
async def mock_user(async_session: AsyncSession):
    test_user = User(
        full_name='Borya',
        email='borya@mail.com',
        profile_picture=None,
    )
    async_session.add(test_user)
    await async_session.commit()
    await async_session.refresh(test_user)
    return test_user


@pytest.fixture(scope='function')
async def mock_social_account(async_session: AsyncSession, mock_user: User):
    social_account = SocialAccount(
        service='google',
        social_account_id='123456789',
        access_token='my token',
        refresh_token='my',
        user_id=mock_user.id,
    )
    async_session.add(social_account)
    await async_session.commit()
    await async_session.refresh(social_account)
    return social_account


@pytest.fixture(scope='function')
async def mock_place(async_session: AsyncSession, mock_user: User):
    test_place = Place(
        place_name='Test place',
        city='Kyiv',
        country='Ukraine',
        description='my favorite place',
        photo_url='kyiv.ua',
        rating=5,
        days_spent=5,
        visit_date=date(2024, 1, 28),
        place_type='visited',
        user_id=mock_user.id,
    )
    async_session.add(test_place)
    await async_session.commit()
    await async_session.refresh(test_place)
    return test_place

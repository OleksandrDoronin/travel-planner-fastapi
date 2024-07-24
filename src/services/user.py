from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.db_session = db
        self.user_repository = UserRepository(db)

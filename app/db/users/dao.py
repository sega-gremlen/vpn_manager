from sqlalchemy import select
from app.db.users.models import Users
from app.db.creator import async_sessionmaker

from app.db.dao.base import BaseDAO


class UsersDAO(BaseDAO):
    model = Users





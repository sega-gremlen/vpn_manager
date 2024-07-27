from app.db.subscribe_types.models import SubscriptionTypes
from app.db.dao.base import BaseDAO


class SubscriptionTypesDAO(BaseDAO):
    model = SubscriptionTypes

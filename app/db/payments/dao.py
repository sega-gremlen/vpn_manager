from app.db.payments.models import Payments
from app.db.dao.base import BaseDAO


class PaymentsDAO(BaseDAO):
    model = Payments

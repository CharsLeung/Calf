from datetime import datetime

from .base_model import KlineBase


class Month(KlineBase):
    __tablename__ = 'month'

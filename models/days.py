# -*- coding: utf-8 -*-

# from .base_model import BaseModel, columns



# class Day(BaseModel):
#     # __table_name__ = 'days'
#     # stock_code = columns.Integer(indicators=True)
#     # market = columns.TinyInt()
#     # date = columns.Integer(indicators=True)
#     # open = columns.Decimal()
#     # close = columns.Decimal()
#     # high = columns.Decimal()
#     # low = columns.Decimal()
#     # volume = columns.BigInt()
#     # amount = columns.BigInt()
#     # __tablename__ = 'day'
#     __fields__ = BaseModel.__fields__ + [
#         ('stock_code', int, -1),
#         ('market', int, -1),
#         ('date', int, -1),
#         ('open', float, -1),
#         ('close', float, -1),
#         ('high', float, -1),
#         ('low', float, -1),
#         ('volume', int, -1),
#         ('amount', int, -1),
#     ]
from model_data_get.models.kline import KlineBase


class HKDay(KlineBase):
    __tablename__ = 'hk_kline_day'


class Day(KlineBase):
    __tablename__ = 'kline_day'


class XDXRDay(KlineBase):
    __tablename__ = 'XDXR_day'

    # @classmethod
    # def insert_batch(cls, *args):
    #     _ = list()
    #     if len(args) == 1:
    #         _ = args[0]
    #     elif len(args) > 1:
    #         _ = args
    #     __ = list()
    #     for i in _:
    #         if cls.query(stock_code=i['stock_code']).count() != len(_):
    #             BaseModel.upsert_batch(__)

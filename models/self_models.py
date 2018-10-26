# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2017/12/4 8:50
"""

from datetime import datetime

from ..models.base_model import BaseModel


class DvgPoints(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('date', datetime, -1),
        ('time', int, -1),
        ('c_mark', bool, True),
        ('dvg_flag', bool, False),
        ('last_max_area', float, -1.0),
        ('last_max_macd', float, -1.0),
        ('max_area', float, -1.0),
        ('max_macd', float, -1.0),
        ('dist', int, -1),
        ('open', float, -1.0),
        ('close', float, -1.0),
        ('sell_date', datetime, -1),
        ('sell_price', float, -1.0),
        ('class', str, ''),
    ]


class Dvg(DvgPoints):
    # __tablename__ = 'dvgs'
    pass


class PositionsList(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('c_mark', bool, False),
        ('buy_date', datetime, -1),
        ('sell_date', datetime, -1),
        ('buy_price', float, 0),
        ('sell_price', float, 0),
        ('profit', float, 0),
        ('model_from', str, ''),
        ('reason', int, 0),
        ('version', str, ''),
    ]


class SellList(PositionsList):
    # __tablename__ = 'positionslist'
    pass


class Signal(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('date', datetime, -1),
        ('time', int, 0),
        ('buy_price', float, -1.0),
        ('dist', int, 0),
        ('confidence', float, -1.0),
        ('version', int, 0),
        ('model_from', str, ''),
    ]


class signal(Signal):
    # __tablename__ = 'signals'
    pass


class TransactionRecord(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('date', datetime, -1),
        ('profit', float, 0.0),
        ('version', int, 0),
        ('model_from', str, ''),
        ('note', str, '')
    ]


class TradeMenu(TransactionRecord):
    # __tablename__ = 'trademenu'
    pass


class FinanceIndex(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('date', datetime, -1),
        ('spr', float, 0.0),
        ('cpr', float, 0.0),
        ('win_rate', float, 0.0),
        ('trade_counts', int, 0),
        ('max_dd', float, 0.0),
        ('sharp', float, 0.0),
        ('avg_signals', float, 0.0),
        ('avg_day_get', float, 0.0),
        ('alpha', float, 0.0),
        ('beta', float, 0.0),
        ('version', int, 0),
        ('model_from', str, ''),
        ('note', str, '')
    ]


class ModelFinanceIndex(FinanceIndex):
    # __tablename__ = 'financeindex'
    pass


class naughty(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('date', datetime, -1),
        ('time', int, -1),
        ('c_mark', bool, True),
        ('open', float, -1.0),
        ('close', float, -1.0),
        ('amount', float, 0),
        ('volume', float, 0),
        ('sell_date', datetime, -1),
        ('sell_price', float, -1.0),
        ('lv_delta', float, 0),
        ('nv_delta', float, 0),
        ('version', int, 0),
        ('class', str, ''),
    ]


class Naughtiers(naughty):
    # __tablename__ = 'naughtiers'
    pass

# -*- coding: utf-8 -*-
from datetime import datetime

from .base_model import BaseModel, KlineBase


class OneMinute(BaseModel):
    # __table_name__ = 'min_1'
    # stock_code = columns.Integer(indicators=True)
    # date = columns.Integer(indicators=True)
    # time = columns.Integer(indicators=True)
    # market = columns.TinyInt()
    # price = columns.Decimal()
    # volume = columns.BigInt()
    # amount = columns.BigInt()
    # change = columns.Decimal()
    # change_p = columns.Decimal()
    __tablename__ = 'min_1'
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('market', int, -1),
        ('date', datetime, -1),
        ('time', datetime, -1),
        ('price', float, -1),
        ('change', float, -1),
        ('change_p', float, -1),
        ('volume', int, -1),
        ('amount', int, -1),
    ]

    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = int(source_data.get('stock_code', -1))
        _['market'] = source_data.get('market', -1)
        _['date'] = int(source_data.get('date', -1))
        _['time'] = int(source_data.get('time', -1))
        _['price'] = float(source_data.get('price', -1))
        _['change_p'] = float(source_data.get('change_p', -1))
        _['change'] = float(source_data.get('change', -1))
        _['volume'] = int(source_data.get('volume', -1))
        _['amount'] = int(float(source_data.get('amount', -1)))
        return _


class MinuteBase(KlineBase):
    __fields__ = KlineBase.__fields__ + [
        ('time', int, -1)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = KlineBase.trans_data(source_data)
        dt = source_data.get('date').split(' ')
        hour, minute = dt[1].split(':')
        _['time'] = int(hour + minute)
        return _


class FiveMinutes(MinuteBase):
    __tablename__ = 'kline_min5'


class FifteenMinutes(MinuteBase):
    __tablename__ = 'kline_min15'


class ThirtyMinutes(MinuteBase):
    __tablename__ = 'kline_min30'


class OneHour(MinuteBase):
    __tablename__ = 'kline_min60'

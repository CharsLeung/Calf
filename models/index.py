# -*- coding: utf-8 -*-

from datetime import datetime

from .base_model import BaseModel


class IndexBase(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('market', int),
        ('date', datetime),
        ('open', float),
        ('close', float),
        ('high', float),
        ('low', float),
        ('volume', int),
        ('amount', int),
        ('up', int),
        ('down', int)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = source_data.get('stock_code', 'xxxxxx')
        _['market'] = source_data.get('market', 'unknow')
        d = source_data.get('date')
        _['date'] = datetime(year=int(d[:4]), month=int(d[4:6]), day=int(d[6:]))
        _['open'] = float(source_data.get('open', -1))
        _['close'] = float(source_data.get('close', -1))
        _['high'] = float(source_data.get('high', -1))
        _['low'] = float(source_data.get('low', -1))
        _['volume'] = int(source_data.get('volume', -1))
        _['amount'] = int(float(source_data.get('amount', -1)))
        _['up'] = int(source_data.get('up', -1))
        _['down'] = int(source_data.get('down', -1))
        return _


class DayIndex(IndexBase):
    pass


class WeekIndex(IndexBase):
    pass


class MonthIndex(IndexBase):
    pass


class MintueIndex(IndexBase):
    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = int(source_data.get('stock_code', -1))
        _['market'] = source_data.get('market', -1)
        dt = source_data.get('date').split(' ')
        year, month, day = dt[0].split('-')
        _['date'] = datetime(year=int(year), month=int(month), day=int(day))
        hour, minute = dt[1].split(':')
        _['time'] = int(hour + minute)
        _['open'] = float(source_data.get('open', -1))
        _['close'] = float(source_data.get('close', -1))
        _['high'] = float(source_data.get('high', -1))
        _['low'] = float(source_data.get('low', -1))
        _['volume'] = int(source_data.get('volume', -1))
        _['amount'] = int(float(source_data.get('amount', -1)))
        _['up'] = int(source_data.get('up', -1))
        _['down'] = int(source_data.get('down', -1))
        return _

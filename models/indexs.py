# -*- coding: utf-8 -*-
from datetime import datetime

from model_data_get.models.base_model import BaseModel


class IndexBase(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('market', int, -1),
        ('date', datetime, datetime.today()),
        ('open', float, -1),
        ('close', float, -1),
        ('high', float, -1),
        ('low', float, -1),
        ('volume', int, -1),
        ('amount', int, -1),
        ('up', int, -1),
        ('down', int, -1)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = int(source_data.get('stock_code', -1))
        _['market'] = source_data.get('market', -1)
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


class IndexDay(IndexBase):
    __tablename__ = 'index_day'


class Index30Minutes(IndexBase):
    __tablename__ = 'index_min30'

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


class Index60Minutes(IndexBase):
    __tablename__ = 'index_min60'

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


class IndexMonth(IndexBase):
    __tablename__ = 'index_month'


class IndexWeek(IndexBase):
    __tablename__ = 'index_week'


class Index5Minutes(IndexBase):
    __tablename__ = 'index_min5'

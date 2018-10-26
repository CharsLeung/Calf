# -*- coding: utf-8 -*-
import re
from datetime import datetime

from .base_model import BaseModel


class KlineBase(BaseModel):
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
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = source_data.get('stock_code', 'xxxxxx')
        _['market'] = source_data.get('market', 'unknow')
        dt = source_data.get('date').split(' ')
        r = re.search('(^\d{4})[./-]*(\d{1,2})[./-]*(\d{1,2}$)', dt[0])
        year, month, day = r.groups()
        _['date'] = datetime(year=int(year), month=int(month), day=int(day))
        _['open'] = float(source_data.get('open', -1))
        _['close'] = float(source_data.get('close', -1))
        _['high'] = float(source_data.get('high', -1))
        _['low'] = float(source_data.get('low', -1))
        _['volume'] = int(source_data.get('volume', -1))
        _['amount'] = int(float(source_data.get('amount', -1)))
        return _


class Day(KlineBase):
    pass


class Week(KlineBase):
    pass


class Month(KlineBase):
    pass


class Minute(KlineBase):
    __fields__ = KlineBase.__fields__ + [
        ('time', int)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = KlineBase.trans_data(source_data)
        dt = source_data.get('date').split(' ')
        hour, minute = dt[1].split(':')
        _['time'] = int(hour + minute)
        return _

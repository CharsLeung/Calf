# -*- coding: utf-8 -*-
from datetime import datetime

from .base_model import BaseModel
from .kline import Day, Minute


class XDXR(BaseModel):
    __tablename__ = 'XDXR'
    __fields__ = [
        ('stock_code', str),
        ('market', int),
        ('date', datetime),
        ('save', int),
        ('cache', float),
        ('stock_p', float),
        ('stock_v', float),
        ('percent', float)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = source_data.get('stock_code', 'xxxxxx')
        _['market'] = source_data.get('market', 'unknow')
        dt = source_data.get('date').split(' ')
        import re
        r = re.search('(^\d{4})[./-]*(\d{1,2})[./-]*(\d{1,2}$)', dt[0])
        year, month, day = r.groups()
        _['date'] = datetime(year=int(year), month=int(month), day=int(day))
        _['save'] = int(source_data.get('save', -1))
        _['cache'] = float(source_data.get('cache', -1))
        _['stock_p'] = float(source_data.get('stock_p', -1))
        _['stock_v'] = float(source_data.get('stock_v', -1))
        _['percent'] = float(source_data.get('percent', -1))
        return _


class XDXROffset(BaseModel):
    __tablename__ = 'XDXR_offset'
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('market', int),
        ('date', datetime),
        ('offset', float)
    ]


class DayXDXR(Day):
    pass


class MinuteXDXR(Minute):
    pass

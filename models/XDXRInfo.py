# -*- coding: utf-8 -*-
from datetime import datetime

from .base_model import BaseModel, KlineBase


class XDXR(BaseModel):
    __tablename__ = 'XDXR'
    __fields__ = [
        ('stock_code', str, ''),
        ('market', int, -1),
        ('date', datetime, -1),
        ('save', int, -1),
        ('cache', float, -1),
        ('stock_p', float, -1),
        ('stock_v', float, -1),
        ('percent', float, -1)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = int(source_data.get('stock_code', -1))
        _['market'] = int(source_data.get('market', -1))
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


class XDXRDay(KlineBase):
    __tablename__ = 'XDXR_day'


class XDXR30min(KlineBase):
    __tablename__ = 'XDXR_min_30'

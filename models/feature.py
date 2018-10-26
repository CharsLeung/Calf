# -*- coding: utf-8 -*-
from datetime import datetime

from .base_model import BaseModel


class Tushare(BaseModel):
    pass


class Capital(BaseModel):
    pass


class DayFeature(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('market', int),
        ('date', datetime),
        ('ma5', float),
        ('ma10', float),
        ('ma20', float),
        ('ma30', float),
        ('ma60', float),
        ('v_ma5', float),
        ('v_ma10', float),
        ('v_ma20', float),
        ('v_ma30', float),
        ('v_ma60', float),
        ('close_z', float),
        ('change_r', float),
        ('volume_r', float),
        ('last_volume', float),
        ('v_dt_ma60', float),
        ('capital', float),
        ('roe', float),
    ]

    @classmethod
    def trans_data(cls, source):
        _ = dict()
        _['date'] = source['date']
        _['stock_code'] = source['stock_code']
        return _


class IndexFeature(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('market', int),
        ('date', datetime),
        ('up_03', int),
        ('up_35', int),
        ('up_57', int),
        ('up_79', int),
        ('up_95', int),
        ('down_03', int),
        ('down_35', int),
        ('down_57', int),
        ('down_79', int),
        ('down_95', int),
    ]


class IndexMA(DayFeature):
    pass

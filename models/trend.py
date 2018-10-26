# -*- coding: utf-8 -*-
from datetime import datetime

from lunardate import LunarDate

# from app.models import *
# from app.models.base_model import Base
from model_data_get.models import Calendar
from .base_model import BaseModel


class TrendBase(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int),
        ('buy_date', datetime),
        ('sell_date', datetime),
        ('profit', bool),
        ('price', float),
        ('category', str)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        # stock_code 处的 int() 动作非常重要
        # 因为经过 numpy 或者 pandas 等库处理后的数据，其类型可能被转换为 int64 等特殊类型
        # mongodb 无法处理基本类型之外的自定义类型
        _['stock_code'] = int(source_data.get('stock_code'))
        _['buy_date'] = source_data.get('buy_date')
        _['sell_date'] = source_data.get('sell_date')
        _['profit'] = source_data.get('profit', True)
        _['price'] = source_data.get('price')
        _['category'] = source_data.get('category')
        return _


class Trend3Day(TrendBase):
    __tablename__ = 'trend_3day'


class Rebound(TrendBase):
    __tablename__ = 'trend_rebound'


class SolarTerm(TrendBase):
    __tablename__ = 'trend_solar_terms'
    __fields__ = TrendBase.__fields__ + [
        ('name', str),
        ('buy_tradate', str),
        ('sell_tradate', str),
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = TrendBase.trans_data(source_data)
        _['name'] = SolarCalendar.recent(_['buy_date'])['name']
        bd = LunarDate.fromSolarDate(_['buy_date'].year, _['buy_date'].month, _['buy_date'].day)
        sd = LunarDate.fromSolarDate(_['buy_date'].year, _['buy_date'].month, _['buy_date'].day)
        _['buy_tradate'] = '{}-{:02d}-{:02d}'.format(bd.year, bd.month, bd.day)
        _['sell_tradate'] = '{}-{:02d}-{:02d}'.format(sd.year, sd.month, sd.day)
        return _


class BaGua(BaseModel):
    __tablename__ = 'bagua'
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int),
        ('date', datetime),
        ('bin', str),
        ('category', str)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = source_data.get('stock_code')
        _['date'] = Calendar.to(datetime, source_data.get('date'))
        _['bin'] = source_data.get('bin')
        _['category'] = source_data.get('category')
        return _


class BaGuaTerm(TrendBase):
    __tablename__ = 'trend_bagua_terms'
    __fields__ = TrendBase.__fields__ + [
        ('bin', str)
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = TrendBase.trans_data(source_data)
        _['bin'] = source_data.get('bin')
        return _

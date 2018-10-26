# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2017/12/29 11:58
"""
import datetime

from Calf.models.base_model import BaseModel


class Order(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('c_mark', bool, False),
        ('date', datetime, -1),
        ('time', int, 0),
        ('buy_price', float, -1.0),
        ('stop_loss', float, 0),
        ('stop_get', float, 0),
        ('fee', float, 0),
        ('max_pst_date', datetime, -1),
        ('Rr', float, 0),
        ('confidence', float, -1.0),
        ('version', int, 0),
        ('model_from', str, ''),
    ]


class Orders(Order):
    # __tablename__ = 'orders'
    pass


class OrderHis(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('c_mark', bool, False),
        ('buy_date', datetime, -1),
        ('time', int, 0),
        ('buy_price', float, -1.0),
        ('stop_loss', float, 0),
        ('stop_get', float, 0),
        ('fee', float, 0),
        ('sell_date', datetime, -1),
        ('Rr', float, 0),
        ('profit', float, -1.0),
        ('reason', int, 0),
        ('model_from', str, ''),
    ]


class OrdersHis(OrderHis):
    pass


class RmdHis(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('client_no', str, ''),
        ('stock_code', int, -1),
        ('c_mark', bool, False),
        ('buy_date', datetime, -1),
        ('time', int, 0),
        ('buy_price', float, -1.0),
        ('stop_loss', float, 0),
        ('stop_get', float, 0),
        ('fee', float, 0),
        ('sell_date', datetime, -1),
        ('Rr', float, 0),
        ('buy', float, 0),
        ('profit', float, -1.0),
        ('reason', int, 0),
        ('model_from', str, ''),
    ]


class RmdsHis(RmdHis):
    pass
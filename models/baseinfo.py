# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/1/31 11:11
"""
import datetime

from Calf.data import BaseModel


class rrads(BaseModel):
    """定期报告预约披露时间表,目前主要应用于股票市场"""
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('name', str, ''),
        ('reservation', datetime, -1),
        ('reservation1', datetime, -1),
        ('reservation2', datetime, -1),
        ('reservation3', datetime, -1),
        ('publish', datetime, -1),
        ('class', str, ''),
    ]
    pass
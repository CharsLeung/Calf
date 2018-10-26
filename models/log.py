# -*- coding: utf-8 -*-
from datetime import datetime

from .base_model import BaseModel
from .calendar import Calendar


class LogBase(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('time', int, -1),
        ('date', datetime, -1),
        ('func', str, 'none'),
        ('message', str, '')
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        now = datetime.now()
        _['time'] = source_data.get('date', int('{}{:02d}{:02d}'.format(now.hour, now.minute, now.second)))
        _['date'] = source_data.get('date', Calendar.today())
        _['func'] = source_data.get('func')
        _['message'] = source_data.get('message')
        return _

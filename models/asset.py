# -*- coding: utf-8 -*-
import copy
from datetime import datetime

from .base_model import BaseModel
from .calendar import Calendar


class Asset(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('client_no', str, ''),
        ('total', float, 0.0),
        ('model_from', str, ''),
        ('model_ratio', float, 0.0),
        ('date', datetime, None)
    ]

    @classmethod
    def trans_data(cls, source_data, model_from):
        sl = list()
        source_data['date'] = source_data.get('date', Calendar.today())
        for m in model_from:
            s = copy.deepcopy(source_data)
            s['model_from'] = m
            s['model_ratio'] = 0.5
            sl.append(s)
        return sl


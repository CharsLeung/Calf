# -*- coding: utf-8 -*-

from .calendar import Calendar
from .feature import DayFeature, IndexFeature, Tushare, Capital, IndexMA
from .fundamentals import ZYBK_TTM, ZJH_TTM, ZZ_TTM
from .index import DayIndex, MintueIndex, WeekIndex, MonthIndex
from .kline import Day, Minute, Week, Month
from .xdxr import XDXROffset, DayXDXR, MinuteXDXR, XDXR
from .self_models import Dvg, SellList, signal


class LazyProperty(object):
    def __init__(self, method):
        self.method = method
        self.method_name = method.__name__
        print('function overriden: {}'.format(self.method))
        print("function's name: {}".format(self.method_name))

    def __get__(self, obj, cls):
        if not obj:
            return None
        value = self.method(obj)
        print('value {}'.format(value))
        setattr(obj, self.method_name, value)
        return value

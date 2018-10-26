# -*- coding: utf-8 -*-
from .days import Day
from .minutes import OneHour, FiveMinutes, FifteenMinutes, ThirtyMinutes


class DayRealtime(Day):
    __tablename__ = 'rt_day'


class OneHourRealtime(OneHour):
    __tablename__ = 'rt_hour_1'


class FiveMinutesRealtime(FiveMinutes):
    __tablename__ = 'rt_min_5'


class FifteenMinutesRealtime(FifteenMinutes):
    __tablename__ = 'rt_min_15'


class ThirtyMinutesRealtime(ThirtyMinutes):
    __tablename__ = 'rt_min_30'

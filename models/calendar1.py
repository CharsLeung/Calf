# -*- coding: utf-8 -*-
import re
from datetime import timedelta, datetime, date

from pandas._libs.tslib import Timestamp

from .base_model import BaseModel


class Calendar(BaseModel):
    # __table_name__ = 'trade_calendar'
    # date = columns.Integer(indicators=True)
    # num = columns.Integer(indicators=True)
    __tablename__ = 'calendar'
    __fields__ = BaseModel.__fields__ + [
        ('date', datetime),
        ('num', int)
    ]

    @classmethod
    def today(cls, pure=True):
        t = date.today()
        if pure:
            t = datetime(year=t.year, month=t.month, day=t.day)
        return t

    @classmethod
    def in_business(cls, dt, hard=True):
        ms = datetime(year=dt.year, month=dt.month, day=dt.day, hour=9, minute=35)
        me = datetime(year=dt.year, month=dt.month, day=dt.day, hour=11, minute=30)
        afs = datetime(year=dt.year, month=dt.month, day=dt.day, hour=13, minute=0)
        afe = datetime(year=dt.year, month=dt.month, day=dt.day, hour=15, minute=0)
        if hard:
            if (ms <= dt <= me) or (afs <= dt <= afe):
                return True
        else:
            if ms <= dt <= afe:
                return True
        return False

    @classmethod
    def recent(cls, _date=None, forward=True):
        if _date is None:
            t = cls.today()
        elif isinstance(_date, datetime):
            t = _date
        else:
            t = cls.to(datetime, _date)
        while True:
            d = Calendar().query_one({'date': t})
            if d:
                return d
            else:
                if forward:
                    t -= timedelta(1)
                else:
                    t += timedelta(1)

    @classmethod
    def trans_data(cls, source_data):
        _ = list()
        l = len(source_data['calendarDate'])
        index = 0
        for i in range(l):
            if source_data['isOpen'][i]:
                r = re.search('(^\d{4})[./-]*(\d{1,2})[./-]*(\d{1,2}$)', source_data['calendarDate'][i])
                _.append(
                    {'date': datetime(year=int(r.group(1)), month=int(r.group(2)), day=int(r.group(3))), 'num': index})
                index += 1
        return _

    @classmethod
    def calc(cls, date, offset):
        if offset > 0:
            sd = cls.recent(date, False)
        else:
            sd = cls.recent(date)
        td = Calendar().query({'num':sd['num'] + offset})[0]
        return td

    @classmethod
    def to(cls, _type, dt, _format='%Y%m%d'):
        _ = None
        if isinstance(dt, dict):
            _ = dt['date']
        elif isinstance(dt, Timestamp):
            _ = dt.to_pydatetime()
        elif isinstance(dt, datetime):
            _ = dt
        elif isinstance(dt, int):
            dt = str(dt)
            if len(dt) == 8:
                _ = datetime(year=int(dt[0:4]), month=int(dt[4:6]), day=int(dt[-2:]))
            else:
                raise ValueError('input int date should be like 19990101')
        elif isinstance(dt, str):
            ld = len(dt)
            if ld >= 8 and ld <= 10:
                # _ = datetime(year=int(dt[0:4]), month=int(dt[4:6]), day=int(dt[-2:]))
                # elif ld == 10:
                r = re.search('(^\d{4})[./-]*(\d{1,2})[./-]*(\d{1,2}$)', dt)
                _ = datetime(year=int(r.groups()[0]), month=int(r.groups()[1]), day=int(r.groups()[2]))
            else:
                raise ValueError('input str date should be like "19990101" or "1999-01-01"')

        if _type in ['int', int]:
            return _.year * 10000 + _.month * 100 + _.day
        elif _type in ['str', str]:
            # return '{}{:02d}{:02d}'.format(_.year, _.month, _.day)
            return _.strftime(_format)
        elif _type in ['datetime', datetime]:
            return _


            # def __sub__(self, other):
            #     res = None
            #     if isinstance(other, Calendar):
            #         sd = other
            #         res = int(self.num - sd['num'])
            #     elif isinstance(other, int):
            #         r = re.search('^\d{8}$', str(other))
            #         if r:
            #             sd = Calendar.query(date=other)
            #             res = int(self.num - sd['num'])
            #         else:
            #             res = Calendar.query(num=self.num - other)
            #     elif isinstance(other, str):
            #         r = re.search('(^\d{4})[./-](\d{1,2})[./-](\d{1,2}$)', other)
            #         if r:
            #             sd = Calendar.query(date=int(''.join(r.group())))
            #             res = int(self.num - sd['num'])
            #     return res
            #
            # def __add__(self, other):
            #     res = None
            #     if isinstance(other, int):
            #         res = Calendar.query(num=self.num + other)
            #     return res

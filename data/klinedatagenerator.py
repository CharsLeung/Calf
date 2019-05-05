# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2019-04-22 15:26
"""
import numpy as np
import pandas as pd

from .klinedata import KlineData


class KlineDataGenerator(KlineData):

    """
    K线数据的一个迭代器
    """

    def __init__(self,
                 code,
                 start_date,
                 end_date,
                 kline,
                 axis=1,
                 timemerge=False,
                 fields=None,
                 batch_size=None,
                 location=None,
                 dbname=None,
                 **kwargs):
        """
        :param code: str or list when axis=0
        :param start_date:
        :param end_date:
        :param kline:
        :param fields:
        :param batch_size: int days
        :param location:
        :param dbname:
        """
        super(KlineDataGenerator, self).__init__(
            location, dbname
        )
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.kline = kline
        if axis in (0, 1):
            self.axis = axis
        else:
            raise ValueError('axis must in (0, 1).')
        self.timemerge = timemerge
        self.fields = fields
        self.kwargs = kwargs
        self.batch_size = batch_size
        self.days = self.__days__()
        pass

    def __days__(self):
        _ = self.field(
            table_name=self.kline,
            field_name='date',
            filter={'date': {'$gte': self.start_date, '$lte': self.end_date}}
        )
        return sorted(_)

    def __blocks__(self):
        """
        对查询结构进行分块，以便下一步分块查询
        :return:
        """
        bks = []
        if self.axis == 1:
            l = len(self.days)
            for i in range(0, l, self.batch_size):
                e = i + self.batch_size - 1
                if e >= l:
                    bks.append([self.days[i], self.days[l - 1]])
                else:
                    bks.append([self.days[i], self.days[e]])
        if self.axis == 0:
            l = len(self.code)
            for i in range(0, l, self.batch_size):
                e = i + self.batch_size - 1
                if e >= l:
                    bks.append([self.code[i], self.code[l - 1]])
                else:
                    bks.append([self.code[i], self.code[e]])
        return bks

    def datas(self):
        bks = self.__blocks__()
        if len(bks):
            pass
        else:
            raise StopIteration('invalid generator index.')
        if self.axis == 1:
            # data = self.read_data(
            #     code=self.code,
            #     start_date=bks[0][0],
            #     end_date=bks[0][1],
            #     kline=self.kline,
            #     axis=1,
            #     timemerge=self.timemerge,
            #     **self.kwargs
            # )
            for d in bks:
                # yield data
                data = self.read_data(
                    code=self.code,
                    start_date=d[0],
                    end_date=d[1],
                    kline=self.kline,
                    axis=1,
                    timemerge=self.timemerge,
                    **self.kwargs
                )
                yield data
                pass
        if self.axis == 0:
            for codes in bks:
                data = self.read_data(
                    code=codes,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    kline=self.kline,
                    axis=0,
                    timemerge=self.timemerge,
                    **self.kwargs
                )
                yield data
                pass
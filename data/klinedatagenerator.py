# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2019-04-22 15:26
"""
# import numpy as np
# import pandas as pd
import threading

from .klinedata import KlineData


class KlineThread(threading.Thread):

    def __init__(self, func, args=()):
        super(KlineThread, self).__init__()
        self.result = None
        self.func = func
        self.args = args

    def run(self):
        try:
            self.result = self.func(*self.args)
        except Exception:
            pass
        pass

    def get_result(self):
        return self.result


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
                    field=self.fields,
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
                    field=self.fields,
                    **self.kwargs
                )
                yield data
                pass
        pass

    def apply(self, func, args):
        """
        通过多线程使在读取数据的同时可以做计算，即为每一个数据块创建一个
        线程，并把相应的数据快交给对应的线程
        :param func:
        :param args:
        :return: a list with thread-func
        """
        threads = []
        for data in self.datas():
            th = KlineThread(func, args=(data, ) + args)
            threads.append(th)
            th.start()
        results = []
        for th in threads:
            th.join()
            results.append(th.get_result())
        return results
        pass

    def apply_on_window(self, func, args, windows=3):
        """
        把数据块组装成一个具有固定大小的窗口，并在窗口内执行
        多线程函数
        :param func:
        :param args:
        :param windows:
        :return: a list with thread-func
        """
        threads = []
        q = []
        for data in self.datas():
            q.append(data)
            if len(q) < windows:
                continue
            # func(q, 1, 2)
            th = KlineThread(func, args=(q.copy(),) + args)
            threads.append(th)
            th.start()
            q.pop(0)
        results = []
        for th in threads:
            th.join()
            results.append(th.get_result())
        return results
        pass
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
    加载K线数据的一个迭代器，目的是为了分块加载大规模的
    K线数据。通常情况下一次性加载符合条件的所有数据，这
    会造成内存灾难，会急剧拖慢速度。按照某种规则分块后，
    分批查询并返回，这样只会占用较少的内存，这在某些情况
    下是适用的。
    分块的一般思路：下表是code/date索引矩阵
    -----------------------------------------
    |       | code1 | code2 | ..... | coden |
    |-------+-------+-------+-------+-------+
    | date1 |       |       |       |       |
    |-------+-------+-------+-------+-------+
    | date2 |       |       |       |       |
    |-------+-------+-------+-------+-------+
    | ..... |       |       |       |       |
    |-------+-------+-------+-------+-------+
    | daten |       |       |       |       |
    |-------+-------+-------+-------+-------+
    每块是code-date索引矩阵的一个矩形子集。
    当前的版本只支持按code-date列或行划分块
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
        :param start_date: code/date索引矩阵date的开始位置
        :param end_date: code/date索引矩阵的结束位置
        :param axis: 1-> 按行分块(n天所有code的数据)
        0-> 按列索引(code中n个股票的所有date数据)
        :param batch_size: 当axis=1时，表示天数，当axis=0的
        表示股票代码数。
        以下参数可以参考KlineData类
        :param kline: 表名
        :param timemerge
        :param fields:
        :param location:
        :param dbname:
        :param kwargs
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
        """
        :return: a list of days from start_date to end_date
        """
        _ = self.field(
            table_name=self.kline,
            field_name='date',
            filter={'date': {'$gte': self.start_date, '$lte': self.end_date}}
        )
        return sorted(_)

    def __blocks__(self):
        """
        对查询结构进行分块，以便下一步分块查询
        :return: a list of blocks
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
                e = i + self.batch_size
                if e >= l:
                    bks.append(self.code[i:l - 1])
                else:
                    bks.append(self.code[i:e])
        return bks

    def datas(self):
        bks = self.__blocks__()
        if len(bks):
            pass
        else:
            raise StopIteration('invalid generator index.')
        if self.axis == 1:
            for d in bks:
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
                    axis=1,
                    timemerge=self.timemerge,
                    field=self.fields,
                    **self.kwargs
                )
                yield data
                pass
        pass

    def apply(self, func, args=None, use_multiprocessing=True):
        """
        通过多线程使在读取数据的同时可以做计算，即为每一个数据块创建一个
        线程，并把相应的数据快交给对应的线程
        :param use_multiprocessing:
        :param func:
        :param args:
        :return: a list with thread-func
        """
        threads, results = [], []
        for data in self.datas():
            arg = (data, ) + args if args is not None else (data, )
            if use_multiprocessing:
                th = KlineThread(func, args=arg)
                threads.append(th)
                th.start()
            else:
                results.append(func(*arg))
        if use_multiprocessing:
            for th in threads:
                th.join()
                results.append(th.get_result())
        return results
        pass

    def apply_on_window(self, func, args=None, windows=3,
                        use_multiprocessing=True):
        """
        把数据块组装成一个具有固定大小的窗口，并在窗口内执行
        多线程函数
        :param use_multiprocessing:
        :param func:
        :param args:
        :param windows:
        :return: a list with thread-func
        """
        threads, results = [], []
        q = []
        for data in self.datas():
            q.append(data)
            if len(q) < windows:
                continue
            # func(q, *args)
            arg = (q.copy(), ) + args if args is not None else (q.copy(), )
            if use_multiprocessing:
                th = KlineThread(func, args=arg)
                threads.append(th)
                th.start()
            else:
                results.append(func(*arg))
            q.pop(0)
        if use_multiprocessing:
            for th in threads:
                th.join()
                results.append(th.get_result())
        return results
        pass
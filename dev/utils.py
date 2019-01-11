# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/11/27 17:20
"""
import os, time, ntplib
import numpy as np
from Calf.exception import ExceptionInfo


def cut(left, right, interval, labels=None, println=False):
    """
    通过边界和组距计算bins、labels, pandas.cut函数需要
    使用这两个关键参数
    :param println:
    :param labels:
    :param left: 左边界
    :param right: 右边界
    :param interval: 组距
    :return:
    """
    if (right - left) % interval != 0:
        # 不能按组距(interval)等距划分[left, right]
        raise ValueError('不能按组距({})等距划分'.format(interval))
    else:
        # 两端开区间
        bins = [-np.inf] + list(np.arange(left, right + interval, interval)) + [np.inf]
        if labels is None:
            labels = np.arange(left // interval, (right + interval) // interval + 1, 1)
        else:
            if len(labels) + 1 != len(bins):
                raise ValueError('length of labels add 1 should equal length of bins')
        if println:
            for i in range(len(bins) - 1):
                print('({}, {}) -> {}'.format(bins[i], bins[i + 1], labels[i]))
        return bins, labels


# cut(-5, 55, 10, println=True)
def calibration():
    """
    将本地的时间与ali的时间同步
    :return:
    """
    try:
        c = ntplib.NTPClient()
        response = c.request('pool.ntp.org')
        ts = response.tx_time
        _date = time.strftime('%Y-%m-%d', time.localtime(ts))
        _time = time.strftime('%X', time.localtime(ts))
        os.system('date {} && time {}'.format(_date, _time))
    except Exception as e:
        ExceptionInfo(e)

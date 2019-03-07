# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/11/27 17:20
"""
import os, time, ntplib, glob
import numpy as np
from Calf.exception import ExceptionInfo
from skimage import io, transform


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
        # ExceptionInfo(e)
        pass
    pass


def read_images(path, reshape=None, start=None, end=None):
    """
    从path文件夹下读取图片，并使其转化成np数组
    各像素点是以[r,g,b,透明度]数组表示的
    :param path:
    :param reshape:
    :return:
    """
    path += '\\'
    cate = [path + x for x in os.listdir(path) if not os.path.isdir(path + x)]
    # 按文件名排序
    cate = sorted(cate)
    if start is not None and end is not None:
        cate = cate[start:end]
    images = []
    labels = []

    for idx, folder in enumerate(cate):
        for im in glob.glob(folder):
            # print('reading the images:%s' % (im))
            img = io.imread(im)
            if reshape is not None:
                img = transform.resize(img, reshape)
            images.append(img)
            # 图片名：label信息可能存储在这当中
            labels.append(im.split('\\')[-1])
        pass
    return np.asarray(images, np.float32), np.asarray(labels)

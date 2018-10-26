# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/27 15:35
"""
import numpy as np
import pandas as pd
from numpy import linalg as la


class SimilarShape(object):
    """

    """
    def __init__(self, superior, data, feature_columns):
        """
        :param superior: 我们认为表现优秀的那些信号点集，它是一个
        DataFrame，主要包含三个方面的数据，证券代码、信号时间、描述
        某个‘形状的’特征集。
        :param data:那些我们需要去计算与superior相似程度的目标数据，
        它的数据结构跟superior一样。
        :param feature_columns: 特征字段名
        """
        self.feature_columns = feature_columns
        self.superior = superior
        self.data = data

    def euclid_distance(self, r1, r2):
        """
        欧式距离
        :param r1:
        :param r2:
        :return:
        """
        inA = np.mat(r1[self.feature_columns])
        inB = np.mat(r2[self.feature_columns])
        return 1.0 / (1.0 + la.norm(inA - inB))

    def cos_distance(self, r1, r2):
        """
        余弦距离
        :param r1:
        :param r2:
        :return:
        """
        inA = np.mat(r1[self.feature_columns])
        inB = np.mat(r2[self.feature_columns])
        num = float(inA * inB.T)
        denom = la.norm(inA) * la.norm(inB)
        return 0.5 + 0.5 * (num / denom)

    def fit(self):
        spr = self.superior.loc[:, self.feature_columns]
        spr = spr.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        spr['code'] = self.superior.code
        spr['open_date'] = self.superior.open_date
        data = self.data
        X = self.data.loc[:, self.feature_columns]
        X = X.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        X['open_date'] = self.data.open_date
        rls = list()
        l = len(X)
        for i, row in X.iterrows():
            sp = spr[pd.eval('spr.open_date < row.open_date')]
            sp['dis'] = 0
            cos = pd.DataFrame([], columns=['dis'])
            cos['dis'] = sp.apply(lambda r: self.euclid_distance(row, r), axis=1)
            # cos = cos[pd.eval('cos.cos < 1')]
            arg = cos.dis.argmax()
            tag_code = sp.code.iloc[arg]
            tag_date = sp.open_date.iloc[arg]
            dis = sp.dis.iloc[arg]
            rls.append(dict(tag_code=tag_code, tag_date=tag_date, dis=dis))
            print('\r{0}/{1}'.format(i + 1, l), end=' ', flush=True)
        rls = pd.DataFrame(rls)
        data = pd.concat([data, rls], axis=1, join='outer')
        return data

import datetime as dt
# d1 = dt.datetime(2017, 1, 1)
# d1 = pd.Timestamp(d1, freq='d')
# print(d1.timestamp())
# print(pd.to_datetime(d1.timestamp(), unit='s'))
# print(type(d1))
clm = ['amount', 'J', 'j1', 'j2', 'j3', 'j4', 'l1', 'l2', 'l3', 'l4',
       's1', 's2', 's3', 's4', 'angle1', 'angle2', 'angle3', 'angle4',
       'dt1', 'dt2', 'dt3', 'qs120', 'qs26', 'up120', 'up26', 'gains', '2y']
data = pd.read_csv('C:\\Users\Administrator\Desktop\SX\day\kdj_J_2018.csv')
data['open_date'] = pd.to_datetime(data.open_date)
will = pd.read_csv('C:\\Users\Administrator\Desktop\SX\day\kdj_J_win_16_17.csv')
will['open_date'] = pd.to_datetime(will.open_date)
will = will[will.open_date < dt.datetime(2016, 10, 1)]
SimilarShape(will, data, clm).fit()
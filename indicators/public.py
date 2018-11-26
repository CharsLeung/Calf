# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/3/21 9:50
"""
import numba
import pandas as pd


@numba.jit
def EMA(data, N):
    tiaoguo0 = 0
    data_t = data[:]
    for i in range(len(data) - 2, -1, -1):
        if tiaoguo0 > 0 or data[i] > 0:
            tiaoguo0 = 1
            data_t[i] = (data[i] * 2 + data_t[i + 1] * (N - 1)) / (N + 1)
    return data_t


# @numba.jit
def MACD(data, short=12, long=26, mid=9):
    data['s'] = EMA(list(data['close']), short)
    data['l'] = EMA(list(data['close']), long)
    data['dif'] = pd.eval('data.s - data.l')
    data['dea'] = EMA(list(data['dif']), mid)
    data['macd'] = pd.eval('2 * (data.dif - data.dea)')
    data.fillna(0, inplace=True)
    data.drop(['s', 'l'], axis=1, inplace=True)
    return data


@numba.jit
def SMA2(data, N, M):
    tiaoguo0 = 0
    data_t = data[:]
    for i in range(len(data) - 2, -1, -1):
        if tiaoguo0 > 0 or data[i] > 0:
            tiaoguo0 = 1
            data_t[i] = (data[i] * M + data_t[i + 1] * (N - M)) / N
    return data_t


def KDJ(data, n=9, m=3):
    data = data[::-1]
    data['low_list'] = data['low'].rolling(window=n).min()
    data['high_list'] = data['high'].rolling(window=n).max()
    data['rsv'] = pd.eval('(data.close - data.low_list) / (data.high_list - data.low_list) * 100')
    data = data[::-1]
    data.fillna(0, inplace=True)

    data['K'] = KDJ.SMA2(list(data.rsv), m, 1)
    data['D'] = KDJ.SMA2(list(data.K), m, 1)
    data['J'] = pd.eval('3 * data.K - 2 * data.D')
    data.drop(['low_list', 'high_list', 'rsv'], axis=1, inplace=True)
    return data
    pass


def QRR(data, level, N=5):
    """
    quantity relative ratio,与过去N个相同时间周期的成交额相比
    :return:
    """
    if level == 'day':
        data = data.sort_values('date', ascending=False)
        data['MAn'] = data.amount.rolling(window=N).mean()
        data['QRR'] = data.amount / data.MAn.shift(-1)
        data.drop(['MAn'], axis=1, inplace=True)
    if level == 'min':
        data = data.sort_values(['date', 'time'], ascending=False)
        data['QRR'] = 1
        for k, w in data.iterrows():
            _ = data[data.time == w.time].loc[(k + 1)::, ['amount']].head(N)
            la = _.amount.mean()
            data.at[k, ['QRR']] = w.amount / la if la != 0 else 1
    data.QRR.fillna(1, inplace=True)
    data = data.round({'QRR': 2})
    return data




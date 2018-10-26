# coding=utf-8
import numpy as np
import pandas as pd
import numba


def cross(data, col_name_1, col_name_2, col_name_3, col_name_4, result_1, result_2):
    data[result_1] = (data[col_name_1] < data[col_name_2]) & (data[col_name_3] > data[col_name_4])
    data[result_2] = (data[col_name_1] > data[col_name_2]) & (data[col_name_3] < data[col_name_4])

    return data


def last_n(data, n=1, col_name='close'):
    temp = data[col_name][n:]
    temp.reset_index(drop=True, inplace=True)
    return temp


def next_n(data, n=1, col_name='close'):
    temp = data[col_name].iloc[::-1]
    for i in range(n):
        temp = temp.append(pd.Series({col_name: 0}), ignore_index=True)
    temp = temp.iloc[::-1]
    temp = temp.reset_index(drop=True)
    return temp


@numba.jit
def SMA2(data, N, M):
    tiaoguo0 = 0
    data_t = data[:]
    for i in range(len(data) - 2, -1, -1):
        if tiaoguo0 > 0 or data[i] > 0:
            tiaoguo0 = 1
            data_t[i] = (data[i] * M + data_t[i + 1] * (N - M)) / N
    return data_t


@numba.jit
def EMA(data, N):
    tiaoguo0 = 0
    data_t = data[:]
    for i in range(len(data) - 2, -1, -1):
        if tiaoguo0 > 0 or data[i] > 0:
            tiaoguo0 = 1
            data_t[i] = (data[i] * 2 + data_t[i + 1] * (N - 1)) / (N + 1)
    return data_t


@numba.jit
def cci_helper(typ, typ_mean, n):
    cci = typ[:]
    for i in range(len(typ) - n):
        ssum = 0
        cci1 = typ[i] - typ_mean[i]
        for j in range(n):
            ssum += abs(typ[i + j] - typ_mean[i])
        if ssum > 0:
            cci[i] = cci1 / (0.015 * (ssum / n))
        else:
            cci[i] = 0
    return cci


def n_RSI(data, N1=6, N2=12, N3=24):
    # data['max'] = data.apply(lambda x: x.close - x.last_close if x.close - x.last_close > 0
    data['max'] = data.close - data.last_close
    data.loc[data['max'] < 0, 'max'] = 0
    data['abs'] = abs(data.close - data.last_close)

    # SMA  X的N日移动平均
    data['RSI1_1'] = SMA2(list(data['max']), N1, 1)

    # data['RSI1_1'] = data['max']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'RSI1_1'] = (data.loc[i, 'max'] * 1 + data.loc[i+1, 'RSI1_1'] * (N1 - 1)) / N1

    data['RSI1_2'] = SMA2(list(data['abs']), N1, 1)

    # data['RSI1_2'] = data['abs']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'RSI1_2'] = (data.loc[i, 'abs'] * 1 + data.loc[i+1, 'RSI1_2'] * (N1 - 1)) / N1

    data['RSI1'] = data['RSI1_1'] / data['RSI1_2'] * 100

    data['RSI2_1'] = SMA2(list(data['max']), N2, 1)

    # data['RSI2_1'] = data['max']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'RSI2_1'] = (data.loc[i, 'max'] * 1 + data.loc[i+1, 'RSI2_1'] * (N2 - 1)) / N2

    data['RSI2_2'] = SMA2(list(data['abs']), N2, 1)

    # data['RSI2_2'] = data['abs']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'RSI2_2'] = (data.loc[i, 'abs'] * 1 + data.loc[i+1, 'RSI2_2'] * (N2 - 1)) / N2

    data['RSI2'] = data['RSI2_1'] / data['RSI2_2'] * 100

    data['RSI3_1'] = SMA2(list(data['max']), N3, 1)
    # data['RSI3_1'] = data['max']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'RSI3_1'] = (data.loc[i, 'max'] * 1 + data.loc[i+1, 'RSI3_1'] * (N3 - 1)) / N3
    # data['RSI3_2'] = data['abs']

    data['RSI3_2'] = SMA2(list(data['abs']), N3, 1)
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'RSI3_2'] = (data.loc[i, 'abs'] * 1 + data.loc[i+1, 'RSI3_2'] * (N3 - 1)) / N3

    data['RSI3'] = data['RSI3_1'] / data['RSI3_2'] * 100

    # 白色的短期ＲＳＩ值在２０以下,由下向上交叉黄色的长期ＲＳＩ值时为买入信号。
    data['sRSI_z'] = last_n(data, 1, 'RSI1')
    data['lRSI_z'] = last_n(data, 1, 'RSI3')
    data.fillna(0, inplace=True)

    data['sRSI_20_cross_lRSI'] = (data['RSI1'] < 20.0) & (data['sRSI_z'] < data['lRSI_z']) & (
    data['RSI1'] > data['RSI3'])
    # data['sRSI_20_cross_lRSI'] = x['RSI1'] < 20.0 and x['sRSI_z'] < x['lRSI_z'] and x['RSI1'] > x['RSI3'] else 0,axis=1)
    # 白色的短期ＲＳＩ值在８０以上,由上向下交叉黄色的长期ＲＳＩ值时为卖出信号。
    data['sRSI_80_cross_lRSI'] = (data['RSI1'] > 80.0) & (data['RSI1'] < data['RSI3']) & (
    data['sRSI_z'] > data['lRSI_z'])
    # data['sRSI_80_cross_lRSI'] = data.apply(
    #     lambda x: 1 if x['RSI1'] > 80.0 and x['RSI1'] < x['RSI3'] and x['sRSI_z'] > x['lRSI_z']

    # 短期ＲＳＩ值由上向下突破５０,代表股价已经转弱。
    data['sRSI_down_cross_50'] = (data['RSI1'] < 50.0) & (data['sRSI_z'] > 50.0)
    # data['sRSI_down_cross_50'] = data.apply(
    #     lambda x: 1 if x['RSI1'] < 50.0 and x['sRSI_z'] > 50.0
    # 短期ＲＳＩ值由下向上突破５０,代表股价已经转强。
    data['sRSI_up_cross_50'] = (data['RSI1'] > 50.0) & (data['sRSI_z'] < 50.0)
    # data['sRSI_up_cross_50'] = data.apply(
    #     lambda x: 1 if x['RSI1'] > 50.0 and x['sRSI_z'] < 50.0
    # 当ＲＳＩ值高于８０进入超买区,股价随时可能形成短期回档。
    data['sRSI_up_cross_80'] = data['RSI1'] > 80.0
    # data['sRSI_up_cross_80'] = data.apply(
    #     lambda x: 1 if x['RSI1'] > 80.0 
    # 当ＲＳＩ值低于２０进入超卖区,股价随时可能形成短期反弹。
    data['sRSI_down_cross_20'] = data['RSI1'] < 20.0
    # data['sRSI_down_cross_20'] = data.apply(
    #     lambda x: 1 if x['RSI1'] < 20.0 

    # data.drop(['max', 'RSI1_1', 'abs', 'RSI1_2', 'RSI2_1', 'RSI2_2', 'RSI3_1', 'RSI3_2', 'RSI1', 'RSI2', 'RSI3', 'sRSI_z',     'lRSI_z'], axis=1, inplace=True)
    return data


def n_KDJ(data, n=9, m=3):
    data = data[::-1]
    data['low_list'] = data['low'].rolling(window=n).min()
    data['high_list'] = data['high'].rolling(window=n).max()
    data['rsv'] = (data['close'] - data['low_list']) / (data['high_list'] - data['low_list']) * 100
    data = data[::-1]
    data.fillna(0, inplace=True)

    data['K'] = SMA2(list(data.rsv), m, 1)
    # data['K']=data['rsv']
    # indec = 0
    # for i in xrange(len(data) - 2, -1, -1):
    #     if data['rsv'][i] > 0.0:
    #          # indec = indec+1
    #          # if indec >1:
    #          data.loc[i, 'K'] = (data.loc[i, 'rsv'] * 1 + data.loc[i+1, 'K'] * (m - 1)) / m

    data['D'] = SMA2(list(data.K), m, 1)
    # data['D'] = data['K']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'D'] = (data.loc[i, 'K'] * 1 + data.loc[i+1, 'D'] * (m - 1)) / m
    # data['K']=data['rsv'].rolling(window=m).mean()
    # data['D']=data['K'].rolling(window=m).mean()
    data['J'] = 3 * data['K'] - 2 * data['D']

    data['J_z'] = last_n(data, 1, 'J')
    data['D_z'] = last_n(data, 1, 'D')

    # J小于20 金叉
    data['J_less_20'] = (data['J'] < 20.0) & (data['J_z'] < data['D_z']) & (data['J'] > data['D'])
    # data['J_less_20'] = x['J'] < 20.0 and x['J_z']<x['D_z'] and x['J']>x['D']
    # J大于80 死叉
    data['J_over_80'] = (data['J'] < 80.0) & (data['J_z'] < data['D_z']) & (data['J'] > data['D'])
    # data['J_over_80'] = x['J'] < 80.0 and x['J_z'] < x['D_z'] and x['J'] > x['D']
    # J下穿100
    data['J_down_cross_100'] = (data['J'] < 100) & (data['J_z'] > 100)
    # data['J_down_cross_100']=x['J'] < 100 and x['J_z'] > 100
    # J上穿0
    data['J_up_cross_0'] = (data['J'] > 0) & (data['J_z'] < 0)
    # KDJ 背驰
    data['J_up_cross_0'] = (data['J'] > 0) & (data['J_z'] < 0)

    data = data[::-1]
    data['kdj_60_max'] = data['J_z'].rolling(window=60).max()
    data['kdj_30_max'] = data['J_z'].rolling(window=30).max()
    data['kdj_10_max'] = data['J_z'].rolling(window=10).max()
    data['kdj_5_max'] = data['J_z'].rolling(window=5).max()
    data['kdj_60_min'] = data['J_z'].rolling(window=60).min()
    data['kdj_30_min'] = data['J_z'].rolling(window=30).min()
    data['kdj_10_min'] = data['J_z'].rolling(window=10).min()
    data['kdj_5_min'] = data['J_z'].rolling(window=5).min()
    data = data[::-1]

    data['kdj_5_10_up'] = abs(data['kdj_5_max'] - data['kdj_10_max']) / 100
    data['kdj_5_30_up'] = abs(data['kdj_5_max'] - data['kdj_30_max']) / 100
    data['kdj_5_60_up'] = abs(data['kdj_5_max'] - data['kdj_60_max']) / 100

    data['kdj_5_10_down'] = (data['kdj_5_min'] - data['kdj_10_min']) / 100
    data['kdj_5_30_down'] = (data['kdj_5_min'] - data['kdj_30_min']) / 100
    data['kdj_5_60_down'] = (data['kdj_5_min'] - data['kdj_60_min']) / 100

    # data.drop(['low_list', 'high_list', 'rsv', 'K', 'D', 'J_z', 'J', 'D_z','kdj_60_max','kdj_30_max','kdj_10_max','kdj_5_max','kdj_60_min','kdj_30_min','kdj_10_min','kdj_5_min'], axis=1, inplace=True)
    data.fillna(0, inplace=True)
    return data


def n_MA(data):
    data['last_close'] = last_n(data, 1, 'close')
    data['last_high'] = last_n(data, 1, 'high')
    data['last_low'] = last_n(data, 1, 'low')
    data['last_open'] = last_n(data, 1, 'open')
    data['last_volume'] = last_n(data, 1, 'volume')
    data['last2_close'] = last_n(data, 2, 'close')
    data['last2_high'] = last_n(data, 2, 'high')
    data['last2_low'] = last_n(data, 2, 'low')
    data['last2_open'] = last_n(data, 2, 'open')
    data['last2_volume'] = last_n(data, 2, 'volume')
    data['last3_close'] = last_n(data, 3, 'close')
    data['last3_high'] = last_n(data, 3, 'high')
    data['last3_low'] = last_n(data, 3, 'low')
    data['last3_open'] = last_n(data, 3, 'open')
    data['last3_volume'] = last_n(data, 3, 'volume')
    data['last4_close'] = last_n(data, 4, 'close')
    data['last4_high'] = last_n(data, 4, 'high')
    data['last4_low'] = last_n(data, 4, 'low')
    data['last4_open'] = last_n(data, 4, 'open')
    data['last4_volume'] = last_n(data, 4, 'volume')
    data['last5_high'] = last_n(data, 5, 'high')
    data['last5_low'] = last_n(data, 5, 'low')
    data['last10_high'] = last_n(data, 10, 'high')
    data['last10_low'] = last_n(data, 10, 'low')
    data['last20_high'] = last_n(data, 20, 'high')
    data['last20_low'] = last_n(data, 20, 'low')

    data = data[::-1]
    data['ma5'] = data['close'].rolling(window=5).mean()
    data['ma10'] = data['close'].rolling(window=10).mean()
    data['ma20'] = data['close'].rolling(window=20).mean()
    data['ma30'] = data['close'].rolling(window=30).mean()
    data['ma60'] = data['close'].rolling(window=60).mean()
    data['v_ma5'] = data['volume'].rolling(window=5).mean()
    data['v_ma10'] = data['volume'].rolling(window=10).mean()
    data['v_ma20'] = data['volume'].rolling(window=20).mean()
    data['v_ma30'] = data['volume'].rolling(window=30).mean()
    data['v_ma60'] = data['volume'].rolling(window=60).mean()
    data['vv_ma5'] = data['volume'].rolling(window=5).sum()
    data['vv_ma10'] = data['volume'].rolling(window=10).sum()
    data['vv_ma20'] = data['volume'].rolling(window=20).sum()
    data['vv_ma30'] = data['volume'].rolling(window=30).sum()
    data['vv_ma60'] = data['volume'].rolling(window=60).sum()

    data['highest_5'] = data['last_high'].rolling(window=5).max()
    data['highest_10'] = data['last_high'].rolling(window=10).max()
    data['highest_20'] = data['last_high'].rolling(window=20).max()
    data['highest_30'] = data['last_high'].rolling(window=30).max()
    data['highest_60'] = data['last_high'].rolling(window=60).max()

    data['highest_5_5'] = data['last5_high'].rolling(window=5).max()
    data['highest_10_5'] = data['last5_high'].rolling(window=10).max()
    data['highest_20_5'] = data['last5_high'].rolling(window=20).max()
    data['highest_30_5'] = data['last5_high'].rolling(window=30).max()
    data['highest_60_5'] = data['last5_high'].rolling(window=60).max()

    data['highest_5_10'] = data['last10_high'].rolling(window=5).max()
    data['highest_10_10'] = data['last10_high'].rolling(window=10).max()
    data['highest_20_10'] = data['last10_high'].rolling(window=20).max()
    data['highest_30_10'] = data['last10_high'].rolling(window=30).max()
    data['highest_60_10'] = data['last10_high'].rolling(window=60).max()

    data['highest_5_20'] = data['last20_high'].rolling(window=5).max()
    data['highest_10_20'] = data['last20_high'].rolling(window=10).max()
    data['highest_20_20'] = data['last20_high'].rolling(window=20).max()
    data['highest_30_20'] = data['last20_high'].rolling(window=30).max()
    data['highest_60_20'] = data['last20_high'].rolling(window=60).max()

    data['highestl_5'] = data['last_high'].rolling(window=5).min()
    data['highestl_10'] = data['last_high'].rolling(window=10).min()
    data['highestl_20'] = data['last_high'].rolling(window=20).min()
    data['highestl_30'] = data['last_high'].rolling(window=30).min()
    data['highestl_60'] = data['last_high'].rolling(window=60).min()

    data['lowest_5'] = data['last_low'].rolling(window=5).min()
    data['lowest_10'] = data['last_low'].rolling(window=10).min()
    data['lowest_20'] = data['last_low'].rolling(window=20).min()
    data['lowest_30'] = data['last_low'].rolling(window=30).min()
    data['lowest_60'] = data['last_low'].rolling(window=60).min()

    data['lowest_5_5'] = data['last5_low'].rolling(window=5).min()
    data['lowest_10_5'] = data['last5_low'].rolling(window=10).min()
    data['lowest_20_5'] = data['last5_low'].rolling(window=20).min()
    data['lowest_30_5'] = data['last5_low'].rolling(window=30).min()
    data['lowest_60_5'] = data['last5_low'].rolling(window=60).min()

    data['lowest_5_10'] = data['last10_low'].rolling(window=5).min()
    data['lowest_10_10'] = data['last10_low'].rolling(window=10).min()
    data['lowest_20_10'] = data['last10_low'].rolling(window=20).min()
    data['lowest_30_10'] = data['last10_low'].rolling(window=30).min()
    data['lowest_60_10'] = data['last10_low'].rolling(window=60).min()

    data['lowest_5_20'] = data['last20_low'].rolling(window=5).min()
    data['lowest_10_20'] = data['last20_low'].rolling(window=10).min()
    data['lowest_20_20'] = data['last20_low'].rolling(window=20).min()
    data['lowest_30_20'] = data['last20_low'].rolling(window=30).min()
    data['lowest_60_20'] = data['last20_low'].rolling(window=60).min()

    data['lowesth_5'] = data['last_low'].rolling(window=5).max()
    data['lowesth_10'] = data['last_low'].rolling(window=10).max()
    data['lowesth_20'] = data['last_low'].rolling(window=20).max()
    data['lowesth_30'] = data['last_low'].rolling(window=30).max()
    data['lowesth_60'] = data['last_low'].rolling(window=60).max()
    data.fillna(0, inplace=True)
    data = data[::-1]

    data['p_close'] = next_n(data, 1, 'close')
    data['change_r_next'] = (data.p_close - data.close) / data.close
    # 距离close ,5 ，10，20，30，60，120

    data['Close_dt_ma5'] = data['close'] / data['ma5']
    data['Close_dt_ma10'] = data['close'] / data['ma10']
    data['Close_dt_ma20'] = data['close'] / data['ma20']
    data['Close_dt_ma30'] = data['close'] / data['ma30']
    data['Close_dt_ma60'] = data['close'] / data['ma60']

    # 价格成交量收益率

    data['change_r'] = data['close'] / data['last_close']
    data['volume_r'] = data['volume'] / data['last_volume']

    # 成交量距离

    data['v_dt_ma5'] = data['volume'] / data['v_ma5']
    data['v_dt_ma10'] = data['volume'] / data['v_ma10']
    data['v_dt_ma20'] = data['volume'] / data['v_ma20']
    data['v_dt_ma30'] = data['volume'] / data['v_ma30']
    data['v_dt_ma60'] = data['volume'] / data['v_ma60']

    data['vv_dt_ma5'] = data['volume'] / data['vv_ma5']
    data['vv_dt_ma10'] = data['volume'] / data['vv_ma10']
    data['vv_dt_ma20'] = data['volume'] / data['vv_ma20']
    data['vv_dt_ma30'] = data['volume'] / data['vv_ma30']
    data['vv_dt_ma60'] = data['volume'] / data['vv_ma60']

    # 新高新低

    data['New_Highest_60'] = data.high > data.highest_60  # 26
    data['New_Highest_30'] = data.high > data.highest_30  # 26
    data['New_Highest_20'] = data.high > data.highest_20  # 26
    data['New_Highest_10'] = data.high > data.highest_10  # 26
    data['New_Highest_5'] = data.high > data.highest_5  # 26

    data['New_Lowest_60'] = data.low < data.lowest_60  # 26
    data['New_Lowest_30'] = data.low < data.lowest_30  # 26
    data['New_Lowest_20'] = data.low < data.lowest_20  # 26
    data['New_Lowest_10'] = data.low < data.lowest_10  # 26
    data['New_Lowest_5'] = data.low < data.lowest_5  # 26

    data['New_H_60'] = data.high / data.highest_60  # 26
    data['New_H_30'] = data.high / data.highest_30  # 26
    data['New_H_20'] = data.high / data.highest_20  # 26
    data['New_H_10'] = data.high / data.highest_10  # 26
    data['New_H_5'] = data.high / data.highest_5  # 26

    data['New_H_60_5'] = data.high / data.highest_60_5  # 26
    data['New_H_30_5'] = data.high / data.highest_30_5  # 26
    data['New_H_20_5'] = data.high / data.highest_20_5  # 26
    data['New_H_10_5'] = data.high / data.highest_10_5  # 26
    data['New_H_5_5'] = data.high / data.highest_5_5  # 26

    data['New_H_60_10'] = data.high / data.highest_60_10  # 26
    data['New_H_30_10'] = data.high / data.highest_30_10  # 26
    data['New_H_20_10'] = data.high / data.highest_20_10  # 26
    data['New_H_10_10'] = data.high / data.highest_10_10  # 26
    data['New_H_5_10'] = data.high / data.highest_5_10  # 26

    data['New_H_60_20'] = data.high / data.highest_60_20  # 26
    data['New_H_30_20'] = data.high / data.highest_30_20  # 26
    data['New_H_20_20'] = data.high / data.highest_20_20  # 26
    data['New_H_10_20'] = data.high / data.highest_10_20  # 26
    data['New_H_5_20'] = data.high / data.highest_5_20  # 26

    data['New_Hl_60'] = data.low / data.highestl_60  # 26
    data['New_Hl_30'] = data.low / data.highestl_30  # 26
    data['New_Hl_20'] = data.low / data.highestl_20  # 26
    data['New_Hl_10'] = data.low / data.highestl_10  # 26
    data['New_Hl_5'] = data.low / data.highestl_5  # 26

    data['New_L_60'] = data.low / data.lowest_60  # 26
    data['New_L_30'] = data.low / data.lowest_30  # 26
    data['New_L_20'] = data.low / data.lowest_20  # 26
    data['New_L_10'] = data.low / data.lowest_10  # 26
    data['New_L_5'] = data.low / data.lowest_5  # 26

    data['New_L_60_5'] = data.low / data.lowest_60_5  # 26
    data['New_L_30_5'] = data.low / data.lowest_30_5  # 26
    data['New_L_20_5'] = data.low / data.lowest_20_5  # 26
    data['New_L_10_5'] = data.low / data.lowest_10_5  # 26
    data['New_L_5_5'] = data.low / data.lowest_5_5  # 26

    data['New_L_60_10'] = data.low / data.lowest_60_10  # 26
    data['New_L_30_10'] = data.low / data.lowest_30_10  # 26
    data['New_L_20_10'] = data.low / data.lowest_20_10  # 26
    data['New_L_10_10'] = data.low / data.lowest_10_10  # 26
    data['New_L_5_10'] = data.low / data.lowest_5_10  # 26

    data['New_L_60_20'] = data.low / data.lowest_60_20  # 26
    data['New_L_30_20'] = data.low / data.lowest_30_20  # 26
    data['New_L_20_20'] = data.low / data.lowest_20_20  # 26
    data['New_L_10_20'] = data.low / data.lowest_10_20  # 26
    data['New_L_5_20'] = data.low / data.lowest_5_20  # 26

    data['New_L_60_5'] = data.low / data.lowest_60_5  # 26
    data['New_L_30_5'] = data.low / data.lowest_30_5  # 26
    data['New_L_20_5'] = data.low / data.lowest_20_5  # 26
    data['New_L_10_5'] = data.low / data.lowest_10_5  # 26
    data['New_L_5_5'] = data.low / data.lowest_5_5  # 26

    data['New_Lh_60'] = data.high / data.lowesth_60  # 26
    data['New_Lh_30'] = data.high / data.lowesth_30  # 26
    data['New_Lh_20'] = data.high / data.lowesth_20  # 26
    data['New_Lh_10'] = data.high / data.lowesth_10  # 26
    data['New_Lh_5'] = data.high / data.lowesth_5  # 26

    data['h_5_10'] = data.highest_5 / data.highest_10
    data['h_10_20'] = data.highest_10 / data.highest_20
    data['h_20_30'] = data.highest_20 / data.highest_30
    data['h_30_60'] = data.highest_30 / data.highest_60

    data['l_5_10'] = data.lowest_5 / data.highest_10
    data['l_10_20'] = data.lowest_10 / data.lowest_20
    data['l_20_30'] = data.lowest_20 / data.lowest_30
    data['l_30_60'] = data.lowest_30 / data.lowest_60

    # 多头排列 5>10>20
    data['duotou_5_10_20'] = (data['ma5'] > data['ma10']) & (data['ma10'] > data['ma20'])

    # 空头排列 5<10<20
    data['kongtou_5_10_20'] = (data['ma5'] < data['ma10']) & (data['ma10'] < data['ma20'])

    # 角度5，10，20，30，60，120
    data['ma5_z'] = last_n(data, 1, 'ma5')
    data['ma10_z'] = last_n(data, 1, 'ma10')
    data['ma20_z'] = last_n(data, 1, 'ma20')
    data['ma30_z'] = last_n(data, 1, 'ma30')
    data['ma60_z'] = last_n(data, 1, 'ma60')

    data['ma5_z2'] = last_n(data, 2, 'ma5')
    data['ma10_z2'] = last_n(data, 2, 'ma10')
    data['ma20_z2'] = last_n(data, 2, 'ma20')
    data['ma30_z2'] = last_n(data, 2, 'ma30')
    data['ma60_z2'] = last_n(data, 2, 'ma60')

    data['ma5_z3'] = last_n(data, 3, 'ma5')
    data['ma10_z3'] = last_n(data, 3, 'ma10')
    data['ma20_z3'] = last_n(data, 3, 'ma20')
    data['ma30_z3'] = last_n(data, 3, 'ma30')
    data['ma60_z3'] = last_n(data, 3, 'ma60')

    data['ma5_z4'] = last_n(data, 4, 'ma5')
    data['ma10_z4'] = last_n(data, 4, 'ma10')
    data['ma20_z4'] = last_n(data, 4, 'ma20')
    data['ma30_z4'] = last_n(data, 4, 'ma30')
    data['ma60_z4'] = last_n(data, 4, 'ma60')

    # ma 角度

    data['ma5_angle'] = data.ma5 / data.ma5_z
    data['ma10_angle'] = data.ma10 / data.ma10_z
    data['ma20_angle'] = data.ma20 / data.ma20_z
    data['ma30_angle'] = data.ma30 / data.ma30_z
    data['ma60_angle'] = data.ma60 / data.ma60_z

    data['ma5_angle2'] = data.ma5_z / data.ma5_z2
    data['ma10_angle2'] = data.ma10_z / data.ma10_z2
    data['ma20_angle2'] = data.ma20_z / data.ma20_z2
    data['ma30_angle2'] = data.ma30_z / data.ma30_z2
    data['ma60_angle2'] = data.ma60_z / data.ma60_z2

    data['ma5_angle3'] = data.ma5_z2 / data.ma5_z3
    data['ma10_angle3'] = data.ma10_z2 / data.ma10_z3
    data['ma20_angle3'] = data.ma20_z2 / data.ma20_z3
    data['ma30_angle3'] = data.ma30_z2 / data.ma30_z3
    data['ma60_angle3'] = data.ma60_z2 / data.ma60_z3

    data['ma5_angle4'] = data.ma5_z3 / data.ma5_z4
    data['ma10_angle4'] = data.ma10_z3 / data.ma10_z4
    data['ma20_angle4'] = data.ma20_z3 / data.ma20_z4
    data['ma30_angle4'] = data.ma30_z3 / data.ma30_z4
    data['ma60_angle4'] = data.ma60_z3 / data.ma60_z4

    # 距离5，10，20，30，60，120
    data['ma5_gt_ma10'] = data.ma5 / data.ma10
    data['ma10_gt_ma20'] = data.ma10 / data.ma20
    data['ma20_gt_ma30'] = data.ma20 / data.ma30
    data['ma30_gt_ma60'] = data.ma30 / data.ma60

    data['last_ma5_gt_ma10'] = data.ma5_z / data.ma10_z
    data['last_ma10_gt_ma20'] = data.ma10_z / data.ma20_z
    data['last_ma20_gt_ma30'] = data.ma20_z / data.ma30_z
    data['last_ma30_gt_ma60'] = data.ma30_z / data.ma60_z

    # k self features 3
    data['last2_close_open'] = data.last2_close / data.last2_open
    data['last2_high_open'] = data.last2_high / data.last2_open
    data['last2_low_open'] = data.last2_low / data.last2_open
    data['last2_close_low'] = data.last2_close / data.last2_low
    data['last2_high_low'] = data.last2_high / data.last2_low
    data['last2_close_high'] = data.last2_close / data.last2_high

    # k self features 2
    data['last_close_open'] = data.last_close / data.last_open
    data['last_high_open'] = data.last_high / data.last_open
    data['last_low_open'] = data.last_low / data.last_open
    data['last_close_low'] = data.last_close / data.last_low
    data['last_high_low'] = data.last_high / data.last_low
    data['last_close_high'] = data.last_close / data.last_high

    # k self features 1
    data['close_open'] = data.close / data.open
    data['high_open'] = data.high / data.open
    data['low_open'] = data.low / data.open
    data['close_low'] = data.close / data.low
    data['high_low'] = data.high / data.low
    data['close_high'] = data.close / data.high

    # k cross features 1,2
    data['close_last_close'] = data.close / data.last_close
    data['high_last_close'] = data.high / data.last_close
    data['low_last_close'] = data.low / data.last_close
    data['open_last_close'] = data.open / data.last_close
    data['close_last_open'] = data.close / data.last_open
    data['high_last_open'] = data.high / data.last_open
    data['low_last_open'] = data.low / data.last_open
    data['open_last_open'] = data.open / data.last_open
    data['close_last_high'] = data.close / data.last_high
    data['high_last_high'] = data.high / data.last_high
    data['low_last_high'] = data.low / data.last_high
    data['open_last_high'] = data.open / data.last_high
    data['close_last_low'] = data.close / data.last_low
    data['high_last_low'] = data.high / data.last_low
    data['low_last_low'] = data.low / data.last_low
    data['open_last_low'] = data.open / data.last_low

    # k cross features 2,3
    data['close_last_close_23'] = data.last_close / data.last2_close
    data['high_last_close_23'] = data.last_high / data.last2_close
    data['low_last_close_23'] = data.last_low / data.last2_close
    data['open_last_close_23'] = data.last_open / data.last2_close
    data['close_last_open_23'] = data.last_close / data.last2_open
    data['high_last_open_23'] = data.last_high / data.last2_open
    data['low_last_open_23'] = data.last_low / data.last2_open
    data['open_last_open_23'] = data.last_open / data.last2_open
    data['close_last_high_23'] = data.last_close / data.last2_high
    data['high_last_high_23'] = data.last_high / data.last2_high
    data['low_last_high_23'] = data.last_low / data.last2_high
    data['open_last_high_23'] = data.last_open / data.last2_high
    data['close_last_low_23'] = data.last_close / data.last2_low
    data['high_last_low_23'] = data.last_high / data.last2_low
    data['low_last_low_23'] = data.last_low / data.last2_low
    data['open_last_low_23'] = data.last_open / data.last2_low

    # k cross features 3,4
    data['close_last_close_34'] = data.last2_close / data.last3_close
    data['high_last_close_34'] = data.last2_high / data.last3_close
    data['low_last_close_34'] = data.last2_low / data.last3_close
    data['open_last_close_34'] = data.last2_open / data.last3_close
    data['close_last_open_34'] = data.last2_close / data.last3_open
    data['high_last_open_34'] = data.last2_high / data.last3_open
    data['low_last_open_34'] = data.last2_low / data.last3_open
    data['open_last_open_34'] = data.last2_open / data.last3_open
    data['close_last_high_34'] = data.last2_close / data.last3_high
    data['high_last_high_34'] = data.last2_high / data.last3_high
    data['low_last_high_34'] = data.last2_low / data.last3_high
    data['open_last_high_34'] = data.last2_open / data.last3_high
    data['close_last_low_34'] = data.last2_close / data.last3_low
    data['high_last_low_34'] = data.last2_high / data.last3_low
    data['low_last_low_34'] = data.last2_low / data.last3_low
    data['open_last_low_34'] = data.last2_open / data.last3_low

    # k cross features 4,5
    data['close_last_close_45'] = data.last3_close / data.last4_close
    data['high_last_close_45'] = data.last3_high / data.last4_close
    data['low_last_close_45'] = data.last3_low / data.last4_close
    data['open_last_close_45'] = data.last3_open / data.last4_close
    data['close_last_open_45'] = data.last3_close / data.last4_open
    data['high_last_open_45'] = data.last3_high / data.last4_open
    data['low_last_open_45'] = data.last3_low / data.last4_open
    data['open_last_open_45'] = data.last3_open / data.last4_open
    data['close_last_high_45'] = data.last3_close / data.last4_high
    data['high_last_high_45'] = data.last3_high / data.last4_high
    data['low_last_high_45'] = data.last3_low / data.last4_high
    data['open_last_high_45'] = data.last3_open / data.last4_high
    data['close_last_low_45'] = data.last3_close / data.last4_low
    data['high_last_low_45'] = data.last3_high / data.last4_low
    data['low_last_low_45'] = data.last3_low / data.last4_low
    data['open_last_low_45'] = data.last3_open / data.last4_low

    # k cross features 1,3
    data['close_last_close_13'] = data.close / data.last2_close
    data['high_last_close_13'] = data.high / data.last2_close
    data['low_last_close_13'] = data.low / data.last2_close
    data['open_last_close_13'] = data.open / data.last2_close
    data['close_last_open_13'] = data.close / data.last2_open
    data['high_last_open_13'] = data.high / data.last2_open
    data['low_last_open_13'] = data.low / data.last2_open
    data['open_last_open_13'] = data.open / data.last2_open
    data['close_last_high_13'] = data.close / data.last2_high
    data['high_last_high_13'] = data.high / data.last2_high
    data['low_last_high_13'] = data.low / data.last2_high
    data['open_last_high_13'] = data.open / data.last2_high
    data['close_last_low_13'] = data.close / data.last2_low
    data['high_last_low_13'] = data.high / data.last2_low
    data['low_last_low_13'] = data.low / data.last2_low
    data['open_last_low_13'] = data.open / data.last2_low

    # k cross features 1,4
    data['close_last_close_13'] = data.close / data.last3_close
    data['high_last_close_13'] = data.high / data.last3_close
    data['low_last_close_13'] = data.low / data.last3_close
    data['open_last_close_13'] = data.open / data.last3_close
    data['close_last_open_13'] = data.close / data.last3_open
    data['high_last_open_13'] = data.high / data.last3_open
    data['low_last_open_13'] = data.low / data.last3_open
    data['open_last_open_13'] = data.open / data.last3_open
    data['close_last_high_13'] = data.close / data.last3_high
    data['high_last_high_13'] = data.high / data.last3_high
    data['low_last_high_13'] = data.low / data.last3_high
    data['open_last_high_13'] = data.open / data.last3_high
    data['close_last_low_13'] = data.close / data.last3_low
    data['high_last_low_13'] = data.high / data.last3_low
    data['low_last_low_13'] = data.low / data.last3_low
    data['open_last_low_13'] = data.open / data.last3_low

    # k cross features 1,5
    data['close_last_close_13'] = data.close / data.last4_close
    data['high_last_close_13'] = data.high / data.last4_close
    data['low_last_close_13'] = data.low / data.last4_close
    data['open_last_close_13'] = data.open / data.last4_close
    data['close_last_open_13'] = data.close / data.last4_open
    data['high_last_open_13'] = data.high / data.last4_open
    data['low_last_open_13'] = data.low / data.last4_open
    data['open_last_open_13'] = data.open / data.last4_open
    data['close_last_high_13'] = data.close / data.last4_high
    data['high_last_high_13'] = data.high / data.last4_high
    data['low_last_high_13'] = data.low / data.last4_high
    data['open_last_high_13'] = data.open / data.last4_high
    data['close_last_low_13'] = data.close / data.last4_low
    data['high_last_low_13'] = data.high / data.last4_low
    data['low_last_low_13'] = data.low / data.last4_low
    data['open_last_low_13'] = data.open / data.last4_low

    # k ma distance
    data['close_ma5'] = (data.close / data.ma5)
    data['last_close_ma5'] = (data.last_close / data.ma5_z)
    data['high_ma5'] = (data.high / data.ma5)
    data['last_high_ma5'] = (data.last_high / data.ma5_z)
    data['open_ma5'] = (data.open / data.ma5)
    data['last_open_ma5'] = (data.last_open / data.ma5_z)
    data['low_ma5'] = (data.low / data.ma5)
    data['lastlow_ma5'] = (data.last_low / data.ma5_z)

    data['last_Close_dt_ma5'] = data['last_close'] / data['ma5_z']
    data['last_Close_dt_ma10'] = data['last_close'] / data['ma10_z']
    data['last_Close_dt_ma20'] = data['last_close'] / data['ma20_z']
    data['last_Close_dt_ma30'] = data['last_close'] / data['ma30_z']
    data['last_Close_dt_ma60'] = data['last_close'] / data['ma60_z']

    data['last2_Close_dt_ma5'] = data['last2_close'] / data['ma5_z2']
    data['last2_Close_dt_ma10'] = data['last2_close'] / data['ma10_z2']
    data['last2_Close_dt_ma20'] = data['last2_close'] / data['ma20_z2']
    data['last2_Close_dt_ma30'] = data['last2_close'] / data['ma30_z2']
    data['last2_Close_dt_ma60'] = data['last2_close'] / data['ma60_z2']

    data['last3_Close_dt_ma5'] = data['last3_close'] / data['ma5_z3']
    data['last3_Close_dt_ma10'] = data['last3_close'] / data['ma10_z3']
    data['last3_Close_dt_ma20'] = data['last3_close'] / data['ma20_z3']
    data['last3_Close_dt_ma30'] = data['last3_close'] / data['ma30_z3']
    data['last3_Close_dt_ma60'] = data['last3_close'] / data['ma60_z3']

    data['last4_Close_dt_ma5'] = data['last4_close'] / data['ma5_z4']
    data['last4_Close_dt_ma10'] = data['last4_close'] / data['ma10_z4']
    data['last4_Close_dt_ma20'] = data['last4_close'] / data['ma20_z4']
    data['last4_Close_dt_ma30'] = data['last4_close'] / data['ma30_z4']
    data['last4_Close_dt_ma60'] = data['last4_close'] / data['ma60_z4']

    # 均线金叉 5 对于 10，20，30，60，120
    data['ma5_up_ma10'] = (data['ma5'] > data['ma10']) & (data['ma5_z'] < data['ma10_z'])
    data['ma5_up_ma20'] = (data['ma5'] > data['ma20']) & (data['ma5_z'] < data['ma20_z'])
    data['ma5_up_ma30'] = (data['ma5'] > data['ma30']) & (data['ma5_z'] < data['ma30_z'])
    data['ma5_up_ma60'] = (data['ma5'] > data['ma60']) & (data['ma5_z'] < data['ma60_z'])

    data['ma5_up_ma10_2'] = (data['ma5_z'] > data['ma10_z']) & (data['ma5_z2'] < data['ma10_z2'])
    data['ma5_up_ma20_2'] = (data['ma5_z'] > data['ma20_z']) & (data['ma5_z2'] < data['ma20_z2'])
    data['ma5_up_ma30_2'] = (data['ma5_z'] > data['ma30_z']) & (data['ma5_z2'] < data['ma30_z2'])
    data['ma5_up_ma60_2'] = (data['ma5_z'] > data['ma60_z']) & (data['ma5_z2'] < data['ma60_z2'])

    data['ma5_up_ma10_3'] = (data['ma5_z2'] > data['ma10_z2']) & (data['ma5_z3'] < data['ma10_z3'])
    data['ma5_up_ma20_3'] = (data['ma5_z2'] > data['ma20_z2']) & (data['ma5_z3'] < data['ma20_z3'])
    data['ma5_up_ma30_3'] = (data['ma5_z2'] > data['ma30_z2']) & (data['ma5_z3'] < data['ma30_z3'])
    data['ma5_up_ma60_3'] = (data['ma5_z2'] > data['ma60_z2']) & (data['ma5_z3'] < data['ma60_z3'])

    data['ma5_up_ma10_4'] = (data['ma5_z3'] > data['ma10_z3']) & (data['ma5_z4'] < data['ma10_z4'])
    data['ma5_up_ma20_4'] = (data['ma5_z3'] > data['ma20_z3']) & (data['ma5_z4'] < data['ma20_z4'])
    data['ma5_up_ma30_4'] = (data['ma5_z3'] > data['ma30_z3']) & (data['ma5_z4'] < data['ma30_z4'])
    data['ma5_up_ma60_4'] = (data['ma5_z3'] > data['ma60_z3']) & (data['ma5_z4'] < data['ma60_z4'])

    # 均线死叉 5 对于 10，20，30，60，120
    data['ma5_down_ma10'] = (data['ma5'] < data['ma10']) & (data['ma5_z'] > data['ma10_z'])
    data['ma5_down_ma20'] = (data['ma5'] < data['ma20']) & (data['ma5_z'] > data['ma20_z'])
    data['ma5_down_ma30'] = (data['ma5'] < data['ma30']) & (data['ma5_z'] > data['ma30_z'])
    data['ma5_down_ma60'] = (data['ma5'] < data['ma60']) & (data['ma5_z'] > data['ma60_z'])

    data['ma5_down_ma10_2'] = (data['ma5_z'] < data['ma10_z']) & (data['ma5_z2'] > data['ma10_z2'])
    data['ma5_down_ma20_2'] = (data['ma5_z'] < data['ma20_z']) & (data['ma5_z2'] > data['ma20_z2'])
    data['ma5_down_ma30_2'] = (data['ma5_z'] < data['ma30_z']) & (data['ma5_z2'] > data['ma30_z2'])
    data['ma5_down_ma60_2'] = (data['ma5_z'] < data['ma60_z']) & (data['ma5_z2'] > data['ma60_z2'])

    data['ma5_down_ma10_3'] = (data['ma5_z2'] < data['ma10_z2']) & (data['ma5_z3'] > data['ma10_z3'])
    data['ma5_down_ma20_3'] = (data['ma5_z2'] < data['ma20_z2']) & (data['ma5_z3'] > data['ma20_z3'])
    data['ma5_down_ma30_3'] = (data['ma5_z2'] < data['ma30_z2']) & (data['ma5_z3'] > data['ma30_z3'])
    data['ma5_down_ma60_3'] = (data['ma5_z2'] < data['ma60_z2']) & (data['ma5_z3'] > data['ma60_z3'])

    data['ma5_down_ma10_4'] = (data['ma5_z3'] < data['ma10_z3']) & (data['ma5_z4'] > data['ma10_z4'])
    data['ma5_down_ma20_4'] = (data['ma5_z3'] < data['ma20_z3']) & (data['ma5_z4'] > data['ma20_z4'])
    data['ma5_down_ma30_4'] = (data['ma5_z3'] < data['ma30_z3']) & (data['ma5_z4'] > data['ma30_z4'])
    data['ma5_down_ma60_4'] = (data['ma5_z3'] < data['ma60_z3']) & (data['ma5_z4'] > data['ma60_z4'])

    # k线金叉 5，10，20，30，60，120
    data['close_up_ma5'] = (data['close'] > data['ma5']) & (data['last_close'] < data['ma5_z'])
    data['close_up_ma10'] = (data['close'] > data['ma10']) & (data['last_close'] < data['ma10_z'])
    data['close_up_ma20'] = (data['close'] > data['ma20']) & (data['last_close'] < data['ma20_z'])
    data['close_up_ma30'] = (data['close'] > data['ma30']) & (data['last_close'] < data['ma30_z'])
    data['close_up_ma60'] = (data['close'] > data['ma60']) & (data['last_close'] < data['ma60_z'])

    # k线死叉 5，10，20，30，60，120
    data['close_down_ma5'] = (data['close'] < data['ma5']) & (data['last_close'] > data['ma5_z'])
    data['close_down_ma10'] = (data['close'] < data['ma10']) & (data['last_close'] > data['ma10_z'])
    data['close_down_ma20'] = (data['close'] < data['ma20']) & (data['last_close'] > data['ma20_z'])
    data['close_down_ma30'] = (data['close'] < data['ma30']) & (data['last_close'] > data['ma30_z'])
    data['close_down_ma60'] = (data['close'] < data['ma60']) & (data['last_close'] > data['ma60_z'])

    # k金叉均线数量
    data['number_close_up_mean'] = data['close_up_ma5'].astype('int') + data['close_up_ma10'].astype('int') + data[
        'close_up_ma20'].astype('int') + data[
                                       'close_up_ma30'].astype('int') + data['close_up_ma60'].astype('int')

    # k死叉均线数量
    data['number_close_down_mean'] = data['close_down_ma5'].astype('int') + data['close_down_ma10'].astype('int') + \
                                     data['close_down_ma20'].astype('int') + data[
                                         'close_down_ma30'].astype('int') + data['close_down_ma60'].astype('int')

    # data['close_last_close'] = data['close'] / data['last_close']

    # data.drop(['lowest_60', 'lowest_30', 'lowest_20', 'lowest_10', 'lowest_5', 'highest_5', 'highest_10', 'highest_20',
    #            'highest_30', 'highest_60', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'v_ma60', 'v_ma5', 'v_ma10',
    #            'v_ma20', 'ma5_z', 'ma10_z', 'ma20_z', 'ma30_z', 'ma60_z'], axis=1,
    #           inplace=True)

    return data


def n_MACD(data, short=12, long=26, mid=9):
    data['sema'] = EMA(list(data['close']), short)
    # data['sema'] = data['close']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'sema'] = (data.loc[i, 'close'] * 2 + data.loc[i + 1, 'sema'] * (short - 1)) / (short + 1)
    data['lema'] = EMA(list(data['close']), long)
    # data['lema'] = data['close']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'lema'] = (data.loc[i, 'close'] * 2 + data.loc[i + 1, 'lema'] * (long - 1)) / (long + 1)

    data['dif'] = data['sema'] - data['lema']
    data['dea'] = EMA(list(data['dif']), mid)
    # data['dea'] = data['dif']
    # for i in xrange(len(data) - 2, -1, -1):
    #     data.loc[i, 'dea'] = (data.loc[i, 'dif'] * 2 + data.loc[i + 1, 'dea'] * (mid - 1)) / (mid + 1)
    data['macd'] = 2 * (data['dif'] - data['dea'])

    data['dif_z'] = last_n(data, 1, 'dif')
    data['dea_z'] = last_n(data, 1, 'dea')
    data['macd_z'] = last_n(data, 1, 'macd')
    data['macd_q'] = last_n(data, 2, 'macd')

    # diff 上穿0
    data['diff_up_cross_0'] = (data['dif'] > 0) & (data['dif_z'] < 0)
    # diff 下穿0
    data['diff_down_cross_0'] = (data['dif'] < 0) & (data['dif_z'] > 0)
    # dea 上穿0
    data['dea_up_cross_0'] = (data['dea'] > 0) & (data['dea_z'] < 0)
    # dea 下穿0
    data['dea_down_cross_0'] = (data['dea'] < 0) & (data['dea_z'] > 0)
    # diff 上穿 dea
    data['diff_up_cross_dea'] = (data['dif'] > data['dea']) & (data['dif_z'] < data['dea_z'])
    # diff 下穿 dea
    data['diff_down_cross_dea'] = (data['dif'] < data['dea']) & (data['dif_z'] > data['dea_z'])
    # macd 大于 昨日macd,昨日 macd 小于前日macd，diff 大于 0 ，macd 小于0
    data['macd_over_last_macd'] = (data['macd'] > data['macd_z']) & (data['macd_z'] < data['macd_q']) & (
    data['dif'] > 0) & (data['macd'] < 0)
    data = data[::-1]
    data['macd_60_up_sum'] = data[data['macd_z'] > 0]['macd_z'].rolling(window=60).max()
    data['macd_30_up_sum'] = data[data['macd_z'] > 0]['macd_z'].rolling(window=30).max()
    data['macd_10_up_sum'] = data[data['macd_z'] > 0]['macd_z'].rolling(window=10).max()
    data['macd_5_up_sum'] = data[data['macd_z'] > 0]['macd_z'].rolling(window=5).max()
    data['macd_60_down_sum'] = abs(data[data['macd_z'] < 0]['macd_z'].rolling(window=60).min())
    data['macd_30_down_sum'] = abs(data[data['macd_z'] < 0]['macd_z'].rolling(window=30).min())
    data['macd_10_down_sum'] = abs(data[data['macd_z'] < 0]['macd_z'].rolling(window=10).min())
    data['macd_5_down_sum'] = abs(data[data['macd_z'] < 0]['macd_z'].rolling(window=5).min())
    data = data[::-1]
    data['macd_5_10_up'] = data['macd_5_up_sum'] / data['macd_10_up_sum']
    data['macd_5_30_up'] = data['macd_5_up_sum'] / data['macd_30_up_sum']
    data['macd_5_60_up'] = data['macd_5_up_sum'] / data['macd_60_up_sum']

    data['macd_5_10_down'] = data['macd_5_down_sum'] / data['macd_10_down_sum']
    data['macd_5_30_down'] = data['macd_5_down_sum'] / data['macd_30_down_sum']
    data['macd_5_60_down'] = data['macd_5_down_sum'] / data['macd_60_down_sum']

    # data.drop(['sema', 'lema', 'dif', 'macd', 'dea', 'dif_z', 'dea_z', 'macd_z', 'macd_q','macd_60_up_sum','macd_30_up_sum','macd_10_up_sum','macd_5_up_sum' \
    #               , 'macd_60_down_sum', 'macd_30_down_sum', 'macd_10_down_sum', 'macd_5_down_sum'], axis=1, inplace=True)
    data.fillna(0, inplace=True)
    return data


def n_DMI(data, N1=14, M1=6):
    data['MTR_D1'] = data['high'] - data['low']
    data['MTR_D2'] = abs(data['high'] - data.last_close)
    data['MTR_D3'] = abs(data.last_close - data['low'])
    data['MTR_1'] = data['MTR_D2']
    data.loc[data['MTR_D1'] > data['MTR_D2'], 'MTR_1'] = data['MTR_D1']
    # data['MTR_1'] = data.apply(lambda x: x['MTR_D1'] if x['MTR_D1'] > x['MTR_D2']  else x['MTR_D2'], axis=1)

    # 要删除的第一个属性
    data['MTR_2'] = data['MTR_D3']
    data.loc[data['MTR_1'] > data['MTR_D3'], 'MTR_2'] = data['MTR_1']
    # data['MTR_2'] = data.apply(lambda x: x['MTR_1'] if x['MTR_1'] > x['MTR_D3']  else x['MTR_D3'], axis=1)

    # roolling 必须依赖于 transform 才行，只能是先生成一列，然后在抛弃
    # roolling 操作要先进行反转才能。因为rolling操作会空前N行
    data = data[::-1]

    data['MTR'] = data['MTR_2'].rolling(window=N1).sum()

    data['HD'] = data['high'] - data.last_high
    data['LD'] = data.last_low - data['low']

    # HD1 = np.where(HD <= 0, 0, HD)
    # data['DMP1'] = np.where(HD1 <= LD, 0, HD1)
    data['DMP1'] = 0
    data.loc[(data['HD'] > 0) & (data['HD'] > data['LD']), 'DMP1'] = data['HD']

    data['DMP'] = data['DMP1'].rolling(window=N1).sum()

    # LD1 = np.where(LD <= 0, 0, LD)
    # data['DMM1'] = np.where(LD1 <= HD, 0, LD1)
    data['DMM1'] = 0
    data.loc[(data['LD'] > 0) & (data['LD'] > data['HD']), 'DMM1'] = data['LD']

    data['DMM'] = data['DMM1'].rolling(window=N1).sum()

    data['PDI'] = data['DMP'] * 100 / data['MTR']
    data['MDI'] = data['DMM'] * 100 / data['MTR']

    # 要删除的第4个属性
    data['ADX1'] = abs(data['MDI'] - data['PDI']) / (data['MDI'] + data['PDI']) * 100

    data['ADX'] = data['ADX1'].rolling(window=M1).mean()
    data = data[::-1]

    data['PDI_z'] = last_n(data, 1, 'PDI')
    data['MDI_z'] = last_n(data, 1, 'MDI')
    data['ADX_z'] = last_n(data, 1, 'ADX')

    data = cross(data, 'PDI_z', 'MDI_z', 'PDI', 'MDI', 'PDI_MDI_UP', 'PDI_MDI_DOWN')

    data['ADX_50_DOWN'] = (data.ADX < 50) & (50 < data.ADX_z)
    data['ADX_50_UP'] = (data.ADX > 50) & (50 > data.ADX_z)

    # data.drop(
    #     ['MTR_2', 'MTR', 'HD', 'LD', 'MTR_D1', 'MTR_D2', 'MTR_1', 'MTR_D3', 'DMP1', 'DMP', 'DMM', 'DMM1', 'ADX1', 'PDI',
    #      'MDI', 'ADX', 'PDI_z', 'MDI_z', 'ADX_z'],
    #     axis=1, inplace=True)
    data.fillna(0, inplace=True)
    return data


def n_BRAR(data, N1=1):
    data['sum1'] = 0
    data.loc[data['high'] > data['last_close'], 'sum1'] = data['high'] - data['last_close']
    data['sum2'] = 0
    data.loc[data['last_close'] > data['low'], 'sum2'] = data['last_close'] - data['low']

    data['sum3'] = data['high'] - data['open']
    data['sum4'] = data['open'] - data['low']

    revers_data = data[::-1]
    revers_data['sum1'] = revers_data['sum1'].rolling(window=N1).sum()
    revers_data['sum2'] = revers_data['sum2'].rolling(window=N1).sum()
    revers_data['sum3'] = revers_data['sum3'].rolling(window=N1).sum()
    revers_data['sum4'] = revers_data['sum4'].rolling(window=N1).sum()
    data = revers_data[::-1]

    data['BR'] = data['sum1'] / data['sum2'] * 100
    data['AR'] = data['sum3'] / data['sum4'] * 100

    data['BR_z'] = last_n(data, 1, 'BR')
    data['AR_z'] = last_n(data, 1, 'AR')

    data = cross(data, 'BR_z', 'AR_z', 'BR', 'AR', 'BR_AR_UP', 'BR_AR_DOWN')
    data['AR_50_DOWN'] = (data.AR < 50) & (50 < data.AR_z)
    data['AR_50_UP'] = (data.AR_z < 50) & (50 < data.AR)

    # data.drop(['sum1', 'sum2', 'sum3', 'sum4', 'BR_z', 'AR_z', 'BR', 'AR'], axis=1, inplace=True)
    data.fillna(0, inplace=True)
    return data


def n_CR(data, n, m1, m2, m3):
    # data['last_high'] = last_n(data, 1, col_name='high')
    # data['last_low'] = last_n(data, 1, col_name='low')
    # data.fillna(0, inplace=True)
    data = data[::-1]

    data['mid'] = (data.last_high + data.last_low) / 2
    data['max'] = 0
    data.loc[data.high > data.mid, 'max'] = data.high - data.mid
    data['max2'] = 0
    data.loc[data.mid > data.low, 'max2'] = data.mid - data.low

    data['CR'] = data['max'].rolling(window=n).sum() / data.max2.rolling(window=n).sum() * 100
    data['m1'] = data.CR.rolling(window=m1).mean()
    data['m2'] = data.CR.rolling(window=m2).mean()
    data['m3'] = data.CR.rolling(window=m3).mean()
    data = data[::-1]

    data['MA1'] = last_n(data, int(m1 / 2.5 + 1), col_name='m1')
    data['MA2'] = last_n(data, int(m2 / 2.5 + 1), col_name='m2')
    data['MA3'] = last_n(data, int(m3 / 2.5 + 1), col_name='m3')

    data['CR_z'] = last_n(data, 1, 'CR')
    data['MA1_z'] = last_n(data, 1, 'MA1')
    data['MA2_z'] = last_n(data, 1, 'MA2')
    data['MA3_z'] = last_n(data, 1, 'MA3')

    data = cross(data, 'CR_z', 'MA1_z', 'CR', 'MA1', 'CR_MA1_UP', 'CR_MA1_DOWN')
    data = cross(data, 'CR_z', 'MA2_z', 'CR', 'MA2', 'CR_MA2_UP', 'CR_MA2_DOWN')
    data = cross(data, 'CR_z', 'MA3_z', 'CR', 'MA3', 'CR_MA3_UP', 'CR_MA3_DOWN')
    data['CR_40_DOWN'] = (data.CR < 40) & (40 < data.CR_z)
    data['CR_40_UP'] = (data.CR_z < 40) & (40 < data.CR)

    # data.drop(['mid', 'max', 'max2', 'm1', 'm2', 'm3', 'CR', 'MA1', 'MA2', 'MA3', 'CR_z', 'MA1_z', 'MA2_z', 'MA3_z'],
    #           axis=1, inplace=True)
    data.fillna(0, inplace=True)
    return data


def n_VR(data, n):
    data = data[::-1]
    data['TH_1'] = 0
    data.loc[data.close > data.last_close, 'TH_1'] = data.volume
    data['TH'] = data.TH_1.rolling(window=n).sum()
    data['TL_1'] = 0
    data.loc[data.close < data.last_close, 'TL_1'] = data.volume
    data['TL'] = data.TL_1.rolling(window=n).sum()
    data['TQ_1'] = 0
    data.loc[data.close == data.last_close, 'TQ_1'] = data.volume
    data['TQ'] = data.TQ_1.rolling(window=n).sum()
    data['VR'] = 100 * (data.TH * 2 + data.TQ) / (data.TL * 2 + data.TQ)
    data.fillna(0, inplace=True)
    data = data[::-1]
    data['VR_40_DOWN'] = data.VR < 40
    data['VR_40_70'] = (40 < data.VR) & (data.VR < 70)
    data['VR_80_150'] = (80 < data.VR) & (data.VR < 150)
    data['VR_160_450'] = (160 < data.VR) & (data.VR < 450)
    data['VR_450_UP'] = 450 < data.VR

    # data.drop(['TH_1', 'TH', 'TL_1', 'TL', 'TQ_1', 'TQ', 'VR'], axis=1, inplace=True)
    return data


def n_WR(data, n, n1):
    data = data[::-1]
    data['WR1'] = 100 * (data.high.rolling(window=n).max() - data.close) / (
        data.high.rolling(window=n).max() - data.low.rolling(window=n).min())
    data['WR2'] = 100 * (data.high.rolling(window=n1).max() - data.close) / (
        data.high.rolling(window=n1).max() - data.low.rolling(window=n1).min())
    data = data[::-1]

    data['WR1_z'] = last_n(data, 1, 'WR1')
    data['WR2_z'] = last_n(data, 1, 'WR2')

    data['WR1_15_DOWN'] = data.WR1 < 15
    data['WR1_85_UP'] = 85 < data.WR1
    data['WR1_50_UP'] = (data.WR1_z < 50) & (50 < data.WR1)
    data['WR1_50_DOWN'] = (data.WR1 < 50) & (50 < data.WR1_z)
    data = cross(data, 'WR1_z', 'WR2_z', 'WR1', 'WR2', 'WR1_WR2_UP', 'WR1_WR2_DOWN')
    data['WR1_20_UP'] = (data.WR1_z < 20) & (20 < data.WR1)
    data['WR1_80_DOWN'] = (data.WR1 < 80) & (80 < data.WR1_z)

    # data.drop(['WR1', 'WR2', 'WR1_z', 'WR2_z'], axis=1, inplace=True)
    data.fillna(0, inplace=True)

    return data


def n_CCI(data, n):
    data = data[::-1]
    data['TYP'] = (data.high + data.low + data.close) / 3
    data['TYP_mean'] = data.TYP.rolling(window=n).mean()
    data = data[::-1]
    data['CCI'] = cci_helper(list(data['TYP']), list(data['TYP_mean']), n)
    data['CCI_z'] = last_n(data, 1, 'CCI')

    data['CCI_-100_UP'] = (data.CCI_z < -100) & (-100 < data.CCI)
    data['CCI_100_DOWN'] = (data.CCI_z < 100) & (100 < data.CCI)

    # data.drop(['TYP', 'CCI', 'CCI_z'], axis=1, inplace=True)
    data.fillna(0, inplace=True)
    return data


def n_PSY(data, n):
    data = data[::-1]
    data['PSY_1'] = data.close > data.last_close
    data['PSY'] = data.PSY_1.rolling(window=n).sum() / n * 100
    data = data[::-1]
    data['PSY_z'] = last_n(data, 1, 'PSY')

    data['PSY_90_UP'] = 90 < data.PSY
    data['PSY_10_DOWN'] = data.PSY < 10

    # data.drop(['PSY_1', 'PSY', 'PSY_z'], axis=1, inplace=True)

    data.fillna(0, inplace=True)
    return data


def n_BOLL(data, m):
    data = data[::-1]
    data['BOLL'] = data.close.rolling(window=m).mean()
    data['std'] = data.close.rolling(window=m).std()
    data['UB'] = data.BOLL + 2 * data['std']
    data['LB'] = data.BOLL - 2 * data['std']
    data = data[::-1]

    data['UB_z'] = last_n(data, 1, 'UB')
    data['LB_z'] = last_n(data, 1, 'LB')
    data['std_z'] = last_n(data, 1, 'std')

    data['close_UB_UP'] = (data.last_close < data.UB_z) & (data.close > data.UB)
    data['close_LB_DOWN'] = (data.last_close > data.LB_z) & (data.close < data.LB)
    data['std_std_z_UP'] = data['std'] > data.std_z
    data['std_std_z_DOWN'] = data['std'] < data.std_z

    # data.drop(['BOLL', 'std', 'UB', 'LB', 'std_z', 'UB_z', 'LB_z'], axis=1, inplace=True)

    data.fillna(0, inplace=True)
    return data

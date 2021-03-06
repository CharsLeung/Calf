# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/7/3 15:19
"""
import time
import datetime as dt
import requests
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr


class WebData():
    @classmethod
    def yahoo_stock_data(cls, stock_code, start_date, end_date):
        """

        :param end_date: a datetime
        :param start_date: a datetime
        :param stock_code: symbol like yahoo style
        :return:
        """
        start_date = int(time.mktime(start_date.timetuple()))
        end_date = int(time.mktime(end_date.timetuple()))
        stock_code = stock_code.strip()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.181 Safari/537.36',
            'referer': 'https://finance.yahoo.com',
            'origin': 'https://finance.yahoo.com',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'B=fju5rp9cqcptr&b=3&s=n1; GUCS=AR6HuGsH; '
                      'GUC=AQEBAQFbMfpcGkIjGgUj&s=AQAAAKg7Svm0&g=WzCx-g'
        }
        r = requests.get(
            'https://query1.finance.yahoo.com/v7/finance/download/{0}?'
            'period1={1}&period2={2}&interval=1d&events=history&crumb=mOI10jFT7Ye'.
                format(stock_code, start_date, end_date),
            stream=True, headers=headers)
        # with open(r'{}.csv'.format(stock_code), 'wb') as f:
        #     for chunk in r.iter_content(chunk_size=1024):
        #         if chunk:
        #             f.write(chunk)
        # print(stock_code) if len(a) else nan
        rsl = ''
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                rsl += str(chunk, encoding='utf-8')
        rsl = rsl.split('\n')
        if len(rsl) > 1:
            columns = rsl[0].split(',')
            data = rsl[1:]
            # nan = list(np.nan for i in range(len(columns)))
            data = list(a.split(',') for a in data)
            data = pd.DataFrame(data, columns=columns)
            data.dropna(axis=0, inplace=True)
            data.drop(['Adj Close'], axis=1, inplace=True)
            data = data.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high',
                                        'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
            data.replace('null', np.nan, inplace=True)
            data.dropna(axis=0, inplace=True)
            data['open'] = data.open.astype('float32')
            data['close'] = data.close.astype('float32')
            data['high'] = data.high.astype('float32')
            data['low'] = data.low.astype('float32')
            data['volume'] = data.volume.astype('int64')
            data['amount'] = 0
            data['stock_code'] = stock_code
            data['date'] = pd.to_datetime(data.date)
            return data
        return pd.DataFrame([], columns=['stock_code', 'date', 'open', 'close',
                                         'low', 'high', 'amount', 'volume'])

    @classmethod
    def Stooq_index_data(cls, code):
        """

        :return:
        """
        try:
            data = pdr.DataReader('^' + code, 'stooq')
            if len(data):
                data['date'] = data.index
                data['amount'] = 0
                data['stock_code'] = code
                data = data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low',
                                            'Close': 'close', 'Volume': 'volume'})
                data.fillna(0, inplace=True)
                data = data.reset_index(drop=True)
                return data
            else:
                return None
        except Exception as e:
            print(e)
            return None

    @classmethod
    def IEX_data(cls, code):
        start = dt.datetime(2018, 2, 9)
        end = dt.datetime(2018, 7, 6)
        f = pdr.DataReader('000001', 'iex', start, end)
        print(f.head())

    @classmethod
    def get_capital_flow_hs_a(cls):
        try:
            data = requests.get('http://ff.eastmoney.com/EM_CapitalFlowInterf'
                                'ace/api/js?id=ls&type=ff&check=MLBMS&cb=var%20'
                                'aff_data=&js={(x)}&rtntype=3&acces_token=1942f'
                                '5da9b46b069953c873404aad4b5&_=1542089930344')
            data = data.text
            data = data.split('=')[1]
            data = eval(data)
            data['xa'] = data['xa'].split(',')
            data['xa'] = data['xa'][0:-1]
            data = pd.DataFrame(data)
            data['ya'] = data.ya.map(lambda x: x.split(','))
            data['small'] = data.ya.map(lambda x: x[4])
            data['big'] = data.ya.map(lambda x: x[2])
            data['super_big'] = data.ya.map(lambda x: x[1])
            data['mid'] = data.ya.map(lambda x: x[3])
            data['main'] = data.ya.map(lambda x: x[0])
            data.drop(['ya'], axis=1, inplace=True)
            data = data.rename(columns={'xa': 'date'})
            data = data.replace('', np.NaN).dropna()
            _ = 'float'
            data = data.astype({'small': _, 'big': _, 'super_big': _, 'mid': _, 'main': _})
            # print(data)
            return data

        except Exception as e:
            print(e)
            return None

    @classmethod
    def get_capital_flow_hk(cls, direction='north'):
        try:
            data = requests.get(url='http://ff.eastmoney.com/EM_CapitalF'
                                    'lowInterface/api/js?id=' + direction +
                                    '&type=EFR&rtntype=2&acces_token=1942f5d'
                                    'a9b46b069953c873404aad4b5&js=var%20zhbO'
                                    'snorth=({data:[(x)]})')
            data = data.text
            data = data.split('=')[1].replace('(', '').replace(')', '').replace('data', '"data"')
            data = eval(data)
            data = pd.DataFrame({'ya': data['data']})
            data['ya'] = data.ya.map(lambda x: x.split(','))
            data['date'] = data.ya.map(lambda x: x[0])
            data['H'] = data.ya.map(lambda x: x[1])
            data['S'] = data.ya.map(lambda x: x[2])
            data['H_l'] = data.ya.map(lambda x: x[3])
            data['S_l'] = data.ya.map(lambda x: x[4])  # 深市剩余资金
            data = data.replace('', np.NaN).dropna()
            _ = 'float'
            data = data.astype({'S': _, 'H': _, 'H_l': _, 'S_l': _})
            data['money'] = data.H + data.S
            data = data.drop(['ya'], axis=1)
            return data
        except Exception as e:
            print(e)
            return None

pass
# t = dt.datetime.today()
# sd = dt.datetime(2018, 6, 1)
# ed = dt.datetime(2018, 7, 3)
#
# sd = int(time.mktime(sd.timetuple()))
# ed = int(time.mktime(ed.timetuple()))
# d = WebData.yahoo_stock_data('SBIN.BO', sd, ed)
# print(d.head())
# WebData.IEX_data('')
# d = WebData.get_capital_flow_hs_a()
# d = WebData.get_capital_flow_hk()
pass


# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2017/12/26 9:43
"""
import datetime as dt
import pandas as pd
from urllib.request import urlopen
from pandas_datareader import data as pdr
from Calf.exception import warning, ExceptionInfo


class RealData:
    """
    从各个行情服务器读取实时数据
    """
    # 新浪A股返回的数据结构
    columns = {0: 'stock_name', 1: 'open', 2: 'last_close', 3: 'price', 4: 'high',
               5: 'low', 6: 'buy_', 7: 'sell_', 8: 'volume', 9: 'amount',
               10: 'B1V', 11: 'B1', 12: 'B2V', 13: 'B2', 14: 'B3V', 15: 'B3',
               16: 'B4V', 17: 'B4', 18: 'B5V', 19: 'B5', 20: 'S1V',
               21: 'S1', 22: 'S2V', 23: 'S2', 24: 'S3V', 25: 'S3', 26: 'S4V', 27: 'S4',
               28: 'S5V', 29: 'S5', 30: 'datetime', 31: 'time'}

    @classmethod
    def market_judge(cls, stock_code):
        """
        根据股票的代码判断其所属市场，并返回带市场标示前缀的股票代码
        :param stock_code:
        :return:
        """
        if stock_code[0:1] == '6':
            stock_code = 'sh' + stock_code
        else:
            stock_code = 'sz' + stock_code
        return stock_code

    @classmethod
    def get_stock_data(cls, stock_code):
        """
        读取一止股票的实时数据
        :param stock_code:
        :return:
        """
        _code = RealData.market_judge(stock_code)
        html = urlopen('http://hq.sinajs.cn/list={}'.format(_code)).read()
        data_l = html.decode('gbk').split('\n')
        i = 0
        res = dict()
        for data in data_l:
            if len(data):
                d = data.split('="')
                key = stock_code
                i = i + 1
                res[key] = d[1][:-2].split(',')

        # print(res, len(res['601088']))
        return res

    @classmethod
    def get_stocks_data(cls, stocks_code):
        """
        根据所给的股票代码列表，从新浪接口读取实时数据并打包成一个df
        注意：在交易时间之外价格数据可能不符合实际
        :param stocks_code:
        :return:
        """
        try:
            _codes = ['sh' + c if c[0:1] == '6' else 'sz' + c for c in stocks_code]
            # _codes = [RealData.market_judge(x) for x in stocks_code]
            _codes = ','.join(_codes)
            html = urlopen('http://hq.sinajs.cn/list={}'.format(_codes)).read()
            data_l = html.decode('gbk').split('\n')
            i = 0
            res = dict()
            for data in data_l:
                if len(data):
                    d = data.split('="')
                    key = stocks_code[i]
                    i += 1
                    res[key] = d[1][:-2].split(',')
            data = pd.DataFrame(res).T
            data[30] = data[30] + ' ' + data[31]
            data = data.rename(columns=RealData.columns)
            data['datetime'] = pd.to_datetime(data.datetime)
            data['stock_code'] = data.index
            _ = 'float'
            dtypes = dict(open=_, last_close=_, price=_, high=_, low=_,
                          buy_=_, sell_=_, volume=_, amount=_,
                          B1=_, B2=_, B3=_, B4=_, B5=_,
                          S1=_, S2=_, S3=_, S4=_, S5=_,
                          B1V=_, B2V=_, B3V=_, B4V=_, B5V=_,
                          S1V=_, S2V=_, S3V=_, S4V=_, S5V=_, )
            data = data.astype(dtypes)
            _ = 2
            data = data.round(dict(B1=_, B2=_, B3=_, B4=_, B5=_,
                                   S1=_, S2=_, S3=_, S4=_, S5=_,
                                   open=_, last_close=_, price=_, high=_, low=_,))
            data = data.reset_index(drop=True)
            # print(data.T)
            return data
        except Exception as e:
            print(e)
            return None

    @classmethod
    def get_index_data(cls, index_code):
        """
        获取A股某大盘指数的实时数据
        :param index_code:
        :return:
        """
        try:
            if isinstance(index_code, str):
                _code = 's_sh' + index_code if index_code[0:1] == '0' else 's_sz' + index_code
            elif isinstance(index_code, list):
                _code = ['s_sh' + c if c[0:1] == '0' else 's_sz' + c for c in index_code]
                _code = ','.join(_code)
            else:
                raise TypeError('This stock code type must in (str, list)')
            html = urlopen('http://hq.sinajs.cn/list={}'.format(_code)).read()
            datas = html.decode('gbk').split('\n')
            res = []
            for data in datas:
                if len(data):
                    d = data.split('=')
                    _ = [d[0][-6::]] + d[1][1:len(d[1]) - 2].split(',')
                    res.append(_)
            res = pd.DataFrame(res, columns=['code', 'name', 'price', 'delta',
                                             'R', 'volume', 'amount'])
            res = res.astype(dict(price='float', delta='float', R='float',
                                  volume='float', amount='float'))
            # print(res, len(res['601088']))
            return res
        except Exception as e:
            ExceptionInfo(e)
            return None

    @classmethod
    def yahoo_stock_data(cls, stock_code, start_date, end_date):
        """

        :param stock_code:
        :return:
        """
        # sc = sc.strip()
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        #                   'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        #     'referer': 'https://finance.yahoo.com',
        #     'origin': 'https://finance.yahoo.com',
        #     'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept-language': 'zh-CN,zh;q=0.9',
        #     'cookie': 'B=fju5rp9cqcptr&b=3&s=n1; GUCS=AR6HuGsH; '
        #               'GUC=AQEBAQFbMfpcGkIjGgUj&s=AQAAAKg7Svm0&g=WzCx-g'
        # }
        # r = requests.get(
        #     'https://query1.finance.yahoo.com/v7/finance/download/{0}?'
        #     'period1={1}&period2={2}&interval=1d&events=history&crumb=mOI10jFT7Ye'.
        #         format(stock_code, start_date, end_date),
        #     stream=True, headers=headers)
        # with open(r'{}.csv'.format(stock_code), 'wb') as f:
        #     for chunk in r.iter_content(chunk_size=1024):
        #         if chunk:
        #             f.write(chunk)
        # print(stock_code)

    @classmethod
    def usa_stock_data(cls, stock_code):
        """
        获取美股的实时数据
        :param stock_code:
        :return:
        """
        try:
            data = pdr.DataReader(stock_code, 'iex-last')
            data = data.T
            if len(data) > 1:
                data = data.T
            elif len(data) == 1:
                pass
            else:
                return None
            data = data.rename(columns={'symbol': 'stock_code', 'time': 'datetime'})
            data['datetime'] = pd.to_datetime(data.datetime, unit='ms', utc=True)
            data['datetime'] = data.datetime + pd.Timedelta(hours=-4)
            data['datetime'] = data.datetime.map(lambda d: d.replace(tzinfo=None))
            return data
        except Exception as e:
            print(e)
            return None

    @classmethod
    def hk_stock_data(cls, stock_code):
        try:
            if isinstance(stock_code, str):
                _code = 'hk' + stock_code
                stock_code = [stock_code]
            elif isinstance(stock_code, list):
                _code = ['hk' + c for c in stock_code]
                _code = ','.join(_code)
            else:
                raise TypeError('This stock code type must in (str, list)')
            html = urlopen('http://hq.sinajs.cn/list={}'.format(_code)).read()
            data_l = html.decode('gbk').split('\n')
            i = 0
            res = dict()
            for data in data_l:
                if len(data):
                    d = data.split('="')
                    key = stock_code[i]
                    res[i] = [stock_code[i]] + d[1][:-2].split(',')
                    i += 1
            data = pd.DataFrame(res).T
            data[18] = data[18] + ' ' + data[19]
            data = data.loc[:, [0, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 18]]
            columns = {0: 'stock_code', 2: 'stock_name', 3: 'open', 4: 'last_close',
                       5: 'price', 6: 'low', 7: 'high', 9: 'gains', 10: 'B1', 11: 'S1',
                       12: 'amount', 13: 'volume', 18: 'datetime'}
            data = data.rename(columns=columns)
            data['datetime'] = pd.to_datetime(data.datetime)
            # data['stock_code'] = data.index
            # print(data.T)
            return data
        except Exception as e:
            ExceptionInfo(e)
            return None

    @classmethod
    def Stooq_index_data(cls):
        """

        :return:
        """
        data = pdr.DataReader('^SPX', 'stooq', start=dt.datetime(2018, 4, 1))
        print(data)


pass
# print(RealData.get_index_data('000300'))
# realdata.get_stocks_data(['601088', '002427'])
# RealData.yahoo_stock_data('aa')
# print(RealData.hk_stock_data(['00981', '00006']))
# RealData.Stooq_index_data()
# t = datetime.today()
# end_date = datetime(t.year, t.month, t.day, 4)
# ed = int(time.mktime(end_date.timetuple()))
# RealData.yahoo_stock_data('DJI', '')

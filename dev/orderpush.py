# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/11/2 17:07
"""
import json
import pandas as pd
import datetime as dt
import pytz
from Calf.exception import ExceptionInfo, WarningMessage
from net import notice, MODEL_ORDER_ACTION, TASK_CODE
from utils import trading, fontcolor
from verification import reason
from .realkit import RealKit as rk


class Console:

    @classmethod
    def A_is_not_trade_day(cls):
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        print(fontcolor.F_RED, '时间：', dt.datetime.now(),
              '备注：A股休市.', fontcolor.END)
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)

    @classmethod
    def HSHCN_is_not_trade_day(cls):
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        print(fontcolor.F_RED, '时间：', dt.datetime.now(),
              '备注：沪、深港通(北向休市)', fontcolor.END)
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)

    @classmethod
    def HK_is_not_trade_day(cls):
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        print(fontcolor.F_RED, '时间：', dt.datetime.now(),
              '备注：港股休市.', fontcolor.END)
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)

    @classmethod
    def HSHCS_is_not_trade_day(cls):
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        print(fontcolor.F_RED, '时间：', dt.datetime.now(),
              '备注：沪、深港通(南向休市)', fontcolor.END)
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)

    @classmethod
    def no_asset_or_client(cls):
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        print(fontcolor.F_RED, '时间：', dt.datetime.now(),
              '备注：未能查询到客户资产(asset)、有效的策略订阅(client)信息.',
              fontcolor.END)
        print(fontcolor.F_RED + '=' * 80 + fontcolor.END)


class OrderPush(object):
    """
        真实的信号推荐。
        在一个订单中包含了几个用于标识业务逻辑的字段：
        status：用于标记订单的买卖状态的字段，这个字段
        只能又交易端更改，status=0 -> 未开仓
        status=1 -> 已开仓， status=2 ->  已平仓
        RV：Rr权值回收的阶级，RV=0 -> 为进行任何回收，
        RV=1 -> 未开仓回收，　RV=2 -> 开仓回收，
        RV=3 -> 平仓回收，平仓回收即为RV的回收终态
        """

    # order_action_xx系列函数需要读取本地（默认）数据库的asset、client表
    # 确保在指定的时间（point）有数据
    # 最终将合适的order插入到orders表中

    @classmethod
    def order_action_zh(cls, model_from, data, point=None, market=None):
        """
        为已接受托管的账户推荐信号，按’因户推送‘的原则推送，
        :param market: 通过何种方式交易，即是通过国内平台，还是沪、深港通
        :param point:
        :param model_from:模型策略的名称
        :param data:model_from策略的信号数据
        :return:
        """
        # TODO(leung jain): 当前买卖A股要么通过沪、深港通，要么通过国内的平台

        tdy = dt.date.today() if point is None else point
        tdy = dt.datetime(tdy.year, tdy.month, tdy.day)
        # data['date'] = tdy
        if market is None:
            # 默认国内平台
            if trading().is_trade_day(tdy) is not True:
                Console.A_is_not_trade_day()
                return pd.DataFrame()
            pass
        else:
            if market in ['HSHCN']:  # 当前使用沪、深港通
                if trading(market=market).is_trade_day(tdy) is not True:
                    Console.HSHCN_is_not_trade_day()
                    return pd.DataFrame()
        order_filed = ['type', 'open_date', 'open_price', 'confidence', 'model_from']
        if set(order_filed) <= set(data.columns):
            pass
        else:
            raise Exception('this orders lost must field')

        from Calf.data import OrderData as od
        ais = od.read_account_info(model_from=model_from, date=tdy)
        cli = od.read_client_info(model_from=model_from, status=1)
        if len(ais) == 0 or len(cli) == 0:
            Console.no_asset_or_client()
            return pd.DataFrame()
        ais = pd.merge(ais, cli, on=['client_no', 'model_from'])
        ais.dropna(axis=1, inplace=True)
        goods = pd.DataFrame()
        if len(ais):
            # 有账户订阅这个策略
            # op = cls.order_param_load(model_from)
            for i, r in ais.iterrows():
                # 为X账户推荐信号
                '''X账户已持有的来自于model_from策略的记录'''
                orders = od.read_orders(
                    model_from=model_from, client_no=r.client_no, status=1
                )
                sgls = data.copy(deep=True)  #
                if len(orders):
                    '''X账户已经持有新推荐的信号，将这些排除在外'''
                    same = list(data[data.stock_code.isin(orders.stock_code)].index)
                    sgls.drop(same, axis=0, inplace=True)
                    # sgls = sgls.reset_index()
                if len(sgls) == 0:
                    '''没有可以向X推荐的信号'''
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    print(fontcolor.F_RED + '# 策略' + model_from +
                          '推荐记录 #' + fontcolor.END)
                    print(fontcolor.F_RED + '账户：' + r.client_no, fontcolor.END)
                    print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                          '备注：没有找到可以推荐的信号：', fontcolor.END)
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    continue
                '''X账户还可以买入的比例，这个比例是针对于这个策略的'''
                Ar = r['Rr']
                if Ar > 0:
                    aRr = 1 / r['max_pst_vol']  # 策略标准单信号买入比例
                    if r['max_pst_vol'] <= len(orders):
                        # 还有钱，但仓位数量已占满
                        '''增加仓位'''
                        # need_ = Ar // aRr
                        # need_ = need_ + 1 if Ar % aRr != 0 else need_
                        # br = Ar / need_
                        need_ = 0
                        br = 0
                        remarks = '账户余额充足，仓位不足'
                    else:
                        need_ = (r['max_pst_vol'] - len(orders))  # 剩余仓位
                        br = Ar / need_
                        br = aRr if br > aRr else br
                        remarks = '账户余额充足，按正常水平补填仓位'
                else:
                    need_ = 0
                    br = 0
                    remarks = '账户余额不足，无新信号推荐'
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
                print(fontcolor.F_GREEN + '# 策略' + model_from +
                      '推荐记录 #' + fontcolor.END)
                print(fontcolor.F_GREEN + '账户：', r.client_no,
                      '当前可用资金比例：', Ar, '当前需购买的数量：',
                      need_, fontcolor.END)
                if br > 0:
                    g = sgls.sort_values(['confidence'], ascending=True).head(n=int(need_))
                    bct_ = len(g)  # 本次购买数量
                    if bct_ > 0:
                        """日内按最大持仓量计算固定投资比例，按实际资金池存量买入"""
                        # br = Rr / cls.model_param['max_position']
                        g['Rr'] = br
                        g['exp_open_vol'] = br * r.model_ratio * r.total * 0.9  # 将剩余资金按比例买入,略低于预期
                        g['stop_loss'] = r['stop_loss']
                        g['stop_get'] = r['stop_get']
                        g['fee'] = r['fee']
                        # TODO(leungjain): A股涉及到通过IB或其他国外交易平台
                        # 这主要关乎通过沪、深港通过北向买卖A股，但其交易日与
                        # A股或港股都不同，这时就需要通过沪、深港通的交易安排计算持有时间
                        g['pst_date'] = rk.finally_datetime(tdy, max_pst_days=r['max_pst_days'],
                                                            max_pst_hour=0, max_pst_min=0,
                                                            market=market)
                        g['client_no'] = r.client_no
                        print(fontcolor.F_GREEN, '买入：', g.stock_code.tolist(), fontcolor.END)
                        try:
                            od.update_client_info(condition={'_id': r['_id_y']}, Rr=r['Rr'] - br * bct_,
                                                  update=dt.datetime.now())
                            # if rst['nModified'] == 0 or rst['updatedExisting'] is not True:
                            #     print('账户:{} Rr未能成功更新，取消本次推荐.'.format(r['client_no']))
                            #     continue
                        except Exception as e:
                            ExceptionInfo(e)
                            continue
                        # op['pst_list'] = g.stock_code.tolist()
                        # op['Rr'] -= br * bct_
                        # op = cls.order_param_modify(op, model_from)
                        goods = pd.concat([goods, g], axis=0, join='outer', ignore_index=True)
                    else:
                        print(fontcolor.F_GREEN, '没有发现可以买入的信号', fontcolor.END)
                else:
                    print(fontcolor.F_GREEN, '支持当前策略的余额不足', fontcolor.END)
                print(fontcolor.F_GREEN, '时间: ', dt.datetime.now(), '备注: ', remarks, fontcolor.END)
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
            if len(goods):
                goods = goods.round({'confidence': 2, 'Rr': 2, 'exp_open_vol': 0})
                # print(goods.head())
                goods['act_open_vol'] = 0
                goods['date'] = goods.open_date.dt.normalize()
                goods['time'] = goods.open_date.map(lambda x: x.hour * 100 + x.minute)
                goods['max_pst_date'] = goods.pst_date + pd.Timedelta(hours=14, minutes=40)
                goods['pst_time'] = 1440
                goods['market'] = 'CN'
                goods['status'] = 0
                goods['limit'] = False
                goods['reason'] = 200
                goods['profit'] = 0
                goods['act_close_vol'] = 0
                goods['RV'] = 0
                #####################
                od.open(goods)
                #####################
                df = goods.loc[:, ['model_from', 'client_no', 'stock_code',
                                   'open_price', 'confidence', 'Rr',
                                   'max_pst_date']]
                df = pd.pivot_table(df, index=['model_from', 'client_no', 'stock_code'])
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
                print(fontcolor.F_PURPLE, df, fontcolor.END)
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
            else:
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                print(fontcolor.F_RED + '#策略' + model_from +
                      '推荐记录#' + fontcolor.END)
                print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                      '备注：无新信号建议', fontcolor.END)
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        else:
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
            print(fontcolor.F_RED + '#策略' + model_from + '推荐记录#' + fontcolor.END)
            print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                  '备注：当前无托管账户支持该策略', fontcolor.END)
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        return goods

    @classmethod
    def order_action_hk(cls, model_from, data, point=None, market=None):
        """
        为已接受托管的账户推荐信号，按’因户推送‘的原则推送，
        :param market: 默认通过港交所（HK_Stock）
        :param point:
        :param model_from:模型策略的名称
        :param data:model_from策略的信号数据
        :return:
        """
        tdy = dt.date.today() if point is None else point
        tdy = dt.datetime(tdy.year, tdy.month, tdy.day)
        # tdy = dt.datetime(2018, 7, 6)
        if market is None:
            # 默认香港平台
            if trading('HK_Stock').is_trade_day(tdy) is not True:
                Console.HK_is_not_trade_day()
                return pd.DataFrame()
            pass
        else:
            if market in ['HSHCS']:  # 当前使用沪、深港通
                if trading(market=market).is_trade_day(tdy) is not True:
                    Console.HSHCS_is_not_trade_day()
                    return pd.DataFrame()
        order_filed = ['type', 'open_date', 'open_price', 'confidence', 'model_from']
        if set(order_filed) <= set(data.columns):
            pass
        else:
            raise Exception('this orders lost must field')

        from Calf.data import OrderData as od
        ais = od.read_account_info(model_from=model_from, date=tdy)
        cli = od.read_client_info(model_from=model_from, status=1)
        if len(ais) == 0 or len(cli) == 0:
            Console.no_asset_or_client()
            return pd.DataFrame()
        ais = pd.merge(ais, cli, on=['client_no', 'model_from'])
        ais.dropna(axis=1, inplace=True)
        goods = pd.DataFrame()
        if len(ais):
            # 有账户订阅这个策略
            # op = cls.order_param_load(model_from)
            for i, r in ais.iterrows():
                # 为X账户推荐信号
                '''X账户已持有的来自于model_from策略的记录'''
                orders = od.read_orders(model_from=model_from, client_no=r.client_no, status=1)
                sgls = data.copy(deep=True)  #
                if len(orders):
                    '''X账户已经持有新推荐的信号，将这些排除在外'''
                    same = list(data[data.stock_code.isin(orders.stock_code)].index)
                    sgls.drop(same, axis=0, inplace=True)
                    # sgls = sgls.reset_index()
                if len(sgls) == 0:
                    '''没有可以向X推荐的信号'''
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    print(fontcolor.F_RED + '# 策略' + model_from + '推荐记录 #' + fontcolor.END)
                    print(fontcolor.F_RED + '账户：' + r.client_no, fontcolor.END)
                    print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                          '备注：没有找到可以推荐的信号：', fontcolor.END)
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    continue
                '''X账户还可以买入的比例，这个比例是针对于这个策略的'''
                # if len(orders):
                #     Ar = op['Rr'] - orders.act_open_vol.sum() / (r.model_ratio * r.total)
                #     op['Rr'] = Ar   # 更新权重，这是一个在model_ratio基础之上相当于total的权值
                # else:
                #     # 使用上一次更新的权值
                #     Ar = op['Rr']
                Ar = r['Rr']
                if Ar > 0:
                    aRr = 1 / r['max_pst_vol']  # 策略标准单信号买入比例
                    if r['max_pst_vol'] <= len(orders):
                        # 还有钱，但仓位数量已占满
                        '''增加仓位'''
                        # need_ = Ar // aRr
                        # need_ = need_ + 1 if Ar % aRr != 0 else need_
                        # br = Ar / need_
                        need_ = 0
                        br = 0
                        remarks = '账户余额充足，仓位不足'
                    else:
                        need_ = (r['max_pst_vol'] - len(orders))  # 剩余仓位
                        br = Ar / need_
                        br = aRr if br > aRr else br
                        remarks = '账户余额充足，按正常水平补填仓位'
                else:
                    need_ = 0
                    br = 0
                    remarks = '账户余额不足，无新信号推荐'
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
                print(fontcolor.F_GREEN + '# 策略' + model_from + '推荐记录 #' + fontcolor.END)
                print(fontcolor.F_GREEN + '账户：', r.client_no, '当前可用资金比例：',
                      Ar, '当前需购买的数量：', need_, fontcolor.END)
                if br > 0:
                    g = sgls.sort_values(['confidence'], ascending=True).head(n=int(need_))
                    bct_ = len(g)  # 本次购买数量
                    if bct_ > 0:
                        """日内按最大持仓量计算固定投资比例，按实际资金池存量买入"""
                        # br = Rr / cls.model_param['max_position']
                        g['Rr'] = br
                        g['exp_open_vol'] = br * r.model_ratio * r.total * 0.9  # 将剩余资金按比例买入,略低于预期
                        g['stop_loss'] = r['stop_loss']
                        g['stop_get'] = r['stop_get']
                        g['fee'] = r['fee']
                        g['client_no'] = r.client_no
                        print(fontcolor.F_GREEN, '买入：', g.stock_code.tolist(), fontcolor.END)
                        try:
                            # g['date'] = trading(market='HK_Stock').trade_period(tdy, 1)
                            g['pst_date'] = rk.finally_datetime(tdy, max_pst_days=r['max_pst_days'],
                                                                max_pst_hour=0, max_pst_min=0,
                                                                market='HK_Stock')
                            od.update_client_info(condition={'_id': r['_id_y']}, Rr=r['Rr'] - br * bct_,
                                                  update=dt.datetime.now())
                            # if rst['nModified'] == 0 or rst['updatedExisting'] is not True:
                            #     print('账户:{} Rr未能成功更新，取消本次推荐.'.format(r['client_no']))
                            #     continue
                        except Exception as e:
                            ExceptionInfo(e)
                            continue
                        # op['pst_list'] = g.stock_code.tolist()
                        # op['Rr'] -= br * bct_
                        # op = cls.order_param_modify(op, model_from)
                        goods = pd.concat([goods, g], axis=0, join='outer', ignore_index=True)
                    else:
                        print(fontcolor.F_GREEN, '没有发现可以买入的信号', fontcolor.END)
                else:
                    print(fontcolor.F_GREEN, '支持当前策略的余额不足', fontcolor.END)
                print(fontcolor.F_GREEN, '时间：', dt.datetime.now(), '备注：', remarks, fontcolor.END)
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
            if len(goods):
                # TODO(leungjain): 一切相对于orders表的特殊操作都应该通过goods修改
                goods = goods.round({'confidence': 2, 'Rr': 2, 'exp_open_vol': 0})
                # print(goods.head())
                goods['stock_code'] = goods.stock_code.map(lambda x: str(int(x)))
                goods['act_open_vol'] = 0
                goods['date'] = goods.open_date.dt.normalize()
                goods['time'] = goods.open_date.map(lambda x: x.hour * 100 + x.minute)
                goods['max_pst_date'] = goods.pst_date + pd.Timedelta(hours=15, minutes=40)
                goods['pst_time'] = 1540
                goods['market'] = 'HK'
                goods['status'] = 0
                goods['limit'] = False
                goods['reason'] = 200
                goods['profit'] = 0
                goods['act_close_vol'] = 0
                goods['RV'] = 0
                # goods['stock_code'] = goods.stock_code.map(lambda x: str(int(x)))
                #####################
                od.open(goods)
                #####################
                df = goods.loc[:, ['model_from', 'client_no', 'stock_code', 'open_price',
                                   'confidence', 'Rr', 'max_pst_date']]
                df = pd.pivot_table(df, index=['model_from', 'client_no', 'stock_code'])
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
                print(fontcolor.F_PURPLE, df, fontcolor.END)
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
            else:
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                print(fontcolor.F_RED + '#策略' + model_from +
                      '推荐记录#' + fontcolor.END)
                print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                      '备注：无新信号建议', fontcolor.END)
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                # return pd.DataFrame([], columns=cls.order_columns)
        else:
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
            print(fontcolor.F_RED + '#策略' + model_from +
                  '推荐记录#' + fontcolor.END)
            print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                  '备注：当前无托管账户支持该策略', fontcolor.END)
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        return goods

    @classmethod
    def order_action_usa(cls, model_from, data, point=None):
        """
        为已接受托管的账户推荐信号，按’因户推送‘的原则推送，
        :param point:
        :param model_from:模型策略的名称
        :param data:model_from策略的信号数据
        :return:
        """
        order_filed = ['type', 'open_date', 'open_price', 'confidence', 'model_from']
        if set(order_filed) <= set(data.columns):
            pass
        else:
            raise Exception('this orders lost must field')
        tdy = dt.datetime.now(tz=pytz.timezone('US/Eastern')) if point is None else point
        tdy = dt.datetime(tdy.year, tdy.month, tdy.day)
        # tdy = dt.datetime(2018, 7, 9)
        # data['date'] = tdy
        from Calf.data import OrderData as od
        ais = od.read_account_info(model_from=model_from, date=tdy)
        cli = od.read_client_info(model_from=model_from, status=1)
        if len(ais) == 0 or len(cli) == 0:
            Console.no_asset_or_client()
            return pd.DataFrame()
        ais = pd.merge(ais, cli, on=['client_no', 'model_from'])
        ais.dropna(axis=1, inplace=True)
        goods = pd.DataFrame()
        if len(ais):
            # 有账户订阅这个策略
            # op = cls.order_param_load(model_from)
            for i, r in ais.iterrows():
                # 为X账户推荐信号
                '''X账户已持有的来自于model_from策略的记录'''
                orders = od.read_orders(model_from=model_from, client_no=r.client_no, status=1)
                sgls = data.copy(deep=True)  #
                if len(orders):
                    '''X账户已经持有新推荐的信号，将这些排除在外'''
                    same = list(data[data.stock_code.isin(orders.stock_code)].index)
                    sgls.drop(same, axis=0, inplace=True)
                    # sgls = sgls.reset_index()
                if len(sgls) == 0:
                    '''没有可以向X推荐的信号'''
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    print(fontcolor.F_RED + '# 策略' + model_from +
                          '推荐记录 #' + fontcolor.END)
                    print(fontcolor.F_RED + '账户：' + r.client_no, fontcolor.END)
                    print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                          '备注：没有找到可以推荐的信号：', fontcolor.END)
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    continue
                '''X账户还可以买入的比例，这个比例是针对于这个策略的'''
                # if len(orders):
                #     Ar = op['Rr'] - orders.act_open_vol.sum() / (r.model_ratio * r.total)
                #     op['Rr'] = Ar   # 更新权重，这是一个在model_ratio基础之上相当于total的权值
                # else:
                #     # 使用上一次更新的权值
                #     Ar = op['Rr']
                Ar = r['Rr']
                if Ar > 0:
                    aRr = 1 / r['max_pst_vol']  # 策略标准单信号买入比例
                    if r['max_pst_vol'] <= len(orders):
                        # 还有钱，但仓位数量已占满
                        '''增加仓位'''
                        # need_ = Ar // aRr
                        # need_ = need_ + 1 if Ar % aRr != 0 else need_
                        # br = Ar / need_
                        need_ = 0
                        br = 0
                        remarks = '账户余额充足，仓位不足'
                    else:
                        need_ = (r['max_pst_vol'] - len(orders))  # 剩余仓位
                        br = Ar / need_
                        br = aRr if br > aRr else br
                        remarks = '账户余额充足，按正常水平补填仓位'
                else:
                    need_ = 0
                    br = 0
                    remarks = '账户余额不足，无新信号推荐'
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
                print(fontcolor.F_GREEN + '# 策略' + model_from +
                      '推荐记录 #' + fontcolor.END)
                print(fontcolor.F_GREEN + '账户：', r.client_no,
                      '当前可用资金比例：', Ar, '当前需购买的数量：',
                      need_, fontcolor.END)
                if br > 0:
                    g = sgls.sort_values(['confidence'], ascending=True).head(n=int(need_))
                    bct_ = len(g)  # 本次购买数量
                    if bct_ > 0:
                        """日内按最大持仓量计算固定投资比例，按实际资金池存量买入"""
                        # br = Rr / cls.model_param['max_position']
                        g['Rr'] = br
                        g['exp_open_vol'] = br * r.model_ratio * r.total * 0.9  # 将剩余资金按比例买入,略低于预期
                        g['stop_loss'] = r['stop_loss']
                        g['stop_get'] = r['stop_get']
                        g['fee'] = r['fee']
                        g['client_no'] = r.client_no
                        print(fontcolor.F_GREEN, '买入：', g.stock_code.tolist(), fontcolor.END)
                        try:
                            g['date'] = trading(market='USA_Stock').trade_period(tdy, 1)
                            g['pst_date'] = rk.finally_datetime(
                                tdy, max_pst_days=r['max_pst_days'],
                                max_pst_hour=0, max_pst_min=0,
                                market='USA_Stock')
                            od.update_client_info(condition={'_id': r['_id_y']},
                                                  Rr=r['Rr'] - br * bct_,
                                                  update=dt.datetime.now())
                            # if rst['nModified'] == 0 or rst['updatedExisting'] is not True:
                            #     print('账户:{} Rr未能成功更新，取消本次推荐.'.format(r['client_no']))
                            #     continue
                        except Exception as e:
                            ExceptionInfo(e)
                            continue
                        # op['pst_list'] = g.stock_code.tolist()
                        # op['Rr'] -= br * bct_
                        # op = cls.order_param_modify(op, model_from)
                        goods = pd.concat([goods, g], axis=0, join='outer', ignore_index=True)
                    else:
                        print(fontcolor.F_GREEN, '没有发现可以买入的信号', fontcolor.END)
                else:
                    print(fontcolor.F_GREEN, '支持当前策略的余额不足', fontcolor.END)
                print(fontcolor.F_GREEN, '时间：', dt.datetime.now(),
                      '备注：', remarks, fontcolor.END)
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
            if len(goods):
                goods = goods.round({'confidence': 2, 'Rr': 2, 'exp_open_vol': 0})
                # print(goods.head())
                goods['act_open_vol'] = 0
                goods['date'] = goods.open_date.dt.normalize()
                goods['time'] = goods.open_date.map(lambda x: x.hour * 100 + x.minute)
                goods['max_pst_date'] = goods.pst_date + pd.Timedelta(hours=15, minutes=40)
                goods['pst_time'] = 1540
                goods['market'] = 'US'
                goods['status'] = 0
                goods['limit'] = False
                goods['reason'] = 200
                goods['profit'] = 0
                goods['act_close_vol'] = 0
                goods['RV'] = 0
                #####################
                od.open(goods)
                #####################
                df = goods.loc[:, ['model_from', 'client_no', 'stock_code',
                                   'open_price', 'confidence', 'Rr',
                                   'max_pst_date']]
                df = pd.pivot_table(df, index=['model_from', 'client_no', 'stock_code'])
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
                print(fontcolor.F_PURPLE, df, fontcolor.END)
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
            else:
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                print(fontcolor.F_RED + '#策略' + model_from +
                      '推荐记录#' + fontcolor.END)
                print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                      '备注：无新信号建议', fontcolor.END)
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                # return pd.DataFrame([], columns=cls.order_columns)
        else:
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
            print(fontcolor.F_RED + '#策略' + model_from +
                  '推荐记录#' + fontcolor.END)
            print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                  '备注：当前无托管账户支持该策略', fontcolor.END)
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        return goods

    @classmethod
    def order_action_fx(cls, model_from, data, point=None):
        """
        为已接受托管的账户推荐信号，按’因户推送‘的原则推送，
        :param point:
        :param model_from:模型策略的名称
        :param data:model_from策略的信号数据
        :return:
        """
        order_filed = ['type', 'open_date', 'open_price',
                       'confidence', 'model_from']
        if set(order_filed) <= set(data.columns):
            pass
        else:
            raise Exception('this orders lost must field')
        tdy = dt.datetime.now(tz=pytz.timezone('US/Eastern')) if point is None else point
        tdy = dt.datetime(tdy.year, tdy.month, tdy.day)
        # tdy = dt.datetime(2018, 7, 9)
        # data['date'] = tdy
        from Calf.data import OrderData as od
        ais = od.read_account_info(model_from=model_from, date=tdy)
        cli = od.read_client_info(model_from=model_from, status=1)
        if len(ais) == 0 or len(cli) == 0:
            return pd.DataFrame()
        ais = pd.merge(ais, cli, on=['client_no', 'model_from'])
        ais.dropna(axis=1, inplace=True)
        goods = pd.DataFrame()
        if len(ais):
            # 有账户订阅这个策略
            # op = cls.order_param_load(model_from)
            for i, r in ais.iterrows():
                # 为X账户推荐信号
                '''X账户已持有的来自于model_from策略的记录'''
                orders = od.read_orders(
                    model_from=model_from, client_no=r.client_no, status=1
                )
                sgls = data.copy(deep=True)  #
                if len(orders):
                    '''X账户已经持有新推荐的信号，将这些排除在外'''
                    same = list(data[data.stock_code.isin(orders.stock_code)].index)
                    sgls.drop(same, axis=0, inplace=True)
                    # sgls = sgls.reset_index()
                if len(sgls) == 0:
                    '''没有可以向X推荐的信号'''
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    print(fontcolor.F_RED + '# 策略' + model_from +
                          '推荐记录 #' + fontcolor.END)
                    print(fontcolor.F_RED + '账户：' + r.client_no, fontcolor.END)
                    print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                          '备注：没有找到可以推荐的信号：', fontcolor.END)
                    print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                    continue
                '''X账户还可以买入的比例，这个比例是针对于这个策略的'''
                # if len(orders):
                #     Ar = op['Rr'] - orders.act_open_vol.sum() / (r.model_ratio * r.total)
                #     op['Rr'] = Ar   # 更新权重，这是一个在model_ratio基础之上相当于total的权值
                # else:
                #     # 使用上一次更新的权值
                #     Ar = op['Rr']
                Ar = r['Rr']
                if Ar > 0:
                    aRr = 1 / r['max_pst_vol']  # 策略标准单信号买入比例
                    if r['max_pst_vol'] <= len(orders):
                        # 还有钱，但仓位数量已占满
                        '''增加仓位'''
                        # need_ = Ar // aRr
                        # need_ = need_ + 1 if Ar % aRr != 0 else need_
                        # br = Ar / need_
                        need_ = 0
                        br = 0
                        remarks = '可用余额不为零，但不增加额外仓位'
                    else:
                        need_ = (r['max_pst_vol'] - len(orders))  # 剩余仓位
                        br = Ar / need_
                        br = aRr if br > aRr else br
                        remarks = '可用余额不为零，按正常水平补填仓位'
                else:
                    need_ = 0
                    br = 0
                    remarks = '可用余额不足，无新信号推荐'
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
                print(fontcolor.F_GREEN + '# 策略' + model_from +
                      '推荐记录 #' + fontcolor.END)
                print(fontcolor.F_GREEN + '账户：', r.client_no,
                      '当前可用资金比例：', Ar, '当前需购买的数量：',
                      need_, fontcolor.END)
                if br > 0:
                    g = sgls.sort_values(['confidence'], ascending=True).head(n=int(need_))
                    bct_ = len(g)  # 本次购买数量
                    if bct_ > 0:
                        """日内按最大持仓量计算固定投资比例，按实际资金池存量买入"""
                        # br = Rr / cls.model_param['max_position']
                        g['Rr'] = br
                        g['exp_open_vol'] = br * r.model_ratio * r.total * 0.9  # 将剩余资金按比例买入,略低于预期
                        g['stop_loss'] = r['stop_loss']
                        g['stop_get'] = r['stop_get']
                        g['fee'] = r['fee']
                        g['client_no'] = r.client_no
                        print(fontcolor.F_GREEN, '买入：', g.stock_code.tolist(), fontcolor.END)
                        try:
                            # g['date'] = tdy
                            # g['pst_date'] = tdy + dt.timedelta(hours=10)
                            od.update_client_info(condition={'_id': r['_id_y']},
                                                  Rr=r['Rr'] - br * bct_,
                                                  update=dt.datetime.now())
                            # if rst['nModified'] == 0 or rst['updatedExisting'] is not True:
                            #     print('账户:{} Rr未能成功更新，取消本次推荐.'.format(r['client_no']))
                            #     continue
                        except Exception as e:
                            ExceptionInfo(e)
                            continue
                        # op['pst_list'] = g.stock_code.tolist()
                        # op['Rr'] -= br * bct_
                        # op = cls.order_param_modify(op, model_from)
                        goods = pd.concat([goods, g], axis=0, join='outer', ignore_index=True)
                    else:
                        print(fontcolor.F_GREEN, '没有发现可以买入的信号', fontcolor.END)
                else:
                    print(fontcolor.F_GREEN, '支持当前策略的余额不足', fontcolor.END)
                print(fontcolor.F_GREEN, '时间：', dt.datetime.now(),
                      '备注：', remarks, fontcolor.END)
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
            if len(goods):
                goods = goods.round({'confidence': 2, 'Rr': 2, 'exp_open_vol': 0})
                # print(goods.head())
                goods['act_open_vol'] = 0
                goods['max_pst_date'] = goods.open_date + pd.Timedelta(hours=10)
                goods['date'] = goods.open_date.map(lambda x: dt.datetime(x.year, x.month, x.day))
                goods['time'] = goods.open_date.map(lambda x: x.hour * 100 + x.minutes)
                goods['pst_date'] = goods.max_pst_date.map(lambda x: dt.datetime(x.year, x.month, x.day))
                goods['pst_time'] = goods.max_pst_date.map(lambda x: x.hour * 100 + x.minutes)
                goods['market'] = 'US'
                goods['status'] = 0
                goods['limit'] = False
                goods['reason'] = 200
                goods['profit'] = 0
                goods['act_close_vol'] = 0
                goods['RV'] = 0
                #####################
                od.open(goods)
                #####################
                df = goods.loc[:, ['model_from', 'client_no', 'stock_code',
                                   'open_price', 'confidence', 'Rr',
                                   'max_pst_date']]
                df = pd.pivot_table(df, index=['model_from', 'client_no', 'stock_code'])
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
                print(fontcolor.F_PURPLE, df, fontcolor.END)
                print(fontcolor.F_PURPLE + '=' * 80 + fontcolor.END)
            else:
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                print(fontcolor.F_RED + '#策略' + model_from +
                      '推荐记录#' + fontcolor.END)
                print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                      '备注：无新信号建议', fontcolor.END)
                print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
                # return pd.DataFrame([], columns=cls.order_columns)
        else:
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
            print(fontcolor.F_RED + '#策略' + model_from +
                  '推荐记录#' + fontcolor.END)
            print(fontcolor.F_RED, '时间：', dt.datetime.now(),
                  '备注：当前无托管账户支持该策略', fontcolor.END)
            print(fontcolor.F_RED + '=' * 80 + fontcolor.END)
        return goods

    @classmethod
    def order_probe_zh(cls, model_from):
        """
        对真实发生的订单进行一些处理，相关的一些参数都维护在数据库
        当中，以便交易端进行相关同步操作，因此，关于order的控制，必
        需协调好交易端的逻辑
        :param model_from:
        :return:
        """
        try:
            # 发生交易且reason=200的订单
            from Calf.data import OrderData as od
            data = od.read_orders(model_from=model_from, status=1, reason=200)
            if len(data):
                # 读取实时价格数据，并计算收益。可能会出现价格数据异常
                # 的情况，例如在非交易时间读取，可能会返回异常的数据
                # 为尽量避免出现这种情况，一是：尽量不要在非交易时间
                # 读取数据，二是：对返回的数据进行判断，下面的函数已经
                # 做了第二点
                data = rk.real_profit(data, market='ZH')
                if len(data) == 0:
                    return None
                # data['reason'] = 200
                for i, r in data.iterrows():
                    p = round(r.profit, 3)
                    rs = 200
                    if r.type and r.datetime.day != r.open_date.day:
                        if p >= r.stop_loss:
                            rs = -1
                        elif p < r.stop_get * -1:
                            rs = 1
                        elif r.datetime >= r.max_pst_date:
                            rs = 0
                        else:
                            pass
                    if not r.type and r.datetime.day != r.open_date.day:
                        if p <= r.stop_loss * -1:
                            rs = -1
                        elif p > r.stop_get:
                            rs = 1
                        elif r.datetime >= r.max_pst_date:
                            rs = 0
                        else:
                            pass
                    # rsn.append(rs)
                    data.at[i, ['reason']] = rs
                # data['reason'] = rsn
                # 已止盈损，或持有最长时间已到
                stop_data = data[(data.reason == reason['stop_get']) |
                                 (data.reason == reason['stop_loss']) |
                                 (data.reason == reason['timeout'])].copy(deep=True)
                if len(stop_data) == 0:
                    return None

                stop_data = stop_data.rename(
                    columns={'datetime': 'close_date', 'price': 'close_price'})
                cols = ['_id', 'stock_code', 'type', 'open_date', 'open_price', 'confidence',
                        'Rr', 'close_date', 'status', 'close_price', 'stop_loss', 'stop_get',
                        'fee', 'profit', 'reason', 'model_from', 'version']
                stop_data = stop_data.loc[:, cols]
                stop_data['profit'] -= stop_data.fee
                # 修改reason，以防下一次继续监控
                for i, r in stop_data.iterrows():
                    '''更新这个推荐的股票'''
                    od.update_orders(condition={'_id': r['_id']},
                                     reason=r.reason, profit=r.profit)
                # op = cls.order_param_load(model_from)  # 修改交易参数
                # '''回笼资金后不补填缺口，仍以不高于原始资金量的比例入市'''
                # op['Rr'] += ((stop_data.profit + 1) * stop_data.Rr).sum()
                # op['Rr'] = 1 if op['Rr'] > 1 else op['Rr']
                # 修改的是项目中的json参数文件，
                # op = cls.order_param_modify(op, model_from)
                print(fontcolor.F_GREEN + '=' * 80)
                print('{}: those orders should exit'.format(model_from))
                print(stop_data.loc[:, ['stock_code', 'type', 'open_date', 'Rr',
                                        'profit', 'reason', 'model_from']])
                # print('Rr ==> {}'.format(op['Rr']))
                print('=' * 80 + fontcolor.END)
                # stop_data['status'] = 0
                # cls.od.insert_orders(stop_data, table_name='orders_simulated')
                # 跟交易端通信，告诉交易端应该把这个order平掉
                # TODO(leungjain): 只告诉交易端止盈止损
                sp = stop_data[(stop_data.reason == reason['stop_get']) |
                               (stop_data.reason == reason['stop_loss'])].copy(deep=True)
                if len(sp):
                    try:
                        r = notice(MODEL_ORDER_ACTION,
                                   close_date=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                   task=TASK_CODE['close_orders'], model_from=model_from,
                                   market='CN', id=sp['_id'].astype('str').tolist())
                        print(r)
                    except Exception as e:
                        ExceptionInfo(e)
                return stop_data
            else:
                return None
        except Exception as e:
            ExceptionInfo(e)
            return None

    @classmethod
    def order_probe_hk(cls, model_from):
        try:
            # 发生交易的订单
            from Calf.data import OrderData as od
            data = od.read_orders(model_from=model_from, status=1, reason=200)
            if len(data):
                # bug
                data['stock_code'] = data.stock_code.map(lambda x: '0' * (5 - len(str(x))) + str(x))
                data = rk.real_profit(data, market='HK')
                if len(data) == 0:
                    return None
                # rsn = list()
                for i, r in data.iterrows():
                    p = round(r.profit, 3)
                    rs = 200
                    if r.type:
                        if p >= r.stop_loss:
                            rs = -1
                        elif p < r.stop_get * -1:
                            rs = 1
                        elif r.datetime >= r.max_pst_date:
                            rs = 0
                        else:
                            pass
                        data.at[i, ['profit', 'reason']] = r.profit * -1, rs
                    if not r.type:
                        if p <= r.stop_loss * -1:
                            rs = -1
                        elif p > r.stop_get:
                            rs = 1
                        elif r.datetime >= r.max_pst_date:
                            rs = 0
                        else:
                            pass
                        data.at[i, ['reason']] = rs
                        # rsn.append(rs)
                # data['reason'] = rsn
                # 已止盈损，或持有最长时间已到
                stop_data = data[(data.reason == reason['stop_get']) |
                                 (data.reason == reason['stop_loss']) |
                                 (data.reason == reason['timeout'])].copy(deep=True)
                if len(stop_data) == 0:
                    return None

                stop_data = stop_data.rename(
                    columns={'datetime': 'close_date', 'price': 'close_price'})
                cols = ['_id', 'stock_code', 'type', 'open_date', 'open_price',
                        'confidence', 'Rr', 'close_date', 'status', 'close_price',
                        'stop_loss', 'stop_get', 'fee', 'profit', 'reason',
                        'model_from', 'version']
                stop_data = stop_data.loc[:, cols]
                stop_data['profit'] -= stop_data.fee
                # 修改reason，以防下一次继续监控
                for i, r in stop_data.iterrows():
                    '''更新这个推荐的股票'''
                    od.update_orders(condition={'_id': r['_id']},
                                     reason=r.reason, profit=r.profit)
                # op = cls.order_param_load(model_from)  # 修改交易参数
                # '''回笼资金后不补填缺口，仍以不高于原始资金量的比例入市'''
                # op['Rr'] += ((stop_data.profit + 1) * stop_data.Rr).sum()
                # op['Rr'] = 1 if op['Rr'] > 1 else op['Rr']
                # op = cls.order_param_modify(op, model_from)
                print(fontcolor.F_GREEN + '=' * 80)
                print('{}: those orders should exit'.format(model_from))
                print(stop_data.loc[:, ['stock_code', 'type', 'open_date', 'Rr',
                                        'profit', 'reason', 'model_from']])
                # print('Rr ==> {}'.format(op['Rr']))
                print('=' * 80 + fontcolor.END)
                # stop_data['status'] = 0
                # cls.od.insert_orders(stop_data, table_name='orders_simulated')
                sp = stop_data[(stop_data.reason == reason['stop_get']) |
                               (stop_data.reason == reason['stop_loss'])].copy(deep=True)
                if len(sp):
                    try:
                        r = notice(MODEL_ORDER_ACTION,
                                   close_date=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                   task=TASK_CODE['close_orders'], model_from=model_from,
                                   market='HK', id=sp['_id'].astype('str').tolist())
                        print(r)
                    except Exception as e:
                        ExceptionInfo(e)
                return stop_data
            else:
                return None
        except Exception as e:
            ExceptionInfo(e)
            return None

    @classmethod
    def order_probe_usa(cls, model_from):
        try:
            # 发生交易的订单
            from Calf.data import OrderData as od
            data = od.read_orders(model_from=model_from, status=1, reason=200)
            if len(data):
                data = rk.real_profit(data, market='US')
                if len(data) == 0:
                    return None
                # rsn = list()
                for i, r in data.iterrows():
                    p = round(r.profit, 3)
                    rs = 200
                    if r.type:
                        if p >= r.stop_loss:
                            rs = -1
                        elif p < r.stop_get * -1:
                            rs = 1
                        elif r.datetime >= r.max_pst_date:
                            rs = 0
                        else:
                            pass
                        data.at[i, ['profit', 'reason']] = r.profit * -1, rs
                    if not r.type:
                        if p <= r.stop_loss * -1:
                            rs = -1
                        elif p > r.stop_get:
                            rs = 1
                        elif r.datetime >= r.max_pst_date:
                            rs = 0
                        else:
                            pass
                        data.at[i, ['reason']] = rs
                        # rsn.append(rs)
                # data['reason'] = rsn
                # 已止盈损，或持有最长时间已到
                stop_data = data[(data.reason == reason['stop_get']) |
                                 (data.reason == reason['stop_loss']) |
                                 (data.reason == reason['timeout'])].copy(deep=True)
                if len(stop_data) == 0:
                    return None

                stop_data = stop_data.rename(
                    columns={'datetime': 'close_date', 'price': 'close_price'})
                cols = ['_id', 'stock_code', 'type', 'open_date', 'open_price', 'confidence',
                        'Rr', 'close_date', 'status', 'close_price', 'stop_loss', 'stop_get',
                        'fee', 'profit', 'reason', 'model_from', 'version']
                stop_data = stop_data.loc[:, cols]
                stop_data['profit'] -= stop_data.fee
                # 修改reason，以防下一次继续监控
                for i, r in stop_data.iterrows():
                    '''移除这个推荐的股票'''
                    od.update_orders(condition={'_id': r['_id']},
                                     reason=r.reason, profit=r.profit)
                # op = cls.order_param_load(model_from)  # 修改交易参数
                # '''回笼资金后不补填缺口，仍以不高于原始资金量的比例入市'''
                # op['Rr'] += ((stop_data.profit + 1) * stop_data.Rr).sum()
                # op['Rr'] = 1 if op['Rr'] > 1 else op['Rr']
                # op = cls.order_param_modify(op, model_from)
                print(fontcolor.F_GREEN + '=' * 80)
                print('{}: those orders should exit'.format(model_from))
                print(stop_data.loc[:, ['stock_code', 'type', 'open_date', 'Rr',
                                        'profit', 'reason', 'model_from']])
                # print('Rr ==> {}'.format(op['Rr']))
                print('=' * 80 + fontcolor.END)
                # stop_data['status'] = 0
                # cls.od.insert_orders(stop_data, table_name='orders_simulated')
                sp = stop_data[(stop_data.reason == reason['stop_get']) |
                               (stop_data.reason == reason['stop_loss'])].copy(deep=True)
                if len(sp):
                    try:
                        r = notice(MODEL_ORDER_ACTION,
                                   close_date=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                   task=TASK_CODE['close_orders'], model_from=model_from,
                                   market='US', id=sp['_id'].astype('str').tolist())
                        print(r)
                    except Exception as e:
                        ExceptionInfo(e)
                return stop_data
            else:
                return None
        except Exception as e:
            ExceptionInfo(e)
            return None

    @classmethod
    def Rr_recover(cls, model_from):
        """
        回收Rr权值
        因为在实际的交易中，可能并为按照预期的那样完全执行交易
        动作。因此，我们需要重新评估在推荐信号时给定的Rr值，以
        便后面的买卖动作尽量在真实的场景中运行，其目的是更好的
        使用资金。
        回收Rr应该是在模型信号推荐之前进行！！！
        :return:
        """
        try:
            # 回收Rr，从三个方面入手，一是：完全未买入，二是未完全买入，
            # 三是平仓后收益导致的Rr变动
            # 1.完全未买入，即orders的status为0

            # 账户信息
            from Calf.data import OrderData as od
            cli = od.read_client_info(model_from, status=1,
                                      field={'client_no': True,
                                             'model_from': True,
                                             'Rr': True,
                                             })  # 订阅m的账户
            # 未开仓或未完全开仓，且从未被回收过
            ods = od.read_orders(model_from=model_from, status={'$in': [0, 1]}, RV=0,
                                 field={
                                     'client_no': True,
                                     'model_from': True,
                                     'Rr': True,
                                     'exp_open_vol': True,
                                     'act_open_vol': True
                                 })
            if len(cli) > 0 and len(ods) > 0:
                ods = pd.merge(ods, cli, on=['client_no', 'model_from'])
                ods['Rr'] = ods['Rr_x'] * (1 - ods.act_open_vol / ods.exp_open_vol)
                ods_ = ods.groupby(['client_no'],
                                   as_index=False).agg({'_id_x': 'first',
                                                        '_id_y': 'first',
                                                        'Rr': 'sum',
                                                        'Rr_y': 'first'
                                                        })
                # 1.回收Rr
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
                print(fontcolor.F_GREEN + '平仓前回收({})'.format(model_from) + fontcolor.END)
                ods_ = ods_.round({'Rr_y': 2, 'Rr': 2})
                for i, r in ods_.iterrows():
                    _ = r['Rr_y'] + r['Rr']
                    _Rr = 1 if _ > 1 else _  # TODO(leungjain): 区分单利与复利的一个计算关键
                    od.update_client_info(condition={'_id': r['_id_y']}, Rr=_Rr)
                    # if False:
                    #     print(fontcolor.F_RED + '账户:{} Rr未能成功更新，取消本次回收.'
                    #           .format(r['client_no']) + fontcolor.END)
                    #     continue
                    # else:
                    # 账户的Rr权值已更新成功
                    # 正式回收Rr
                    _ids = ods[ods.client_no == r['client_no']]['_id_x'].tolist()
                    od.update_orders(condition={'_id': {'$in': _ids}}, RV=2)
                    # if False:
                    #     print(fontcolor.F_RED + '账户:{0} Rr成功更新，但Order:{1}更新失败.'
                    #           .format(r['client_no'], r['_id_x']) + fontcolor.END)
                    #     print(fontcolor.F_RED + '账户:{0} 应回收的Rr值为 {1}'
                    #           .format(r['client_no'], _Rr) + fontcolor.END)
                    # else:
                    print(fontcolor.F_GREEN + '账户:{0}(Rr:{1} -> {2} -> {3})更新成功.'
                          .format(r['client_no'], r.Rr_y, _, _Rr) + fontcolor.END)
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)

            # 平仓后回收，一个订单可能经历两轮回收，平仓后回收是针对status=2&RV=2
            # 而言的，平仓后回收可能有两种情况：1已经被平仓前回收过，2从未被回收过
            cds = od.read_orders(model_from=model_from, status=2, RV={'$in': [0, 2]},
                                 field={
                                     'client_no': True,
                                     'model_from': True,
                                     'Rr': True,
                                     'exp_open_vol': True,
                                     'act_open_vol': True,
                                     'act_close_vol': True
                                 })
            if len(cli) > 0 and len(cds) > 0:
                cds = pd.merge(cds, cli, on=['client_no', 'model_from'])
                cds['Rr'] = cds['Rr_x'] * cds.act_close_vol / cds.exp_open_vol
                cds_ = cds.groupby(['client_no'],
                                   as_index=False).agg({'_id_x': 'first',
                                                        '_id_y': 'first',
                                                        'Rr': 'sum',
                                                        'Rr_y': 'first'
                                                        })
                # 2.回收Rr
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
                print(fontcolor.F_GREEN + '平仓后回收({})'.format(model_from) + fontcolor.END)
                cds_ = cds_.round({'Rr_y': 2, 'Rr': 2})
                for i, r in cds_.iterrows():
                    _ = r['Rr_y'] + r['Rr']
                    _Rr = 1 if _ > 1 else _
                    od.update_client_info(condition={'_id': r['_id_y']}, Rr=_Rr)
                    # if False:
                    #     print(fontcolor.F_RED + '账户:{} Rr未能成功更新，取消本次回收.'.format(r['client_no'])
                    #           + fontcolor.END)
                    #     continue
                    # else:
                    # 账户的Rr权值已更新成功
                    # 正式回收Rr
                    _ids = cds[cds.client_no == r['client_no']]['_id_x'].tolist()
                    od.update_orders(condition={'_id': {'$in': _ids}}, RV=3)
                    # if False:
                    #     print(fontcolor.F_RED + '账户:{0} Rr成功更新，但Order:{1}更新失败.'
                    #           .format(r['client_no'], _ids) + fontcolor.END)
                    #     print(fontcolor.F_RED + '账户:{0} Rr值应更新为:{1}'
                    #           .format(r['client_no'], _Rr) + fontcolor.END)
                    # else:
                    print(fontcolor.F_GREEN + '账户:{0}(Rr:{1} -> {2} -> {3})更新成功.'
                          .format(r['client_no'], r.Rr_y, _, _Rr) + fontcolor.END)
                print(fontcolor.F_GREEN + '=' * 80 + fontcolor.END)
            pass
        except Exception as e:
            ExceptionInfo(e)


pass
# MacdOrder.Rr_recover('macd_min30')

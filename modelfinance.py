# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2017/11/18 10:48
"""
import datetime
import math
import numpy as np
import pandas as pd


class FinanceIndex:
    Model_Param = {
        'RISK_FREE': 0.045,  # 无风险收益或固定收益，常常以国债基金、标准利率、银行短期存款确定即货币的时间价值
        'INDEX_MARKET_REFERENCE': '399303',  # 计算市场无风险收益时选择的大盘指数
    }

    @classmethod
    def total_returns(cls, profit_list):
        """
        策略总收益
        :param profit_list:
        :return:
        """
        return np.sum(profit_list)

    @classmethod
    def annualized_returns(cls, profit_list):
        """
        策略年化收益
        :param profit_list:
        :return:
        """
        TR = np.sum(profit_list)
        Rp = (1 + TR) ** (252 / float(len(profit_list))) - 1
        return Rp

    @classmethod
    def get_loss_ratio(cls, profit_list):
        """
        盈亏比
        :param profit_list:
        :return:
        """
        get = 0
        loss = 0
        for p in profit_list:
            if p > 0:
                get += 1
            else:
                # p等于0的归集为亏损
                loss += 1
        plr = get / loss
        return plr

    @classmethod
    def information_ratio(cls, profit_list, index_profit_list):
        """
        信息比例.衡量单位超额风险带来的超额收益.
        :param profit_list:
        :param index_profit_list:
        :return:
        """
        Rp = np.sum(profit_list)
        Rm = np.sum(index_profit_list)
        Lp = len(profit_list)
        Lm = len(index_profit_list)
        diff = list()
        for i in range(Lp if Lp < Lm else Lm):
            diff.append(profit_list[i] - index_profit_list[i])
        delta_std = np.std(diff)
        IR = (Rp - Rm) / delta_std
        return IR

    @classmethod
    def volatility(cls, profit_list):
        """
        策略波动率。用来测量策略的风险性，波动越大代表策略风险越高
        :param profit_list:
        :return:
        """
        Rp = np.array(profit_list)
        VR = math.sqrt(np.sum((Rp - Rp.mean()) ** 2) * 252 / Rp.size)
        return VR

    @classmethod
    def sharp(cls, profit_list):
        """
        夏普比率：可简单理解为每承受一单位风险，会产生多少的超额报酬,
        传入的收益列表是不累加的，单次的，表示单次交易与风险的关系
        :param profit_list: a list
        :return:
        """
        Rp = np.array(profit_list)
        Rp -= cls.Model_Param['RISK_FREE'] / 252.0
        Sharp = math.sqrt(Rp.size) * Rp.mean() / Rp.std()

        # LENp = len(profit)
        # # ERp = profit_list.profit.sum()  # 预期收益
        # # AVGp = ERp / float(LENp)  # 平均收益
        # profit['profit'] -= cls.Model_Param['RISK_FREE'] / 252.0
        # std = profit.profit.std()  # 标准差
        #
        # Sharp = math.sqrt(LENp) * profit.profit.mean() / std
        return Sharp

    @classmethod
    def CAPM(cls, profit_list, index_profit_list):  # 用市场历史已获得收益率计算
        """
        资本资产定价模型, Capital Asset Pricing Model
        计算得出alpha，beta系数
        alpha反应了策略相对于证券市场整体获得的超额收益
        beta反应了个股或某特定的投资组合随大盘变化的敏感程度
        :param profit_list:
        :param index_profit_list:
        :return:
        """
        Ra_ = len(profit_list)
        Rm_ = len(index_profit_list)
        ERa = sum(profit_list) / float(Ra_)  # 投资组合平均收益
        ERm = sum(index_profit_list) / float(Rm_)  # 大盘市场平均收益=无风险收益
        XY = []
        for i in range(Ra_ if Ra_ < Rm_ else Rm_):
            XY.append((profit_list[i] - ERa) * (index_profit_list[i] - ERm))
        Exy = sum(XY) / float(len(XY))  # 目标投资与市场的协方差
        variance = 0
        for p in index_profit_list:
            variance += (p - ERm) ** 2
        delta_m = variance / float(Rm_)  # 大盘市场的方差
        Beta = Exy / delta_m
        # Rp = FinanceIndex.annualized_returns(profit_list)   # 策略年化收益
        Alpha = np.sum(profit_list) - cls.Model_Param['RISK_FREE'] - Beta * (ERm - cls.Model_Param['RISK_FREE'])
        return Alpha, Beta

    @classmethod
    def max_drawdown(cls, profit_list):
        """
        最大回撤率，表示出现的最糟糕的情况亏损了多少,用已获得收益列表计算
        :param profit_list:
        :return:
        """
        pl = len(profit_list)
        if pl < 1:
            return 0
        elif pl == 1:
            return max(profit_list)
        else:
            drawdowm = list()
            for i in range(pl - 1):
                drawdowm.append(max(profit_list[0:i + 2]) - profit_list[i + 1])
            return max(drawdowm)

    @classmethod
    def already_get(cls, profit_list):
        """
        将单次收益累计成已获得收益
        :param profit_list:
        :return:
        """
        sim = 0
        profits = []
        for p in profit_list:
            sim += p
            profits.append(round(sim, 4))
        return profits

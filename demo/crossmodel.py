# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/21 10:22
"""
from Calf import QuantModel
from Calf.indicators import MACD
import pandas as pd


class crossmodel(QuantModel):
    """
    这是一个用于展示Calf框架的使用方法的示例，
    首先创建一个用于实现量化交易的类，这也是开发量化交易策略
    的开端。
    这里我们将要实现的一个策略就是在DIFF向上突破DEA时买入
    """

    def real_signal(self):
        """
        实时任务对于crossmodel来说就是判断最新的那条记录
        是不是满足条件。
        :return:
        """
        data = self.data
        data = MACD(data)  # 加入MACD指标
        data['last_dif'] = data.dif.shift(-1)
        data['last_dea'] = data.dea.shift(-1)
        data.fillna(0, inplace=True)
        if data.last_dif.iloc[0] < data.last_dea.iloc[0] and data.dif.iloc[0] >= data.dea.iloc[0]:
            return data.iloc[0].to_dict(orient='records')
        else:
            return {}
        pass

    def his_signals(self):
        data = self.data
        data = MACD(data)   # 加入MACD指标
        data['last_dif'] = data.dif.shift(-1)
        data['last_dea'] = data.dea.shift(-1)
        data.fillna(0, inplace=True)
        # 剩下的data就是我们想要的买入信号
        data = data[pd.eval('(data.last_dif < data.last_dea) & (data.dif >= data.dea)')]
        # 这样我们就完成了某一个Symbol的历史信号采集
        # 下一步我们将要完成某个市场的某个品种的全部Symbol的历史信号采集
        return data
        pass

    def __init__(self, data):
        self.data = data    # 这是外部传进来的数据，这是为了逻辑与IO分离
        pass
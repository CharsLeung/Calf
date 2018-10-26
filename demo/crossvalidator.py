# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/21 11:58
"""
import datetime as dt
from Calf import ModelValidator, KlineData, ValidVisual
import pandas as pd


class crossvalidator(ModelValidator):
    """
    为了更好的扩展modelvalidator的功能，我们最好单独创建
    一个用于cross模型的类，以满足更多的需求，比如不同与modelvalidator
    提供的默认平仓函数，以及选股函数，具体哪些方法我们可以自定义，请参见
    modelvalidator的文档描述，就cross模型而言，我们选择使用modelvalidator
    默认的方法。
    -----------------------------------------------------------------
    当我们的量化策略通过评审后，下一步我们就在着手实践我们的策略的实时任务了。
    我们就再次回到量化策略的起点位置去一步一步实现，这可能是一个比较繁杂的过程
    """

    @classmethod
    def verify_day_zh(cls):
        """
        我们新建一个方法用于验证cross模型在A股采集的信号的收益，这个方法
        是自定义的，没有什么特殊的要求，但其实现的内容是值得借鉴的.
        :return:
        """
        # data 就是我们在crossaction中采集到的信号集，先前我们已经将它
        # 保存到了一个csv文件中
        data = pd.read_csv('D:traitors.csv')
        data['stock_code'] = data.stock_code.map(lambda x: '0' * (6 - len(str(x))) + str(x))
        data['date'] = pd.to_datetime(data.date)
        # 对于这个信号集，想要使用Calf的回测验证模块，他需要满足一定的格式
        # 它必须至少要包含'code', 'type', 'open_price', 'open_date', 'confidence'
        # 这几个字段，至于这几个字段表示什么意思可以在modelvalidator
        # 中找到解释
        data.rename(columns={'stock_code': 'code', 'close': 'open_price', 'date': 'open_date'}, inplace=True)
        data['type'] = False
        data['confidence'] = 0
        # 下面我们就开始配置Calf的验证单元了
        sd = dt.datetime(2017, 1, 1)
        ed = dt.datetime(2018, 1, 1)
        # 初始化验证器
        crossvalidator.VerifyFrame(data, 'XDXR_day', KlineData.read_data, sd, ed)
        # 配置验证参数
        crossvalidator.modelparammodify(stop_get=0.07, stop_loss=0.05, max_pst_days=4, max_pst_vol=2)
        # 开始验证, 验证函数包括三个：
        # 1）基于日线采集得到的信号
        # dit, menu, goods = crossvalidator.verify_day()
        # 2）基于日内周期（包括15M、30M、60M）采集得到的信号
        # dit, menu, goods = crossvalidator.verify_min()
        # 3）对全部信号进行验证
        goods = crossvalidator.verify_all()
        # 对验证返回的结果进行下一步处理
        goods.to_csv(path_or_buf='D:cross_day_2017_goods.csv', index=False)
        # menu.to_csv(path_or_buf='D:cross_day_2017_menu.csv', index=False)
        # 我们还可以利用validvisual的profit查看收益的折线图
        # validvisual.profit(menu)

crossvalidator.verify_day_zh()
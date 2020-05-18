# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/2/26 15:09
"""
from abc import ABCMeta, abstractmethod
from Calf.exception import WarningMessage


class ModelAction(object):
    """
    模型驱动任务的基类
    此类的主要任务是完成模型实时信号的采集，并将其按用户的模式存入数据库中
    这里所说的数据库是指M模型的一级‘缓存仓库’，它伴随着不同的模型而独立存在
    """
    name = 'XX'  # 模型名称
    klines = []  # 需要监控跟踪的k线（以周期划分）
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def one(self, **kwargs):
        """
        信号数据的采集通常是以证券品种为单元的，这意味着对某一品种的市场来说
        一次完整的信号采集既是对该市场的各个品种单元的一次采集，那么one函数
        就是实现的这个子功能。
        :param kwargs: 参数由子类给出
        :return:返回的是一个描述最新的bar的字典，它可能是一个新的信号，也许
        不是，这个要看具体模型对实时任务的实现，当出现异常的时候建议返回一个
        空的字典
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

    @abstractmethod
    def one_his(self, **kwargs):
        """
        这一过程跟one函数执行的过程十分类似，one_his实现的是对历史信号的采集
        将采集到的信号集形成DataFrame
        :param kwargs:
        :return:
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

    @abstractmethod
    def batch(self, **kwargs):
        """
        batch需要完成的就是对某一品种的整个市场完成一次实时数据采集，其本质就是
        不断地调用one函数，并将one函数返回的得到的结果进行常规的初次筛选，
        然后存入数据库
        :param kwargs:参数由子类给出
        :return:返回的是对本次采集结果的一个描述，它类似于“{‘task’：1，‘result’：
        1，‘time’：1030}”这样的一个字典或其他可序列化的对象，task表示进程标号，
        因为通常在实时任务中我们会使用多进程来完成某一目标，batch可能只承担了
        其中的一部分，所以batch只需要完成对这一部分的描述即可，
        result表示这部分任务所采集到的信号数量，time对应着标的bar的时点
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

    @abstractmethod
    def batch_his(self, **kwargs):
        """
        这一过程跟batch函数执行的过程十分类似，batch_his实现的是对历史信号的采集
        并将最终的结果存入数据库
        :param kwargs:
        :return:
        """
        pass

    # @abstractmethod
    @classmethod
    def real(cls, **kwargs):
        """
        real主要是协调多进程任务进行信号采集，整个系统都是由数据驱动的，时间
        序列向前推进意味着数据的更新，数据的更新将会触发新的操作。
        由外部方法告诉real哪个表的数据更新了，这就会驱使real去采集新好信号，
        当发现有新的信号时通知推荐系统提请推荐，推荐系统的地址默认在net包中
        做出了说明。
        这个方法必须是通过__main()__方法直接调用或间接调用
        :param kwargs:
        :return:
        """
        # raise NotImplementedError('Subclasses must override this method')
        pass

    @classmethod
    def start(cls):
        """
        交易时间前（盘前）执行的函数，这是一个定时任务，它可能会被ModelRun的scheduler
        方法调用，更多信息可以参考ModelRun
        :return:
        """
        # raise NotImplementedError('Subclasses must override this method')
        pass

    @classmethod
    def execute(cls):
        """
        交易时间（盘中）执行的函数，这是一个定时任务，它可能会被ModelRun的scheduler
        方法调用，更多信息可以参考ModelRun
        :return:
        """
        # raise NotImplementedError('Subclasses must override this method')
        pass

    @classmethod
    def end(cls):
        """
        交易日结束(盘后)时执行的函数，这是一个定时任务，它可能会被ModelRun的scheduler
        方法调用，更多信息可以参考ModelRun
        :return:
        """
        # raise NotImplementedError('Subclasses must override this method')
        pass

    @classmethod
    def interval(cls):
        """
        盘中休息执行的函数
        :return:
        """
        # raise NotImplementedError('Subclasses must override this method')
        pass

    @classmethod
    def his(cls, **kwargs):
        """
        his主要是协调多进程任务进行历史信号采集，
        这个方法必须是通过__main()__方法直接调用或间接调用
        :param kwargs:
        :return:
        """

    # @abstractmethod
    @classmethod
    def rmds(cls, data, **kwargs):
        """
        rmds主要实现模型推荐的功能，其目标是将模型一级’缓存仓库‘的信号进行二次筛选，
        将得到的信号推送至signals表，根据客户定义的交易规则为每个订阅客户推荐至
        orders表
        :param data: 这是由real函数发送过来的关于对’缓存仓库‘的信号进行下一步
        处理的指示
        :return:
        """
        pass

    # @abstractmethod
    @classmethod
    def signals_summary(cls, **kwargs):
        """
        每个交易日收盘时统计今日退出的信号的收益情况
        :param kwargs:
        :return:
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

    # @abstractmethod
    @classmethod
    def orders_summary(cls, **kwargs):
        """
        每个交易日收盘时统计今日退出的为客户推荐的信号的收益情况，这些信号都是实际发生了交易的
        在它们退出后需要做一个统计，并将统计结果（类似于{’date’：“2018-01-01”，’profit‘：
        0.01，‘model_from’: 'XX'}）保存在trade_menu表中
        :param kwargs:
        :return:
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

    # @abstractmethod
    @classmethod
    def probing(cls, **kwargs):
        """
        对给出的信号进行实时监控，监控的内容自定义
        :param kwargs:
        :return:
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

    @classmethod
    def is_trade_day(cls, date):
        """
        判断一个日期是否为交易日
        :param date:
        :return: 是交易日返回True，否则返回False
        """
        print(WarningMessage('Subclass not override this method, and return delault value False'))
        return False
        pass

    @classmethod
    def trade_date(cls, date):
        """
        判断一个datetime是否处于日内的交易时间
        :param date:
        :return: True or False
        """
        # raise NotImplementedError('Subclasses must override this method')
        print(WarningMessage('Subclass not override this method, and return delault value False'))
        return False
        pass

    @classmethod
    def trade_day_end(cls, date):
        """
        判断date是否为交易日的收盘时间，因为我们会在这个时间点执行signals_summary、
        orders_summary方法
        :param date:
        :return:
        """
        # raise NotImplementedError('Subclasses must override this method')
        pass

    @classmethod
    def trade_datetime_classifier(cls, date):
        """
        判断一个datetime在一个交易日内所处的阶段，主要可能分为盘前、盘中、盘中休息，盘后
        :param date: datetime
        :return: 盘前(-1),盘中(0),盘后(1),盘中休息(2)
        """
        # raise NotImplementedError('Subclasses must override this method')
        pass

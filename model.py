# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/20 17:39
"""
import datetime as dt
from abc import ABCMeta, abstractmethod

from Calf.exception import ExceptionInfo


class QuantModel(object):
    """
    所有量化模型的基类，一个quantmodel的实例对象可以处理
    某一品种下的某一个Symbol的历史信号、实时信号，这也是
    一个量化模型实例的基本任务。
    -----------------------------------------------------------------
    开发一个量化交易策略在Calf编程模型指导下，应该遵循这样的步骤：
    1) 继承quantmodel类，首先实现his_signals方法，找出data时序K线数据中可
    能存在的历史信号，his_signal可能会被modelaction的one_his调用，总之当你
    想要采集某个市场的全部历史信号时，我们建议你遵循这样的编程流程：
    quantmodel.his_signals-->modelaction.one_his-->modelaction.batch_his
    -->数据库-->modelvalidator.
    2)当你的量化交易模型通过评审后，你就可能需要采集实时信号了，对于实时信号，
    我们建议你遵循这样的开发流程：
    quantmodel.real_signal-->modelaction.one-->modelaction.batch-->
    数据库-->modelaction.real-->modelaction.rmds-->signals表或orders表。
    还有其他的编程规范可以参见相应接口的文档描述。
    """
    __metaclass__ = ABCMeta
    clm = list()    # 返回的信号（实时模式）或信号集（历史模式）所包含的字段

    def __init__(self, data, **kwargs):
        """
        :param data: 用于计算历史或实时信号的K线数据,这是
        K线数据进入量化模型的唯一合法方式。data必然是一个时间序列数据，
        同时我们强烈建议把data组织成一个DataFrame。
        :param kwargs:
        """
        self.data = data    #
        pass

    @abstractmethod
    def real_signal(self):
        """
        采集data这一数据集的实时信号（即判断最新一条记录是否满足模型的规则）
        :return:返回一个关于这个实时信号的dict（若存在），或空的{}
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

    @abstractmethod
    def his_signals(self):
        """
        采集data这一数据集的历史信号，即判断历史上所有满足模型规则的信号集，
        并把这个信号集封装成一个DataFrame作为返回对象
        :return:
        """
        raise NotImplementedError('Subclasses must override this method')
        pass

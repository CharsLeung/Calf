# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/2/7 17:30
@describe：量化交易分析模型，适用于在python3环境下开发量化策略的研究员

量化交易模型开发框架（我们将这个项目命名为Calf，以后统称Calf）是一个广泛适用的证券量化交易策略开发框架，
Calf贯穿整个量化交易策略的生命周期，它提供了从源数据的组织管理到策略模型开发、策略信号回测验证、策略实时
运行、策略优化路径等一系列的指导规范。Calf系统由Python语言实现，内部广泛使用pandas、numpy数据结构，并
强烈建议使用Calf的开发者使用pandas、numpy这两个数据结构，有关它们的参考文档，你可以在：https://scipy.org/docs.html
找到；此外我们建议Python语言开发者认真学习领会Pythonic精神要义，有关Python的编码风格你可以在：
http://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/contents/找到。
"""
from os.path import abspath, dirname

# 必须在顶级包中加入下面这行代码，并且是在代码文件的最开始
project_dir = dirname(dirname(abspath(__file__))) # Calf项目的安装路径

# 检查运行Calf的平台是否为python3
import platform
pv = platform.python_version()
if int(pv[0]) >= 3:
    pass
else:
    raise EnvironmentError('Calf only support python3')

# Calf用到了这些依赖(可能还包括其他的)，可能用户没有
# 建议开发人员首先安装Anaconda3平台
# TODO(leungjain): pygame包以及相关功能被暂时移除
# TODO(leungjian): pandas_datareader提供的有关读数据的功能有可能被替换
hard_dependencies = ("pandas", "pandas_datareader", "pymongo",
                     "business_calendar", "pytz", "apscheduler")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(dependency)

if missing_dependencies:
    # 注意，如果开发人员自建了与系统环境中相同名称的包，可能会抛出包引入异常
    #
    raise ImportError(
        "Missing required dependencies {0}".format(missing_dependencies))
del hard_dependencies, dependency, missing_dependencies

import pandas
from Calf.sys_config import config
from Calf.date_time import CalfDateTime
from Calf.data import *
from Calf.modelfinance import FinanceIndex
from Calf.modelaction import ModelAction
from Calf.modelrun import ModelRun
from Calf.modelrmds import recsys
from Calf.ugly import ugly
from Calf.model import QuantModel
from Calf.verification import *
from Calf.realkit import RealKit

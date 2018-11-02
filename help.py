# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/7/20 11:39
"""
"""
Calf主要分为一下几个部分：
1、数据IO，包括K线数据->所有以K线图列示的数据，这些信息都在data包下，
关于存储K线数据的表名需要提前配置在KLINE_MODEL_TABLE函数中，
未在该函数中出现的将不能通过KlineData对象进行数据IO。有关K线数据的
IO详细信息，可以在Calf->data->klinedata中找到。另外一个常用的IO
工具是ModelData，这是一个通用、广延（查询条件灵活、不用提前配置表名）
的IO接口，凡是关于MongoDB数据库的访问都可以通过这个对象完成。
关于ModelData更详细的信息可以在Calf->data->modeldata中找到。
data包下针对几个特定的任务添加了一下受限的IO
接口，例如OrderData、SignalData。还用从新浪接口读取A股、H股实时
数据的RealData，其中还用读取美股实时数据的部分。
2、
"""
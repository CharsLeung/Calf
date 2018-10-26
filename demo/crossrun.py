# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/4/28 14:14
"""
import datetime as dt
from Calf.demo.crossaction import CrossAction
from Calf import ModelRun

if __name__ == '__main__':
    ModelRun.scheduler(CrossAction, start_date='9:25', execute_date='9:30-11:30 13:00-15:00', end_date='15:05',
                       execute_interval=300, tz='China/Shanghai')

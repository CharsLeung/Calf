# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/2/26 17:29
"""
import datetime
from os.path import abspath, pardir, join
from sys import path

from Calf import project_dir

path.append(abspath(join(abspath(join(abspath(__file__), pardir)), pardir)))
log_file_path = project_dir + '/Files/'


def runninglog(func):
    def spam(*args):
        print('----')
        func(*args)

    return spam


class ServerLog:
    @classmethod
    def write_log_file(cls, file_name='_log', message='', **kw):
        try:
            _to = open(log_file_path + file_name, 'a+')
            now = datetime.datetime.now()
            _to.write(str(now) + ' ' + message + str(kw) + '\n')
            _to.close()
        except Exception as e:
            print(e)

    @classmethod
    def print_log(cls, file_name='_log', *args, **kw):
        try:
            # _to = open(log_file_path + file_name, 'a+')
            print(args)
        except Exception as e:
            print(e)


# @runninglog
# def f():
#     print('as')
#
# f()
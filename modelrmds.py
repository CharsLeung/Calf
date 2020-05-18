# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/2/27 10:07
"""
import socket
import sys
import datetime as dt

from Calf.exception import ExceptionInfo
from Calf.utils import fontcolor
from Calf.net import MODEL_PROBE, STATUS


class recsys:
    """
    recommend system 模型推荐系统，其主要任务是将模型一级‘缓存仓库’的数据
    进行二次筛选后引入signals表，按客户定义的交易规则推荐至orders表
    """
    HOST = ''  # 默认监听地址（本地）
    PORT = MODEL_PROBE['port']  # 默认监听端口
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp

    @classmethod
    def run(cls, ma, host=None, port=None):
        """

        :return:
        """
        print()
        try:
            if host is None and port is None:
                cls.SERVER.bind((cls.HOST, cls.PORT))
            else:
                cls.SERVER.bind((host, port))
            cls.SERVER.listen(10)
            print(fontcolor.F_GREEN + '-' * 80)
            print('Model recommendation system started')
            print('Datetime:%s' % dt.datetime.now())
            print('-' * 80 + fontcolor.END)
        except Exception as e:
            print(fontcolor.F_RED + '-' * 80)
            print('Model recommendation system failed to start. error code : ' + str(e))
            print('-' * 80 + fontcolor.END)
            sys.exit()
        while 1:
            print('Waiting for a new request···')
            conn, address = cls.SERVER.accept()
            print('Received request from:' + address[0] + ':' + str(address[1]) + ' Datetime:', dt.datetime.now())
            data = conn.recv(1024)
            data = str(data, encoding="utf-8")
            # print(data)
            data = eval(data)
            try:
                conn.sendall(bytes(STATUS['success']))
                ma.rmds(data)
            except Exception as e:
                ExceptionInfo(e)
            finally:
                conn.close()
        cls.SERVER.close()
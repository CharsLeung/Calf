# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/2/26 17:21
"""
import socket
import sys
import datetime as dt
from Calf.exception import ExceptionInfo
from Calf.utils import fontcolor
from ..net import STATUS


class ModelClient:
    @classmethod
    def ClientFrame(cls, info):
        cls.info = info
        try:
            # 获取本机电脑名
            cls.host = socket.getfqdn(socket.gethostname())
            # 获取本机ip
            cls.ip = socket.gethostbyname(cls.host)
            # create an AF_INET, STREAM socket (TCP)
            cls.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cls.socket.settimeout(10)
        except socket.error as msg:
            print('Failed to create socket. Error code: ' + str(msg[0]) +
                  ' , Error message : ' + msg[1])
            sys.exit()

    @classmethod
    def send(cls):

        try:
            cls.socket.connect((cls.info['ip'], cls.info['port']))
            m = cls.info['message']
            m['host'] = cls.host
            m['from'] = cls.ip
            message = bytes(str(m), encoding="utf8")
            # Set the whole string
            cls.socket.sendall(message)
            # print('Message send successfully')
            reply = str(cls.socket.recv(1024), encoding='utf-8')
            # print(reply)
            return reply
        except socket.error:
            print('Send failed')
            return 'Error'

    def __init__(self, address: dict):
        """
        :param address: eg:{'ip':'127.0.0.1',port:50001}
        """
        self.address = address
        try:
            # 获取本机电脑名
            self.host = socket.getfqdn(socket.gethostname())
            # 获取本机ip
            self.ip = socket.gethostbyname(self.host)
            # create an AF_INET, STREAM socket (TCP)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
        except socket.error as msg:
            print('Failed to create socket. Error code: ' + str(msg[0]) +
                  ' , Error message : ' + msg[1])
            sys.exit()

    def transmit(self, message: dict):
        """
        :param message:
        :return:
        """
        try:
            self.socket.connect((self.info['ip'], self.info['port']))
            m = message
            m['host'] = self.host
            m['from'] = self.ip
            message = bytes(str(m), encoding="utf8")
            # Set the whole string
            self.socket.sendall(message)
            # print('Message send successfully')
            reply = str(self.socket.recv(1024), encoding='utf-8')
            # print(reply)
            return reply
        except socket.error:
            print('Send failed')
            return 500


def notice(address, **kw):
    """
    网络通知，address为需要通知的目的地址
    :param address: eg:{'ip':'127.0.0.1',port:50001}
    :param kw:
    :return:
    """
    now = dt.datetime.now()
    must_data = {'date': str(now), 'status': STATUS['success']}
    must_data = dict(must_data, **kw)
    message = {'message': must_data}
    info = dict(address, **message)
    ModelClient.ClientFrame(info)
    return ModelClient.send()

class BroadCast:
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    status = True

    def __init__(self, port=50014):
        self.PORT = port
    
    def accept(self, callback):
        
        try:
            BroadCast.skt.bind(('', self.PORT))
            print(fontcolor.F_GREEN + '-' * 80)
            print('Listening for broadcast at ', BroadCast.skt.getsockname())
            print('Datetime:%s' % dt.datetime.now())
            print('-' * 80 + fontcolor.END)
        except Exception as e:
            print(fontcolor.F_RED + '-' * 80)
            print('Broadcast system failed to start. error '
                  'code : ' + str(e))
            print('-' * 80 + fontcolor.END)
            sys.exit()
        # print('Listening for broadcast at ', skt.getsockname())

        while True:
            if BroadCast.status is not True:
                break
            print('Waiting for a new broadcast...')
            data, address = BroadCast.skt.recvfrom(65535)
            print(fontcolor.F_GREEN + '-' * 80)
            print('Received broadcast from:{0}, datetime: {1}'.format(
                address, dt.datetime.now()))
            print('-' * 80 + fontcolor.END)
            rec = data.decode('utf-8')
            try:
                callback(rec)
            except Exception as e:
                ExceptionInfo(e)
        BroadCast.status = True

    def broading(self, message:str):
        try:
            network = '<broadcast>'
            BroadCast.skt.sendto(message.encode('utf-8'), (network, self.PORT))
            print(fontcolor.F_GREEN + '-' * 80)
            print('Broadcast success, datetime: ', dt.datetime.now())
            print('-' * 80 + fontcolor.END)
        except Exception as e:
            ExceptionInfo(e)

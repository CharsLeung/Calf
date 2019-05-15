# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2019-05-06 15:34
"""
import socket, os, struct
import socketserver, re


def send_file(fn, ip='127.0.0.1', port=50017):
    """
    :param fn: path of file
    :param ip:
    :param port:
    :return: str request of server
    """
    if os.path.isfile(fn):
        f = open(fn, 'rb')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
            struct.calcsize('128sl')  # 定义打包规则
            # 定义文件头信息，包含文件名和文件大小
            v1 = bytes(str(os.path.basename(fn)), encoding='utf-8')
            v2 = os.stat(fn).st_size
            f_head = struct.pack('128sl', v1, v2)
            s.send(f_head)
            while True:
                byte = f.read(1024)
                if not byte:
                    break
                s.send(byte)
            _ = s.recv(1024)
            _ = str(_, encoding='utf-8')
        except Exception as e:
            print(e)
            _ = None
        finally:
            f.close()
            s.close()
            return _
            pass
    else:
        raise IOError("this file don't exit.")
    pass


class FileServer(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server, dir=''):
        super(FileServer, self).__init__(request, client_address, server)
        self.dir = dir
        pass

    def handle(self):
        pass



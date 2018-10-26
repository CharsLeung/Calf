# -*- coding: utf-8 -*-

import json

from . import LazyProperty
from .. import project_dir


class Market(object):
    config_file = project_dir + '\config.json'

    def __init__(self, TradeX, server_name):
        self.server_name = server_name
        with open(self.config_file) as f:
            self.ms = json.loads(f.read())[server_name]
        self.TX = TradeX
        self._connect = None

    @LazyProperty
    def connect(self):
        host = self.ms['host']
        port = int(self.ms['port'])
        retry = True
        while retry:
            try:
                if self.server_name == 'market_a_server':
                    self._connect = self.TX.TdxHq_Connect(host, port)
                else:
                    self._connect = self.TX.TdxExHq_Connect(host, port)
            except Exception as e:
                print(e)
                print('retry')
            else:
                retry = False
        self._connect.SetTimeout(5000, 5000)
        print(u'\n\t连接成功\t{host}:{port}\n'.format(host=host, port=port))
        return self._connect

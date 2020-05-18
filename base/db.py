# -*- coding: utf-8 -*-

from pymongo import *
import json

from Calf import project_dir

# 构建一个默认的MongoDB对象置于项目运行的内存当中，避免频繁
# 的创建MongoDB对象
config_file = project_dir + '/Calf/db_config.json'
try:
    with open(config_file) as f:
        l = f.read()
        a = json.loads(l)
        db = a['default']

    fields = db.keys()
    if 'username' in fields and 'password' in fields and ('@' in db[
        'username'] or '@' in db['password']):
        if 'dbname' in fields:
            dbname = db.pop('dbname')
        else:
            dbname = None
        _ = db['host'].split(':')
        db['host'] = _[0]
        db['port'] = int(_[1])
        if 'replicaset' in fields:
            db['replicaSet'] = db.pop('replicaset')
        if 'dbauth' in fields:
            db['authSource'] = db.pop('dbauth')
        db['connectTimeoutMS'] = 2000
        connection = MongoClient(**db)
        mongodb = connection[db['dbname']] if dbname is not None else None
        pass
    else:
        uri = 'mongodb://'
        if 'username' in fields and 'password' in fields:
            uri += '{username}:{password}@'.format(
                username=db['username'],
                password=db['password'])
        # ip是必须的
        uri += db['host']
        # if 'port' in fields:
        #     uri += ':%s' % db['port']
        uri += '/?connectTimeoutMS=2000'
        if 'replicaset' in fields:
            uri += ';replicaSet=%s' % db['replicaset']
        if 'dbauth' in fields:
            uri += ';authSource=%s' % db['dbauth']
        print('db-uri:', uri)
        connection = MongoClient(uri)
        if 'dbname' in fields:
            mongodb = connection[db['dbname']]
        else:
            mongodb = None
except Exception as e:
    print(e)
    raise Exception('connection MongoDB raise a error')


class MongoDB:
    """数据库对象"""
    connection_count = 0
    # 为了避免连续访问相同的数据库对象，设置location、connection
    # 两个类属性，保留最近一次访问的对象
    location = None
    connection = None
    db_name = None

    @classmethod
    def db_connection(cls, location, db_name=None):
        """
        连接到数据库
        :param db_name:
        :param location:
        :return:
        """
        try:
            if location == cls.location and cls.connection is not None:
                # 这个连接对象已经存在
                if db_name is not None:
                    return cls.connection[db_name]
                else:
                    # 正常情况下，cls.connection不为空的时候，cls.db_name
                    # 也不为空
                    return cls.connection[cls.db_name]
            else:
                with open(config_file) as cf:
                    buffer = cf.read()
                    jn = json.loads(buffer)
                    db_ = jn[location]
                fields = db_.keys()
                if 'username' in fields and 'password' in fields and (
                        '@' in db_['username'] or '@' in db_['password']):
                    if 'dbname' in fields:
                        dbname = db_.pop('dbname')
                    else:
                        dbname = None
                    _ = db_['host'].split(':')
                    db_['host'] = _[0]
                    db_['port'] = int(_[1])
                    if 'replicaset' in fields:
                        db_['replicaSet'] = db_.pop('replicaset')
                    if 'dbauth' in fields:
                        db_['authSource'] = db_.pop('dbauth')
                    db_['connectTimeoutMS'] = 2000
                    connection = MongoClient(**db_)
                    # mongodb = connection[db['dbname']] if dbname is not None else None
                    pass
                else:
                    uri = 'mongodb://'
                    if 'username' in fields and 'password' in fields:
                        uri += '{username}:{password}@'.format(
                            username=db_['username'],
                            password=db_['password'])
                    # ip是必须的
                    uri += db_['host']
                    # if 'port' in fields:
                    #     uri += ':%s' % db_['port']
                    if 'dbname' in fields:
                        dbname = db_.pop('dbname')
                    else:
                        dbname = None
                    uri += '/?connectTimeoutMS=2000'
                    if 'replicaset' in fields:
                        uri += ';replicaSet=%s' % db_['replicaset']
                    if 'dbauth' in fields:
                        uri += ';authSource=%s' % db_['dbauth']

                    print('new db-uri:', uri)
                    connection = MongoClient(uri)
                tn = db_name if db_name is not None else dbname
                cls.location = location
                cls.connection = connection
                cls.db_name = tn
                return connection[tn]
        except Exception:
            raise Exception('connection MongoDB raise a error')

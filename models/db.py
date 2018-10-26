# # -*- coding: utf-8 -*-

# from pymongo import *
# from . import LazyProperty

# class DB(object):
#     def __init__(self, host, port, dbname, username=None, password=None):
#         self.protocal = 'mongodb://'
#          if username is not None:
#             self.user = '{username}:{password}@'.format(username=username, password=password)
#             self.authorisation = '?authoSource={dbname}'.format(dbname=dbname)
#         else:
#             self.user = None
#             self.authorisation = None
#         self.dbname = '/{dbname}'.format(dbname)
#         self.db = '{host}:{port}'.format(host=host, port=port)

#         self.uri = '{}{}{}'.format(self.protocal, self.db) 
#         if self.user is not None:
#             self.uri = '{}{}{}{}'.format(self.protocal, self.user, self.db):
#         if self.authorisation is not None: 
#            self.uri += self.authorisation
#         self.connection = None

#     def __repr__(self):
#         return '{}{}/{}'.format(self.protocal, self.db, self.db)

#     @LazyProperty
#     def connect(self):
#         self.connection = MongoClient(self.uri)
#         return self.connection[self.dbname]

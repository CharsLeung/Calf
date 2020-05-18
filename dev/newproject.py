# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/12/14 10:11
"""
import os
from Calf.utils import File
from Calf import project_dir


class NewProject:

    def __init__(self, location, packages=None):
        self.location = location
        self.packages = ['model', 'verify']
        if packages is not None:
            self.packages += packages
        pass

    def create(self):
        try:
            os.makedirs(self.location)
            os.makedirs(self.location + '\doc')
            File.copy_file(project_dir + '\Calf\dev\MDR.docx',
                           self.location + '\\' + 'doc\MDR.docx')
            for p in self.packages:
                os.makedirs(self.location + '\{}'.format(p))
                os.mknod(self.location + '\{}\__init__.py'.format(p))
            pass
        except Exception:
            os.removedirs(self.location)
            raise Exception
        finally:
            pass


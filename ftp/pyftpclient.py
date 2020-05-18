# encoding: utf-8

"""
project = Calf
file_name = pyftpclient
author = Administrator
datetime = 2020/5/18 0018 上午 11:03
from = office desktop
"""
from ftplib import FTP


class FtpClient:

    def __init__(self, ip, port, user, pwd, bufferSize=1024, **kwargs):
        self.ftp = FTP()
        self.ftp.set_debuglevel(2)
        self.ftp.connect(ip, port)
        self.ftp.login(user, pwd)
        self.bufferSize = bufferSize
        print(self.ftp.getwelcome())
        pass

    # def files(self):
    #     fs = []
    #     dirs = self.ftp.dir()
    #     print(12)
    #     for d in dirs:
    #         self.ftp.cwd(d)
    #         fs += self.ftp.nlst()
    #         pass

    def push(self, local_path, remote_path):
        with open(local_path, 'rb') as local:
            self.ftp.storbinary(
                'STOR {}'.format(remote_path),
                local, self.bufferSize
            )
            pass

    def pull(self, local_path, remote_path):
        with open(local_path, 'wb') as local:
            self.ftp.retrbinary(
                'RETR {}'.format(remote_path),
                local.write, self.bufferSize
            )
            pass


# if __name__ == "__main__":
#     fr = FtpReader(
#         '125.83.84.183',
#         21,
#         'Chubby',
#         'j3PxqH2tvK0J-ftp'
#     )
#     # fr.files()
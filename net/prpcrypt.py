# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/9 11:37
"""
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class prpcrypt:
    def __init__(self, key):
        l = len(key)
        if 6 <= l <= 16:
            self.key = key + ('\0' * (16 - l))
        else:
            raise Exception('this key must be 6-16 characters')
        self.mode = AES.MODE_CBC
        self.ciphertext = None

    def encrypt(self, text):
        """
         加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
        :param text:
        :return:
        """
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        """
        解密函数
        :param text:
        :return:
        """
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = str(cryptor.decrypt(a2b_hex(text)), encoding="utf-8")
        return plain_text.rstrip('\0')


# if __name__ == '__main__':
#     pc = prpcrypt('key')  # 初始化密钥
#     e = pc.encrypt("00000")
#     d = pc.decrypt(e)
#     print(e, d)
#     e = pc.encrypt("00000000000000000000000000")
#     d = pc.decrypt(e)
#     print(e, d)
# from Crypto.Hash import MD5
#
# obj = MD5.new()
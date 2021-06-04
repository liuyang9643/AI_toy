import os
import time
import hashlib
import requests
from uuid import uuid4

from setting import MongoDB, LT_URL, QRCODE_PATH


# 创建二维码 根据 DeviceKey 创建二维码
# 创建二维码


def create_device(count):
    """
    生成count数量的二维码，首先从产生随机的Key，然后存入MongoDB，
    并调用产生二维码的接口生成二维码文件保存到data下的qrcode目录
    :param count: 生产二维码数量
    :return: None
    """
    for i in range(count):
        devicekey = hashlib.md5(f"{uuid4()}{time.time()}{uuid4()}".encode("utf8")).hexdigest()
        MongoDB.devices.insert_one({"device_key": devicekey})
        res = requests.get(LT_URL % devicekey).content
        device_img = os.path.join(QRCODE_PATH, f"{devicekey}.jpg")
        time.sleep(1)
        with open(device_img, "wb") as f:
            f.write(res)


if __name__ == '__main__':
    create_device(20)

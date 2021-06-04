import os
from redis import Redis
from aip import AipSpeech
from pymongo import MongoClient

# 采集喜马拉雅数据需要的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/77.0.3865.90 Safari/537.36"
}
# 从移动端的喜马拉雅获取数据的URL
CONTENT_LIST_URL = "https://m.ximalaya.com/m-revision/common/album/queryAlbumTrackRecordsByPage?\
                    albumId=%s&page=%s&pageSize=20"

# 获取图片的BaseURl
IMAGE_HOST = "http://imagev2.xmcdn.com/"

# 联图二维码配置
# LT_URL = "http://qr.topscan.com/api.php?text=%s"
LT_URL = "https://api.pwmqr.com/qrcode/create/?url=%s"

# 封面路径
COVER_PATH = os.path.join("data", "cover")
# 音频文件存放路径
MUSIC_PATH = os.path.join("data", "music")
# 头像存储路径
AVATAR_PATH = os.path.join("data", "avatar")
# 二维码存放路径
QRCODE_PATH = os.path.join("data", "qrcode")
# 聊天文件存放路径
CHAT_PATH = os.path.join("data", "chat")

# Mongo数据库配置
client = MongoClient("mongodb://139.224.215.199:27017/")
client.admin.authenticate("username", "password", mechanism='SCRAM-SHA-1')
MongoDB = client["80AI"]

# Redis配置
RDB = Redis(host='139.224.215.199', port=****, password="******", db=15)

# Return Base Template配置
RET = {"code": 0, "msg": "", "data": {}}

# 百度AI配置
APP_ID = '17367879'
API_KEY = 'u7LlCY0sK6GGKtC7lnTsgELW'
SECRET_KEY = 'lmFBMjDnybe2nY7A3yWq1nl73Z9kGG21'
SPEECH_CLIENT = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

VOICE = {
    "spd": 4,
    'vol': 5,
    "pit": 7,
    "per": 4
}

# 小思机器人 思知公司
BOT_URL = 'https://api.ownthink.com/bot?appid=a7031c72a71101579ee2fcf8e36abeac&userid=%s&spoken=%s'

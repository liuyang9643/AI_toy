import os
from flask import Blueprint, jsonify, send_file

from setting import MongoDB, RET, COVER_PATH, MUSIC_PATH, AVATAR_PATH, QRCODE_PATH, CHAT_PATH

get_anything = Blueprint("get_anything", __name__)


# 获取首页内容
@get_anything.route("/get_content_list", methods=["POST"])
def get_content_list():
    content_list = list(MongoDB.contents.find({}).limit(10))

    # 解决ObjectId无法被JSON序列化的问题
    for index, item in enumerate(content_list):
        content_list[index]["_id"] = str(item.get("_id"))

    RET["code"] = 0
    RET["msg"] = "获取内容列表"
    RET["data"] = content_list

    return jsonify(RET)


# 获取音乐封面
@get_anything.route("/get_cover/<filename>")
def get_cover(filename):
    file_path = os.path.join(COVER_PATH, filename)
    return send_file(file_path)


# 获取音乐内容
@get_anything.route("/get_music/<filename>")
def get_music(filename):
    file_path = os.path.join(MUSIC_PATH, filename)
    return send_file(file_path)


# 获取头像
@get_anything.route("/get_avatar/<filename>")
def get_avatar(filename):
    file_path = os.path.join(AVATAR_PATH, filename)
    return send_file(file_path)


# 获取玩具二维码
@get_anything.route("/get_qr/<filename>")
def get_qr(filename):
    file_path = os.path.join(QRCODE_PATH, filename)
    return send_file(file_path)


# 获取聊天语音内容
@get_anything.route("/get_chat/<filename>")
def get_chat(filename):
    file_path = os.path.join(CHAT_PATH, filename)
    return send_file(file_path)

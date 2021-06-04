import time
from bson import ObjectId
from flask import Blueprint, jsonify, request

from setting import MongoDB, RET
from baidu_ai import text2audio
from redis_msg import get_redis_msg, get_redis_msg_app

chat = Blueprint("chat", __name__)


# 获取聊天信息列表
@chat.route("/chat_list", methods=["POST"])
def chat_list():
    chat_info = request.form.to_dict()
    chat_window = MongoDB.chats.find_one({"_id": ObjectId(chat_info.get("chat_id"))})

    get_redis_msg_app(chat_info.get("sender"), chat_info.get("receiver"))

    RET["code"] = 0
    RET["msg"] = "查询聊天记录"
    RET["data"] = chat_window.get("chat_list")

    return jsonify(RET)


# 接收消息
@chat.route("/recv_msg", methods=["POST"])
def recv_msg():
    # 查询聊天窗口
    chat_info = request.form.to_dict()

    # 获取当前sender receiver 的未读或离线消息
    sender, count = get_redis_msg(chat_info.get("sender"), chat_info.get("receiver"))

    chat_window = MongoDB.chats.find_one({"user_list": {"$all": [sender, chat_info.get("receiver")]}})
    if count != 0:
        chat_one = chat_window.get("chat_list")[-count:]  # type:list
        chat_one.reverse()

        remark = "陌人生"
        toy = MongoDB.toys.find_one({"_id": ObjectId(chat_info.get("receiver"))})
        for friend in toy.get("friend_list"):
            if friend.get("friend_id") == sender:
                remark = friend.get("friend_remark")

        xxtx = text2audio(f"以下是来自{remark}的消息")
        xxtx_dict = {
            "sender": sender,
            "receiver": chat_info.get("receiver"),
            "chat": xxtx,
            "createTime": time.time()
        }
        chat_one.append(xxtx_dict)

        return jsonify(chat_one)

    else:
        xxtx = text2audio(f"你还没有收到消息哦")
        xxtx_dict = {
            "sender": "ai",
            "receiver": chat_info.get("receiver"),
            "chat": xxtx,
            "createTime": time.time()
        }
        return jsonify([xxtx_dict])

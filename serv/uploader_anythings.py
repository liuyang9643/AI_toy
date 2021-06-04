import os
import time
from uuid import uuid4
from bson import ObjectId
from flask import Blueprint, jsonify, request

from redis_msg import set_redis_msg
from baidu_ai import text2audio, audio2text, my_nlp
from setting import MongoDB, RET, AVATAR_PATH, CHAT_PATH

up_anything = Blueprint("up_anything", __name__)


# 接收用户上传的头像并保存
@up_anything.route("/avatar_uploader", methods=["POST"])
def avatar_uploader():
    avatar = request.files.get("avatar")
    file_path = os.path.join(AVATAR_PATH, avatar.filename)
    avatar.save(file_path)

    RET["code"] = 0
    RET["msg"] = "头像上传成功"
    RET["data"] = {"filename": avatar.filename}

    return jsonify(RET)


# 接收APP上传的语音消息
@up_anything.route("/app_uploader", methods=["POST"])
def app_uploader():
    # 分别获取发送者接收者和录音文件
    receiver = request.form.get("receiver")
    sender = request.form.get("sender")
    record_file = request.files.get("reco")
    record_filename = record_file.filename
    new_file = os.path.join(CHAT_PATH, record_filename)
    record_file.save(new_file)

    # 转换为MP3文件
    os.system(f"ffmpeg -i {new_file} {new_file}.mp3")

    # 将聊天信息格式化并存储到MongoDB中
    chat = {
        "sender": sender,
        "receiver": receiver,
        "chat": f"{record_filename}.mp3",
        "createTime": time.time()
    }
    user_list = [sender, receiver]
    MongoDB.chats.update_one({"user_list": {"$all": user_list}}, {"$push": {"chat_list": chat}})

    # 消息提醒：
    # 你有来自 remark 的消息 ，发件人 在 收件人 通讯录中的 remark
    # 查询收件人
    remark = "陌人生"
    toy = MongoDB.toys.find_one({"_id": ObjectId(receiver)})
    for friend in toy.get("friend_list"):
        if friend.get("friend_id") == sender:
            remark = friend.get("friend_remark")

    xxtx = text2audio(f"你有来自{remark}的消息")

    # 将信息存储在redis中，等待玩具开机查看
    set_redis_msg(sender, receiver)

    RET["code"] = 0
    RET["msg"] = "上传成功"
    RET["data"] = {"filename": xxtx, "friend_type": "app"}

    return jsonify(RET)


# 接收玩具上传的语音消息，流程同上，对应前端的"发送语音消息"
@up_anything.route("/toy_uploader", methods=["POST"])
def toy_uploader():
    sender = request.form.get("sender")
    receiver = request.form.get("receiver")
    file = request.files.get("reco")
    filename = f"{uuid4()}.wav"

    file_path = os.path.join(CHAT_PATH, filename)
    file.save(file_path)

    chat = {
        "sender": sender,
        "receiver": receiver,
        "chat": filename,
        "createTime": time.time()
    }

    MongoDB.chats.update_one({"user_list": {"$all": [sender, receiver]}}, {"$push": {"chat_list": chat}})

    set_redis_msg(sender, receiver)

    remark = "陌人生"
    xxtx = "Unknow"
    toy = MongoDB.toys.find_one({"_id": ObjectId(receiver)})
    if toy:
        for friend in toy.get("friend_list"):
            if friend.get("friend_id") == sender:
                remark = friend.get("friend_remark")

        xxtx = text2audio(f"你有来自{remark}的消息")

    ret = {
        "code": 0,
        "msg": "上传成功",
        "data":
            {
                "filename": xxtx,
                "friend_type": "toy"
            }
    }

    return jsonify(ret)


# 接收玩具上传的语音消息，对应前端的"发送指令"
@up_anything.route("/ai_uploader", methods=["POST"])
def ai_uploader():
    """
    file = request.files.get("reco")
    reco是录音文件，这个接口用于孩子和玩具对话信息处理，对应前端的发送指令
    :return:
    """
    toy_id = request.form.get("toy_id")
    file = request.files.get("reco")
    filename = f"{uuid4()}.wav"
    file_path = os.path.join(CHAT_PATH, filename)
    file.save(file_path)

    # eg：file --> 我要给爸爸发消息 --> audio2text解析 -->
    text = audio2text(file_path)
    res = my_nlp(text, toy_id)

    return jsonify(res)

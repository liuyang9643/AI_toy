from bson import ObjectId
from flask import Blueprint, jsonify, request

from setting import MongoDB, RET

device = Blueprint("device", __name__)


# 扫码绑定玩具
@device.route("/scan_qr", methods=["POST"])
def scan_qr():
    device_key = request.form.to_dict()
    # 查询当前的设备编号是否已经授权
    device_info = MongoDB.devices.find_one(device_key)
    # 授权的
    if device_info:
        toy_info = MongoDB.toys.find_one(device_key)
        if toy_info:
            RET["code"] = 2
            RET["msg"] = f"请求添加{toy_info.get('toy_name')}为好友"
            RET["data"] = {"toy_id": str(toy_info.get("_id"))}
            return jsonify(RET)

        RET["code"] = 0
        RET["msg"] = "来啦老板"
        RET["data"] = device_key

        return jsonify(RET)
    # 未授权的Device
    else:
        RET["code"] = 1
        RET["msg"] = "你花钱买玩具了吗？"
        RET["data"] = {}

        return jsonify(RET)


# 对玩具进行绑定
@device.route("/bind_toy", methods=["POST"])
def bind_toy():
    device_info = request.form.to_dict()
    device_info["avatar"] = "toy.jpg"
    device_info["bind_user"] = device_info.pop("user_id")

    user_info = MongoDB.users.find_one({"_id": ObjectId(device_info["bind_user"])})

    # user_list 中缺少 用户的_id
    chat_window = MongoDB.chats.insert_one({"user_list": [], "chat_list": []})

    device_info["friend_list"] = [
        {
            "friend_id": device_info["bind_user"],
            "friend_nick": user_info.get("nickname"),
            "friend_remark": device_info.pop("remark"),
            "friend_avatar": user_info.get("avatar"),
            "friend_chat": str(chat_window.inserted_id),
            "friend_type": "app"
        }
    ]

    toy = MongoDB.toys.insert_one(device_info)

    toy_id = str(toy.inserted_id)
    # 获取到了toy_id 那么chats表中的 user_list 就有数据了
    user_list = [device_info["bind_user"], toy_id]
    MongoDB.chats.update_one({"_id": chat_window.inserted_id}, {"$set": {"user_list": user_list}})

    # 既然用户已经是玩具的好友了 ，那么用户要不要添加玩具为好友呢？
    user_add_toy = {
        "friend_id": toy_id,
        "friend_nick": device_info.get("baby_name"),
        "friend_remark": device_info.get("toy_name"),
        "friend_avatar": device_info.get("avatar"),
        "friend_chat": str(chat_window.inserted_id),
        "friend_type": "toy"
    }

    MongoDB.users.update_one({"_id": ObjectId(device_info["bind_user"])},
                             {"$push": {"bind_toys": toy_id, "friend_list": user_add_toy}})

    RET["code"] = 0
    RET["msg"] = "老板再来一个呗~"
    RET["data"] = {}

    return jsonify(RET)


# 玩具开机
@device.route("/open_toy", methods=["POST"])
def open_toy():
    device_info = request.form.to_dict()
    is_device = MongoDB.devices.find_one(device_info)

    # 是否为授权设备
    if is_device:
        toy = MongoDB.toys.find_one(device_info)
        # 是否已经与用户发生绑定关系
        if toy:
            toy_ret = {
                "code": 0,
                "music": "Success.mp3",
                "toy_id": str(toy.get("_id")),
                "name": toy.get("toy_name")
            }

            return jsonify(toy_ret)
        # 设备存在但未和用户发生绑定关系
        else:
            toy_ret = {
                "code": 1,
                "music": "Nobind.mp3"
            }

            return jsonify(toy_ret)
    # 设备未经授权 或 (devicekey 异常) 请联系经销商
    else:
        toy_ret = {
            "code": 2,
            "music": "Nolic.mp3"
        }

        return jsonify(toy_ret)


# 获取玩具列表
@device.route("/toy_list", methods=["POST"])
def toy_list():
    user_id = request.form.get("_id")
    toylist = list(MongoDB.toys.find({"bind_user": user_id}))

    for index, item in enumerate(toylist):
        toylist[index]["_id"] = str(item.get("_id"))

    RET["code"] = 0
    RET["msg"] = "获取Toy列表"
    RET["data"] = toylist

    return jsonify(RET)

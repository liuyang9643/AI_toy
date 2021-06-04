from bson import ObjectId
from flask import Blueprint, jsonify, request

from setting import MongoDB, RET

friend = Blueprint("friend", __name__)


# 添加好友请求
@friend.route("/add_req", methods=["POST"])
def add_req():
    """
    请求信息格式如下
    {
    "_id" : ObjectId("5ca5bfbaea512d269449ed1b"), // 自动生成ID
    "add_user" : "5ca17c7aea512d26281bcb8d", // 发起好友申请方 有可能app / toy
    "toy_id" : "5ca17f85ea512d215cd9b079", // 收到好友申请方
    "add_user_type" : "toy", // 发起方的用户类型 app/toy
    "req_info" : "我是仇视单", // 请求信息
    "remark" : "园园", // 发起方对接收方的好友备注
    "status" : 1, // 请求状态 1同意 0未处理 2拒绝

    "toy_name" : "圆圆" // 接收方的名称
    "avatar" : "toy.jpg", // 发起方的头像
    "nickname" : "背背", // 发起方的名称
}
    :return:
    """
    request_info = request.form.to_dict()

    request_info["status"] = 0
    request_info["toy_name"] = MongoDB.toys.find_one({"_id": ObjectId(request_info.get("toy_id"))}).get("toy_name")

    if request_info.get("add_user_type") == "toy":
        add_user = MongoDB.toys.find_one({"_id": ObjectId(request_info.get("add_user"))})
    else:
        add_user = MongoDB.users.find_one({"_id": ObjectId(request_info.get("add_user"))})

    request_info["avatar"] = add_user.get("avatar")
    request_info["nickname"] = add_user.get("nickname") if add_user.get("nickname") else add_user.get("toy_name")

    # 存储 request_info 数据
    MongoDB.request.insert_one(request_info)

    RET["code"] = 0
    RET["msg"] = "添加好友请求成功"
    RET["data"] = {}

    return jsonify(RET)


# 获取好友请求列表
@friend.route("/req_list", methods=["POST"])
def req_list():
    user_id = request.form.get("_id")

    # 查询 request 数据表
    user_bind_toy = MongoDB.users.find_one({"_id": ObjectId(user_id)}).get("bind_toys")
    # 查询绑定玩具收到的好友请求
    req_info_list = list(MongoDB.request.find({"toy_id": {"$in": user_bind_toy}, "status": 0}))

    # 解决 ObjectId 无法被 JSON 的问题
    for index, item in enumerate(req_info_list):
        req_info_list[index]["_id"] = str(item.get("_id"))

    RET["code"] = 0
    RET["msg"] = "查询好友请求"
    RET["data"] = req_info_list

    return jsonify(RET)


# 同意添加好友
@friend.route("/acc_req", methods=["POST"])
def acc_req():
    req_id = request.form.get("req_id")
    remark = request.form.get("remark")  # 接收方对发起方的称呼

    # 查询请求
    req_info = MongoDB.request.find_one({"_id": ObjectId(req_id)})
    re_remark = req_info.get("remark")  # 发起方对接收方的称呼

    # 接收方的数据 toy
    toy = MongoDB.toys.find_one({"_id": ObjectId(req_info.get("toy_id"))})

    # 发起方的数据 app / toy
    if req_info.get("add_user_type") == "toy":
        add_user = MongoDB.toys.find_one({"_id": ObjectId(req_info.get("add_user"))})
    else:
        add_user = MongoDB.users.find_one({"_id": ObjectId(req_info.get("add_user"))})

    # 创建聊天窗口
    chat_window = MongoDB.chats.insert_one(
        {"user_list": [req_info.get("add_user"), req_info.get("toy_id")], "chat_list": []})

    # 同意添加好友 双方通讯录中必须存在对方的数据
    add_user_add_toy = {
        "friend_id": req_info.get("toy_id"),
        "friend_nick": toy.get("toy_name"),
        "friend_remark": re_remark,
        "friend_avatar": toy.get("avatar"),
        "friend_chat": str(chat_window.inserted_id),
        "friend_type": "toy"
    }  # 发起方添加接收方

    toy_add_add_user = {
        "friend_id": str(add_user.get("_id")),
        "friend_nick": add_user.get("toy_name") if add_user.get("toy_name") else add_user.get("nickname"),
        "friend_remark": remark,
        "friend_avatar": add_user.get("avatar"),
        "friend_chat": str(chat_window.inserted_id),
        "friend_type": req_info.get("add_user_type")
    }

    # 更改通讯录
    # 接收方的通讯录 toy
    MongoDB.toys.update_one({"_id": ObjectId(req_info.get("toy_id"))}, {"$push": {"friend_list": toy_add_add_user}})

    # 发起方的通讯录 app / toy
    if req_info.get("add_user_type") == "toy":
        MongoDB.toys.update_one({"_id": ObjectId(req_info.get("add_user"))},
                                {"$push": {"friend_list": add_user_add_toy}})
    else:
        MongoDB.users.update_one({"_id": ObjectId(req_info.get("add_user"))},
                                 {"$push": {"friend_list": add_user_add_toy}})

    # req_info 的status
    MongoDB.request.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 1}})

    RET["code"] = 0
    RET["msg"] = "同意添加好友"
    RET["data"] = {}

    return jsonify(RET)


# 拒绝添加好友
@friend.route("/ref_req", methods=["POST"])
def ref_req():
    req_id = request.form.get("req_id")
    MongoDB.request.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 2}})

    RET["code"] = 0
    RET["msg"] = "拒绝添加好友"
    RET["data"] = {}

    return jsonify(RET)


# 获取好友列表
@friend.route("/friend_list", methods=["POST"])
def friend_list():
    user_id = ObjectId(request.form.get("_id"))

    user_info = MongoDB.users.find_one({"_id": user_id})

    RET["code"] = 0
    RET["msg"] = "好友查询"
    RET["data"] = user_info.get("friend_list")

    return jsonify(RET)

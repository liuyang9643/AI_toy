from bson import ObjectId
from flask import Blueprint, jsonify, request

from setting import MongoDB, RET
from redis_msg import get_redis_msg_all

user = Blueprint("user", __name__)


# 用户注册接口
@user.route("/reg", methods=["POST"])
def reg():
    user_info = request.form.to_dict()
    user_info["bind_toys"] = []
    user_info["friend_list"] = []
    MongoDB.users.insert_one(user_info)

    RET["code"] = 0
    RET["msg"] = "注册成功"
    RET["data"] = {}

    return jsonify(RET)


# 用户登录接口
@user.route("/login", methods=["POST"])
def login():
    user_info = request.form.to_dict()
    cur_user = MongoDB.users.find_one(user_info)

    cur_user["_id"] = str(cur_user["_id"])
    cur_user.pop("password")
    RET["code"] = 0
    RET["msg"] = "登录成功"
    RET["data"] = cur_user
    return jsonify(RET)


# 用户自动登录接口，可以通过_id自动登录
@user.route("/auto_login", methods=["POST"])
def auto_login():
    user_info = request.form.to_dict()
    user_info["_id"] = ObjectId(user_info.get("_id"))
    cur_user = MongoDB.users.find_one(user_info)
    cur_user["_id"] = str(cur_user.get("_id"))

    cur_user.pop("password")
    cur_user["chat"] = get_redis_msg_all(cur_user["_id"])

    RET["code"] = 0
    RET["msg"] = "登录成功"
    RET["data"] = cur_user

    return jsonify(RET)

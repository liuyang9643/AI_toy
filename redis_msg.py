import json
from setting import RDB


# 通过Redis缓存消息
def set_redis_msg(sender, receiver):
    """
    Redis存储格式如下：
    接收者：{发送者n：消息数量}
    receiver：{sender1:3，sender2:5...}
    """
    receiver_msg = RDB.get(receiver)

    # 已经存在数据不能去覆盖 只能追加
    if receiver_msg:
        receiver_msg_dict = json.loads(receiver_msg)
        if receiver_msg_dict.get(sender):  # 当前数据中 已经存在了sender的未读离线消息
            receiver_msg_dict[sender] += 1
            receiver_msg = json.dumps(receiver_msg_dict)
            RDB.set(receiver, receiver_msg)

        # 不存在 sender 的数据
        else:
            receiver_msg_dict[sender] = 1
            receiver_msg = json.dumps(receiver_msg_dict)
            RDB.set(receiver, receiver_msg)

    # 数据不存在 随便覆盖
    else:
        receiver_msg = json.dumps({sender: 1})
        RDB.set(receiver, receiver_msg)


# 获取一个人未读消息。并将未读消息清零
def get_redis_msg(sender, receiver):
    receiver_msg = RDB.get(receiver)
    if receiver_msg:
        receiver_msg_dict = json.loads(receiver_msg)
        count = receiver_msg_dict.get(sender, 0)
        if count == 0:
            for new_sender, c in receiver_msg_dict.items():
                if c != 0:
                    sender = new_sender
                    count = c
        receiver_msg_dict[sender] = 0  # 一次性收取全部消息

    else:
        count = 0
        receiver_msg_dict = {sender: 0}

    RDB.set(receiver, json.dumps(receiver_msg_dict))

    return sender, count


# 获取一个人未读消息。并将未读消息清零 app专用
def get_redis_msg_app(sender, receiver):
    receiver_msg = RDB.get(receiver)
    if receiver_msg:
        receiver_msg_dict = json.loads(receiver_msg)
        receiver_msg_dict[sender] = 0  # 一次性收取全部消息

    else:
        receiver_msg_dict = {sender: 0}

    RDB.set(receiver, json.dumps(receiver_msg_dict))


def get_redis_msg_all(receiver):
    receiver_msg = RDB.get(receiver)
    if receiver_msg:
        receiver_msg_dict = json.loads(receiver_msg)
        count = sum(receiver_msg_dict.values())
        receiver_msg_dict["count"] = count
    else:
        receiver_msg_dict = {"count": 0}

    return receiver_msg_dict

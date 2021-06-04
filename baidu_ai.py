import os
import requests
from uuid import uuid4
from bson import ObjectId
from my_content import my_xiangsidu
from pypinyin import lazy_pinyin, TONE3
from setting import SPEECH_CLIENT, VOICE, CHAT_PATH, MongoDB, BOT_URL


# 语音合成，此函数中的内容都为百度提供，详见https://ai.baidu.com/ai-doc/SPEECH/Ck4nlz91i
def text2audio(text):
    # 通过百度提供的接口将文本转换为语音
    result = SPEECH_CLIENT.synthesis(text, 'zh', 1, VOICE)

    # 识别正确则 返回二进制格式的语音 错误则返回带有错误信息的dict
    filename = f"{uuid4()}.mp3"
    file_path = os.path.join(CHAT_PATH, filename)
    if not isinstance(result, dict):
        with open(file_path, 'wb') as f:
            f.write(result)

    return filename


# 通过ffmpeg将MP3格式的文件转换为pcm，因为百度不支持MP3文件
def get_file_content(filepath):
    os.system(f"ffmpeg -y  -i {filepath} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filepath}.pcm")
    with open(f"{filepath}.pcm", 'rb') as fp:
        return fp.read()


# 语音识别，详见https://ai.baidu.com/ai-doc/SPEECH/Dk4o0bmkl
def audio2text(file_path):
    res = SPEECH_CLIENT.asr(get_file_content(file_path), 'pcm', 16000, {
        'dev_pid': 1536,
    })
    text = res.get("result")[0]
    return text


# 思知机器人智能对话，类似小爱同学，详见https://www.ownthink.com/
def go2bot(text, toy_id):
    res = requests.get(BOT_URL % (toy_id, text))
    res_data = res.json()
    tx = res_data.get("data").get("info").get("text")
    return tx


def my_nlp(text, toy_id):
    """
    :param text:用户输入的语音信息的文本
    :param toy_id:来自哪个玩具的信息
    :return:不同情况返回不同信息
    """

    # text == "我要给爸爸发消息"
    if "发消息" in text or "聊聊天" in text:
        toy_info = MongoDB.toys.find_one({"_id": ObjectId(toy_id)})
        text_pinyin = "".join(lazy_pinyin(text, TONE3))
        for friend in toy_info.get("friend_list"):
            # 通过pinyin处理人名通音情况，例如（贝贝 and 蓓蓓），通过读音将只会识别出贝贝
            remark_pinyin = "".join(lazy_pinyin(friend.get("friend_remark"), TONE3))
            nick_pinyin = "".join(lazy_pinyin(friend.get("friend_nick"), TONE3))
            if remark_pinyin in text_pinyin or nick_pinyin in text_pinyin:
                # 通关语音合成告诉前端可以发送消息了
                filename = text2audio(f"可以向{friend.get('friend_remark')}发送消息了")
                receiver = friend.get("friend_id")
                return {"chat": filename, "sender": receiver, "friend_type": friend.get("friend_type")}

    # text = "我想听雪宝宝"
    if "我想听" in text or "我要听" in text or "来一首" in text:
        text = text.replace("我想听", "")
        text = text.replace("我要听", "")
        text = text.replace("来一首", "")
        # 通过文本相似度来判断孩子想听那首歌
        content = my_xiangsidu(text)
        return {"sender": "ai", "music": content.get("music")}

    # 如果不是上述两种情况，通过思知机器人进行智能对话，类似小爱同学，详见https://www.ownthink.com/
    bot_res = go2bot(text, toy_id)
    filename = text2audio(bot_res)
    return {"sender": "ai", "chat": filename}

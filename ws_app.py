import json
from flask_cors import CORS
from flask import Flask, request
from geventwebsocket.websocket import WebSocket
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WSGIServer  # 替换Wer原始的WSGI

# 创建application并配置跨域
app = Flask(__name__)
CORS(app, supports_credentials=True)


# 用于存放当前存在的WebSocket客户端
socket_dict = {}


@app.route("/ws/<username>")
def ws(username):
    sock = request.environ.get("wsgi.websocket")  # type:WebSocket
    if sock:
        socket_dict[username] = sock
    else:
        return "请使用ws"
    print(len(socket_dict), socket_dict)
    while True:
        msg = sock.receive()  # 发送的消息必须为 json 格式
        # print(msg)
        msg_dict = json.loads(msg)
        receiver = msg_dict.get("receiver")
        rece_sock = socket_dict.get(receiver)
        rece_sock.send(msg)


if __name__ == '__main__':
    http_server = WSGIServer(("0.0.0.0", 9528), app, handler_class=WebSocketHandler)
    http_server.serve_forever()

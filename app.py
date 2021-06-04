from flask import Flask
from flask_cors import CORS
from flask import render_template

from serv.chats import chat
from serv.users import user
from serv.devices import device
from serv.friends import friend
from serv.get_anythings import get_anything
from serv.uploader_anythings import up_anything

app = Flask(__name__)

# app.config["DEBUG"] = True

# 配置跨域
CORS(app, supports_credentials=True)

# 注册蓝图
app.register_blueprint(get_anything)
app.register_blueprint(user)
app.register_blueprint(up_anything)
app.register_blueprint(device)
app.register_blueprint(friend)
app.register_blueprint(chat)


# 测试玩具的页面
@app.route("/toy")
def toy():
    return render_template("toy.html")


if __name__ == '__main__':
    app.run("0.0.0.0", 9527)
    #  6c6802d05b22759a20f9d30a62785577
    # 10.34.130.211

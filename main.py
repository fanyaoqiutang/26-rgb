from flask import Flask
from flask_cors import CORS
from config import SERVER_HOST, SERVER_PORT
# 导入接口蓝图
from api.tourist_api import tourist_bp
from api.admin_api import admin_bp
from api.common_api import common_bp

app = Flask(__name__)
CORS(app)  # 跨域，前后端分离必备

# 注册接口路由
app.register_blueprint(tourist_bp, url_prefix="/api/tourist")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(common_bp, url_prefix="/api/common")

@app.route("/")
def index():
    return "景区AI数字人导览系统 服务已启动"

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
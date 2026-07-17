from flask import Flask, render_template
from flask_cors import CORS
from config import SERVER_HOST, SERVER_PORT
from api.tourist_api import tourist_bp
from api.admin_api import admin_bp
from api.common_api import common_bp

app = Flask(__name__)
CORS(app)

# 注册接口路由
app.register_blueprint(tourist_bp, url_prefix="/api/tourist")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(common_bp, url_prefix="/api/common")

# ====================== 前端页面路由 ======================
@app.route('/')
def tourist_page():
    return render_template('tourist.html')

@app.route('/admin/login')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/admin')
def admin_home():
    return render_template('admin_index.html')

@app.route('/admin/knowledge')
def admin_kb_page():
    return render_template('admin_kb.html')

@app.route('/admin/human')
def admin_human_page():
    return render_template('admin_human.html')

@app.route('/admin/dashboard')
def admin_dash_page():
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    print(f"景区AI数字人导览系统启动: http://{SERVER_HOST}:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
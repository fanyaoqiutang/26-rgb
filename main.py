from flask import Flask, request, jsonify, send_from_directory, render_template_string
from api.tourist_api import tourist_bp
from api.admin_api import admin_bp
from api.common_api import common_bp
import os
# http://localhost:3000数字人
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
app.secret_key = "scenic_digital_human_2024"

app.register_blueprint(tourist_bp, url_prefix="/api/tourist")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(common_bp, url_prefix="/api/common")

@app.route("/")
def index():
    return render_template_string(open('templates/tourist.html', encoding='utf-8').read())

CHARACTER_PAGE = """
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>景区数字人</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    overflow: hidden;
  }
  .character {
    width: 300px;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 20px 40px rgba(0,0,0,0.3));
    cursor: pointer;
    transition: transform 0.3s;
  }
  .character:hover { transform: scale(1.05); }
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
  }
  .sparkle {
    position: absolute; width: 6px; height: 6px;
    background: white; border-radius: 50%;
    animation: sparkle 2s ease-in-out infinite; opacity: 0;
  }
  .sparkle:nth-child(1) { top: 20%; left: 15%; animation-delay: 0s; }
  .sparkle:nth-child(2) { top: 60%; left: 80%; animation-delay: 0.5s; }
  .sparkle:nth-child(3) { top: 80%; left: 25%; animation-delay: 1s; }
  .sparkle:nth-child(4) { top: 30%; left: 70%; animation-delay: 1.5s; }
  @keyframes sparkle {
    0%, 100% { opacity: 0; transform: scale(0); }
    50% { opacity: 1; transform: scale(1); }
  }
</style>
</head>
<body>
  <div class="sparkle"></div><div class="sparkle"></div>
  <div class="sparkle"></div><div class="sparkle"></div>
  <img src="/static/picture.png" class="character" alt="景区数字人">
</body>
</html>
"""

@app.route("/character")
def character_page():
    return render_template_string(CHARACTER_PAGE)

@app.route("/tourist")
def tourist_page():
    return render_template_string(open('templates/tourist.html', encoding='utf-8').read())

@app.route("/admin_login")
def admin_login_page():
    return render_template_string(open('templates/admin_login.html', encoding='utf-8').read())

@app.route("/admin")
def admin_page():
    return render_template_string(open('templates/admin.html', encoding='utf-8').read())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

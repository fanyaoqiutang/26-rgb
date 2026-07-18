景区 AI 数字人导览系统
基于 Python Flask + Milvus RAG 知识库 + 语音 ASR/TTS + SadTalker 数字人开发
一、环境前置安装
必备软件
Python 3.10（推荐，AI 依赖兼容性最佳）
MySQL 8.0
Node.js 18 及以上（用于 Vue 前端）
Git
数据库可视化工具（Navicat/DBeaver，用于手动执行建表 SQL）
二、项目拉取
# 克隆远程仓库
git clone https://github.com/fanyaoqiutang/26-rgb.git
cd 26-rgb
三、本地配置文件修改
打开项目根目录 config.py，修改数据库与大模型密钥配置：
MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "填写你本地MySQL的root密码",
    "database": "scenic_digital_human",
    "charset": "utf8mb4"
}
# 填入自己申请的免费大模型API Key
LLM_API_KEY = "你的大模型key"
LLM_API_URL = "对应模型接口地址"
注意：config.py 已加入.gitignore，不会上传个人密钥，每位组员本地自行修改。

四、手动创建数据库与数据表（核心步骤）
步骤 1：启动 MySQL 服务
Win+R 输入 services.msc，找到 MySQL 服务并右键启动。
步骤 2：Navicat 手动执行建表脚本
打开 Navicat，新建 MySQL 连接
主机：127.0.0.1，端口 3306，用户名 root，密码填本地 MySQL 密码
点击【测试连接】，连接成功后保存
右键连接名 → 新建数据库
数据库名：scenic_digital_human
字符集：utf8mb4，排序规则：utf8mb4_unicode_ci
双击打开 scenic_digital_human 数据库（名称高亮代表选中）
顶部菜单：文件 → 运行 SQL 文件
选择项目路径：database/tables.sql，点击开始执行
执行完成后右键数据库【刷新】，左侧表列表出现 5 张表即完成：
admin_user、kb_document、chat_record、daily_visit_stat、digital_human_config
内置默认账号
后台管理员账号：admin，密码：123456

初次运行执行 vector_milvus.py 自动生成向量库。

手动下载开源数字人项目
https://gitee.com/chen_jian1994/awesome-digital-human-live2d/repository/archive/develop.zip
解压后放入项目根目录

系统前置依赖：FFmpeg
winget install Gyan.FFmpeg

终端在虚拟环境中
输入 cd live2d_digital\web 跳转到数字人项目目录
npm install
# 如果不行就 npm install --legacy-peer-deps --registry=https://registry.npmmirror.com
npm run dev

五、后端 Python 环境初始化
1. 创建并激活虚拟环境
# 创建虚拟环境
python -m venv venv

# Windows激活环境
venv\Scripts\activate

# Mac/Linux激活环境
source venv/bin/activate
激活成功后终端前缀出现 (venv)。
2. 安装全部依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
六、知识库初始化（灵山胜境景区资料）
将景区 Word 文档放入目录：docs/scenic_files/
执行知识库初始化脚本，自动解析文档并存入 Milvus 向量库
python init_kb.py
控制台输出入库文本片段数量，代表知识库构建完成。
七、启动后端服务
虚拟环境保持激活状态，执行：
bash
运行
python main.py
控制台输出 Running on http://127.0.0.1:5000 代表后端接口启动成功。
八、前端页面启动
1. 游客移动端 H5
cd frontend_h5
npm install
npm run dev
2. 景区管理后台
cd frontend_admin
npm install
npm run dev
终端打印本地访问地址，浏览器打开即可使用。
十、系统功能验证
游客端：支持文字提问、录音语音提问，自动生成数字人对口型讲解视频；
管理后台：使用 admin / 123456 登录，可管理知识库、查看游客对话日志、查看访问数据大屏。
十一、团队协作说明
database/tables.sql 统一提交 Git，后续表结构变更更新该文件，所有人重新手动执行 SQL 同步表；
虚拟环境 venv、node_modules、模型缓存、音视频临时文件均已配置.gitignore，不会上传仓库；
每人本地独立 MySQL 数据库，无需共用远程库。
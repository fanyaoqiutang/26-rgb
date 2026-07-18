-- =============================================
-- 景区AI数字人导览项目 数据库初始化脚本
-- 数据库名：scenic_digital_human
-- 执行前请确保MySQL服务已启动
-- =============================================

-- 1. 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS scenic_digital_human 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

-- 切换到目标数据库
USE scenic_digital_human;

-- =============================================
-- 2. 建表：管理员账号表
-- =============================================
CREATE TABLE IF NOT EXISTS admin_user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '管理员登录账号',
    password VARCHAR(255) NOT NULL COMMENT 'MD5加密后的密码',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='后台管理员账号表';

-- 初始化默认管理员账号：admin / 密码：123456
INSERT IGNORE INTO admin_user (username, password) 
VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e');

-- =============================================
-- 3. 建表：景区知识库文档表
-- =============================================
CREATE TABLE IF NOT EXISTS kb_document (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    doc_title VARCHAR(255) NOT NULL COMMENT '文档/景点名称',
    doc_content TEXT COMMENT '文档正文内容',
    category VARCHAR(50) DEFAULT '景点介绍' COMMENT '分类：景点介绍/历史文化/游玩贴士/FAQ',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景区知识库文档表';

-- =============================================
-- 4. 建表：游客对话记录表
-- =============================================
CREATE TABLE IF NOT EXISTS chat_record (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_input TEXT NOT NULL COMMENT '游客提问内容',
    ai_answer TEXT NOT NULL COMMENT 'AI数字人回答内容',
    emotion_tag VARCHAR(20) DEFAULT '中性' COMMENT '情绪标签：正面/中性/负面',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '对话时间',
    visit_date DATE DEFAULT (CURRENT_DATE) COMMENT '访问日期（用于统计）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='游客对话记录表';

-- =============================================
-- 5. 建表：每日访问统计表
-- =============================================
CREATE TABLE IF NOT EXISTS daily_visit_stat (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    visit_date DATE UNIQUE NOT NULL COMMENT '统计日期',
    chat_count INT DEFAULT 0 COMMENT '当日对话总次数',
    user_count INT DEFAULT 0 COMMENT '当日服务人次',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日访问统计表';

-- =============================================
-- 6. 建表：数字人形象配置表
-- =============================================
--CREATE TABLE IF NOT EXISTS digital_human_config (
--    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
--    config_name VARCHAR(100) NOT NULL COMMENT '配置名称，如：古风导游',
--    face_image_path VARCHAR(255) NOT NULL COMMENT '数字人人脸底图路径',
--    voice_type VARCHAR(50) DEFAULT 'zh-CN-XiaoxiaoNeural' COMMENT 'TTS音色标识',
--    costume_style VARCHAR(50) COMMENT '服装风格描述',
--    is_default TINYINT DEFAULT 0 COMMENT '是否默认启用：0否 1是',
--    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
--) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数字人形象配置表';

-- =============================================
-- 执行完成后，执行下面语句验证：
-- SHOW TABLES;
-- =============================================
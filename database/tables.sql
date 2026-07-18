-- =============================================
-- 景区AI数字人导览系统 数据库初始化脚本
-- 数据库名：scenic_digital_human
-- MySQL 8.0+
-- =============================================

CREATE DATABASE IF NOT EXISTS scenic_digital_human
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE scenic_digital_human;

-- =============================================
-- 1. 管理员表
-- =============================================
CREATE TABLE IF NOT EXISTS admin_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录账号',
    password VARCHAR(255) NOT NULL COMMENT 'MD5密码',
    role VARCHAR(20) DEFAULT 'admin' COMMENT '角色：admin/super',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME COMMENT '最后登录时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员账号表';

INSERT IGNORE INTO admin_user (username, password, role)
VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin');

-- =============================================
-- 2. 知识库文档表
-- =============================================
CREATE TABLE IF NOT EXISTS kb_document (
    id INT PRIMARY KEY AUTO_INCREMENT,
    doc_title VARCHAR(255) NOT NULL COMMENT '文档标题',
    doc_content TEXT NOT NULL COMMENT '文档内容',
    category VARCHAR(50) DEFAULT '景点介绍' COMMENT '分类',
    source VARCHAR(50) DEFAULT '手动录入' COMMENT '来源：手动录入/文件导入',
    vector_synced TINYINT DEFAULT 0 COMMENT '是否已同步向量库：0否 1是',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文档表';

-- =============================================
-- 3. 游客会话表（每次访问生成一个会话）
-- =============================================
CREATE TABLE IF NOT EXISTS visitor_session (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL UNIQUE COMMENT '会话唯一标识',
    visitor_tag VARCHAR(50) DEFAULT '通用游客' COMMENT '游客标签：通用/历史/自然/文化/亲子',
    ip_address VARCHAR(50) COMMENT '游客IP',
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '会话开始时间',
    end_time DATETIME COMMENT '会话结束时间',
    chat_count INT DEFAULT 0 COMMENT '该会话对话次数',
    INDEX idx_start_time (start_time),
    INDEX idx_visitor_tag (visitor_tag)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='游客会话表';

-- =============================================
-- 4. 对话记录表
-- =============================================
CREATE TABLE IF NOT EXISTS chat_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) COMMENT '所属会话ID',
    user_input TEXT NOT NULL COMMENT '游客提问',
    ai_answer TEXT NOT NULL COMMENT 'AI回答',
    input_type VARCHAR(10) DEFAULT 'text' COMMENT '输入方式：text/voice',
    emotion_tag VARCHAR(20) DEFAULT '中性' COMMENT '情感：正面/中性/负面',
    audio_url VARCHAR(255) COMMENT 'TTS音频路径',
    visit_date DATE DEFAULT (CURRENT_DATE) COMMENT '访问日期',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_visit_date (visit_date),
    INDEX idx_emotion (emotion_tag),
    INDEX idx_session (session_id),
    INDEX idx_input_type (input_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话记录表';

-- =============================================
-- 5. 每日统计表
-- =============================================
CREATE TABLE IF NOT EXISTS daily_visit_stat (
    id INT PRIMARY KEY AUTO_INCREMENT,
    visit_date DATE UNIQUE NOT NULL COMMENT '统计日期',
    chat_count INT DEFAULT 0 COMMENT '对话总次数',
    user_count INT DEFAULT 0 COMMENT '服务人次（会话数）',
    text_count INT DEFAULT 0 COMMENT '文字输入次数',
    voice_count INT DEFAULT 0 COMMENT '语音输入次数',
    positive_count INT DEFAULT 0 COMMENT '正面情感数',
    negative_count INT DEFAULT 0 COMMENT '负面情感数',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_visit_date (visit_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日访问统计表';

-- =============================================
-- 6. 数字人配置表
-- =============================================
CREATE TABLE IF NOT EXISTS digital_human_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_name VARCHAR(100) NOT NULL COMMENT '配置名称',
    face_image_path VARCHAR(255) COMMENT '形象图片路径',
    voice_type VARCHAR(50) DEFAULT 'zh-CN-XiaoyiNeural' COMMENT 'TTS音色',
    costume_style VARCHAR(100) COMMENT '服装风格',
    is_default TINYINT DEFAULT 0 COMMENT '是否默认：0否 1是',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数字人配置表';

INSERT IGNORE INTO digital_human_config (config_name, voice_type, is_default)
VALUES ('灵山导游', 'zh-CN-XiaoyiNeural', 1);

-- =============================================
-- 7. 系统配置表（扩展用）
-- =============================================
CREATE TABLE IF NOT EXISTS system_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_desc VARCHAR(255) COMMENT '配置说明',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- =============================================
-- 验证
-- =============================================
-- SHOW TABLES;

CREATE DATABASE IF NOT EXISTS scenic_digital_human DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE scenic_digital_human;

-- 景区知识库表
CREATE TABLE IF NOT EXISTS scenic_knowledge (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    content TEXT NOT NULL COMMENT '景点讲解文本',
    tag VARCHAR(100) DEFAULT '通用' COMMENT '分类标签：历史/自然风光/美食',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 游客交互记录表
CREATE TABLE IF NOT EXISTS interact_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_question TEXT COMMENT '游客提问',
    ai_answer TEXT COMMENT '数字人回答',
    emotion VARCHAR(20) COMMENT '情感标签 calm/happy/sad',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 数字人全局配置表
CREATE TABLE IF NOT EXISTS digital_human_cfg (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dh_name VARCHAR(50) COMMENT '数字人名称',
    voice VARCHAR(100) COMMENT 'TTS音色',
    style VARCHAR(50) COMMENT '形象风格'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
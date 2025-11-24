-- SQL Schema for Ucollet Database (MySQL)
-- Generated from SQLAlchemy models

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    domicile VARCHAR(255),
    photo_url VARCHAR(255),
    total_points INT DEFAULT 0,
    level VARCHAR(50) DEFAULT 'Bronze',
    total_waste_amount FLOAT DEFAULT 0.0,
    total_deposits INT DEFAULT 0,
    trees_grown INT DEFAULT 0,
    eco_xp INT DEFAULT 0,
    eco_tree_ready BOOLEAN DEFAULT FALSE,
    streak_current INT DEFAULT 0,
    streak_longest INT DEFAULT 0,
    last_deposit_date DATE,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_id (id)
);

CREATE TABLE waste_deposits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE DEFAULT (CURRENT_DATE),
    waste_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount FLOAT DEFAULT 1.0,
    points_earned INT DEFAULT 0,
    via VARCHAR(20) DEFAULT 'manual',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_waste_deposits_id (id)
);

CREATE TABLE eco_tree_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tree_number INT NOT NULL,
    bonus_points INT DEFAULT 0,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_eco_tree_history_id (id)
);

CREATE TABLE voucher_redemptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nominal INT NOT NULL,
    points_spent INT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_voucher_redemptions_id (id)
);

CREATE TABLE education_contents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    summary TEXT,
    body TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_education_contents_id (id)
);

CREATE TABLE quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_id INT,
    question TEXT NOT NULL,
    options_text TEXT NOT NULL,
    correct_index INT NOT NULL,
    points_reward INT DEFAULT 10,
    FOREIGN KEY (content_id) REFERENCES education_contents(id),
    INDEX idx_quiz_questions_id (id)
);

CREATE TABLE quiz_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES quiz_questions(id),
    INDEX idx_quiz_answers_id (id)
);

CREATE TABLE mission_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    mission_code VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    claimed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_mission_claims_id (id)
);
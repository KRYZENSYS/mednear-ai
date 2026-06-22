-- ============================================
-- MedNear AI - PostgreSQL Initial Setup
-- ============================================

-- Create database (run as superuser)
-- CREATE DATABASE mednear_ai;
-- CREATE USER mednear_user WITH PASSWORD 'mednear_pass';
-- GRANT ALL PRIVILEGES ON DATABASE mednear_ai TO mednear_user;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Tables will be created by Alembic migrations on first run

-- Useful indexes (created by Alembic in models, but here's the SQL for reference)
-- CREATE INDEX idx_users_telegram_id ON users(telegram_id);
-- CREATE INDEX idx_chats_user_id ON chats(user_id);
-- CREATE INDEX idx_messages_chat_id ON messages(chat_id);
-- CREATE INDEX idx_ai_history_user_id ON ai_history(user_id);
-- CREATE INDEX idx_medicine_reminders_user_id ON medicine_reminders(user_id);
-- CREATE INDEX idx_hospitals_location ON hospitals(latitude, longitude);
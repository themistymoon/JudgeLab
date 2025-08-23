-- Initialize PostgreSQL database for JudgeLab
-- This script runs when the database container starts

-- Ensure the database exists
CREATE DATABASE judgelab;

-- Create a role for the application (if not exists)
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'judgelab') THEN

      CREATE ROLE judgelab LOGIN PASSWORD 'judgelab_dev';
   END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE judgelab TO judgelab;

-- Connect to the judgelab database
\c judgelab;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO judgelab;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO judgelab;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO judgelab;
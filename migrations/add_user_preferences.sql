-- Migration: Add preferences column to users table
-- Description: Adds a JSONB column to store user preferences (theme, language, layout, etc)
-- Date: 2025-11-16

-- Add preferences column (JSONB type, default empty object)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'::jsonb;

-- Add index for faster lookups (GIN index works with JSONB)
CREATE INDEX IF NOT EXISTS idx_users_preferences 
ON users USING GIN (preferences);

-- Update existing users to have empty preferences object
UPDATE users 
SET preferences = '{}'::jsonb 
WHERE preferences IS NULL;

-- Add comment to column for documentation
COMMENT ON COLUMN users.preferences IS 'User preferences stored as JSONB (theme, language, layout, notifications, etc)';


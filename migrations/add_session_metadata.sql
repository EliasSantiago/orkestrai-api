-- Migration: Add metadata fields to conversation_sessions table
-- Date: 2025-11-18
-- Purpose: Add support for session metadata (title, description, avatar, pinned, etc.)

DO $$ 
BEGIN 
    -- Add session_metadata JSONB column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversation_sessions' AND column_name = 'session_metadata'
    ) THEN
        ALTER TABLE conversation_sessions 
        ADD COLUMN session_metadata JSONB DEFAULT '{}'::jsonb;
        
        COMMENT ON COLUMN conversation_sessions.session_metadata IS 'Session metadata (title, description, avatar, pinned, etc.)';
    END IF;
    
    -- Add index for metadata queries
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_conversation_sessions_metadata'
    ) THEN
        CREATE INDEX idx_conversation_sessions_metadata 
        ON conversation_sessions USING GIN (session_metadata);
    END IF;
END $$;


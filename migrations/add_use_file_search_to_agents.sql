-- Migration: Add use_file_search column to agents table
-- Date: 2025-11-09
-- Purpose: Allow agents to opt-in/opt-out of File Search (RAG) functionality

-- Add column only if it doesn't exist (idempotent)
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'agents' AND column_name = 'use_file_search'
    ) THEN
        ALTER TABLE agents 
        ADD COLUMN use_file_search BOOLEAN NOT NULL DEFAULT FALSE;
        
        COMMENT ON COLUMN agents.use_file_search IS 'If True, agent will have access to user''s File Search Stores for RAG. If False, agent will not use File Search even if stores are available.';
    END IF;
END $$;


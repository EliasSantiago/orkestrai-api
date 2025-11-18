-- Migration: Fix google_file_name constraint in file_search_files table
-- Date: 2025-11-09
-- Issue: google_file_name had unique constraint but was being saved as empty string,
--        causing unique violation when multiple files couldn't extract the name

DO $$ 
BEGIN 
    -- Step 1: Remove NOT NULL constraint if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'file_search_files' 
        AND column_name = 'google_file_name' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE file_search_files 
        ALTER COLUMN google_file_name DROP NOT NULL;
    END IF;
    
    -- Step 2: Update existing empty strings to NULL
    UPDATE file_search_files 
    SET google_file_name = NULL 
    WHERE google_file_name = '';
END $$;


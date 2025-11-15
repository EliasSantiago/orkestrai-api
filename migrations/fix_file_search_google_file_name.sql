-- Migration: Fix google_file_name constraint in file_search_files table
-- Date: 2025-11-09
-- Issue: google_file_name had unique constraint but was being saved as empty string,
--        causing unique violation when multiple files couldn't extract the name

-- Step 1: Remove NOT NULL constraint
ALTER TABLE file_search_files 
ALTER COLUMN google_file_name DROP NOT NULL;

-- Step 2: Update existing empty strings to NULL
-- This allows multiple files without google_file_name
UPDATE file_search_files 
SET google_file_name = NULL 
WHERE google_file_name = '';

-- Step 3: Verify no duplicate non-null values exist
-- This should return 0 rows (or you need to fix duplicates first)
SELECT google_file_name, COUNT(*) as count
FROM file_search_files 
WHERE google_file_name IS NOT NULL 
GROUP BY google_file_name 
HAVING COUNT(*) > 1;

-- Step 4: Verify the change
-- Check that nullable is now true
SELECT 
    column_name, 
    is_nullable, 
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'file_search_files' 
AND column_name = 'google_file_name';


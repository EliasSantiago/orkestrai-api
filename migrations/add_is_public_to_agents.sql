-- Add is_public column to agents table
-- This allows agents to be marked as public (visible to all users)

-- Check if column exists, if not add it
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='agents' AND column_name='is_public'
    ) THEN
        ALTER TABLE agents 
        ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT FALSE;
        
        RAISE NOTICE 'Column is_public added successfully';
    ELSE
        RAISE NOTICE 'Column is_public already exists';
    END IF;
END $$;

-- Create index for better query performance when filtering by is_public
CREATE INDEX IF NOT EXISTS idx_agents_is_public ON agents(is_public);

-- Display summary
SELECT 
    COUNT(*) as total_agents,
    SUM(CASE WHEN is_public THEN 1 ELSE 0 END) as public_agents,
    SUM(CASE WHEN NOT is_public THEN 1 ELSE 0 END) as private_agents
FROM agents;


-- QUICK FIX: Update existing teams table to match new schema
-- Run this immediately if migration_member_level_attendance.sql hasn't been run yet

-- Step 1: Make old NOT NULL columns nullable (temporary fix)
ALTER TABLE teams 
ALTER COLUMN IF EXISTS leader_name DROP NOT NULL,
ALTER COLUMN IF EXISTS leader_email DROP NOT NULL,
ALTER COLUMN IF EXISTS leader_phone DROP NOT NULL,
ALTER COLUMN IF EXISTS year DROP NOT NULL;

-- Step 2: Drop old columns that conflict with new schema
ALTER TABLE teams 
DROP COLUMN IF EXISTS leader_name CASCADE,
DROP COLUMN IF EXISTS leader_email CASCADE,
DROP COLUMN IF EXISTS leader_phone CASCADE,
DROP COLUMN IF EXISTS year CASCADE,
DROP COLUMN IF EXISTS team_members CASCADE,
DROP COLUMN IF EXISTS access_key CASCADE,
DROP COLUMN IF EXISTS qr_code_path CASCADE,
DROP COLUMN IF EXISTS id_cards_pdf_path CASCADE,
DROP COLUMN IF EXISTS attendance_status CASCADE,
DROP COLUMN IF EXISTS checkin_time CASCADE,
DROP COLUMN IF EXISTS checkout_time CASCADE;

-- Step 3: Verify table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'teams' 
ORDER BY ordinal_position;

-- Step 4: Create team_members table if it doesn't exist
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    is_team_leader BOOLEAN DEFAULT FALSE,
    access_key VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_team_id FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE
);

-- Step 5: Create indexes
CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_email ON team_members(email);
-- attendance index removed
CREATE INDEX IF NOT EXISTS idx_team_members_access_key ON team_members(access_key);
CREATE INDEX IF NOT EXISTS idx_teams_team_id ON teams(team_id);

-- Done! System ready for new code

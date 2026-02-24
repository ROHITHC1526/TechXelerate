-- ================================================================
-- Migration: Convert to Member-Level Attendance Tracking
-- ================================================================
-- This migration converts from team-level attendance to per-member 
-- attendance tracking. Each team member gets unique access_key and
-- attendance_status.
-- ================================================================

-- ================================================================
-- BACKUP: Create backup of old teams table (optional)
-- ================================================================
-- Uncomment if you want to backup the old data first
-- CREATE TABLE teams_backup AS SELECT * FROM teams;

-- ================================================================
-- STEP 1: Create new team_members table
-- ================================================================
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    photo_path VARCHAR(512),
    is_team_leader BOOLEAN DEFAULT FALSE,
    access_key VARCHAR(64) UNIQUE NOT NULL,
    attendance_status BOOLEAN DEFAULT FALSE,
    checkin_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_team_id FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    CONSTRAINT unique_team_member UNIQUE (team_id, email)
);

-- Create indexes for faster queries
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_email ON team_members(email);
CREATE INDEX idx_team_members_attendance ON team_members(attendance_status);
CREATE INDEX idx_team_members_leader ON team_members(is_team_leader);

-- ================================================================
-- STEP 2: Modify teams table - REMOVE OLD COLUMNS
-- ================================================================
-- Drop columns that are now member-level (if they exist)
ALTER TABLE teams 
DROP COLUMN IF EXISTS leader_name,
DROP COLUMN IF EXISTS leader_email,
DROP COLUMN IF EXISTS leader_phone,
DROP COLUMN IF EXISTS year,
DROP COLUMN IF EXISTS team_members,
DROP COLUMN IF EXISTS access_key,
DROP COLUMN IF EXISTS qr_code_path,
DROP COLUMN IF EXISTS id_cards_pdf_path,
DROP COLUMN IF EXISTS attendance_status,
DROP COLUMN IF EXISTS checkin_time,
DROP COLUMN IF EXISTS checkout_time;

-- ================================================================
-- STEP 3: Verify final teams table structure
-- ================================================================
-- Expected teams table columns after cleanup:
-- - id (UUID)
-- - team_id (VARCHAR 32, UNIQUE, INDEX)
-- - team_name (VARCHAR 255)
-- - college_name (VARCHAR 255)
-- - domain (VARCHAR 100)
-- - created_at (TIMESTAMP)

-- ================================================================
-- NOTES FOR PRODUCTION
-- ================================================================
-- 1. Before running this migration, notify all users that:
--    - Each team member now has individual QR codes
--    - Each member has unique access_key (64 chars, stored in DB)
--    - Attendance is tracked per member (not team-level)
--    - QR payload format changed: {"team_id": "...", "member_id": "<UUID>", "access_key": "..."}
--
-- 2. After migration:
--    - Regenerate all ID cards with member-level QRs
--    - Test attendance scanning with member QR endpoint
--    - Verify stats dashboard shows per-member attendance
--
-- 3. Old team-level columns are permanently removed
--    - All data must be migrated to team_members table first
--    - Use team_creation_service.py to bulk migrate if needed
--
-- 4. To verify migration:
--    SELECT 
--        t.team_id, 
--        t.team_name,
--        COUNT(tm.id) as member_count,
--        SUM(CASE WHEN tm.attendance_status THEN 1 ELSE 0 END) as present_count
--    FROM teams t
--    LEFT JOIN team_members tm ON t.team_id = tm.team_id
--    GROUP BY t.team_id, t.team_name;

-- ================================================================
-- ROLLBACK INSTRUCTIONS (if needed)
-- ================================================================
-- To rollback this migration:
-- 1. Restore from teams_backup (if created): 
--    ALTER TABLE teams RENAME TO teams_new;
--    ALTER TABLE teams_backup RENAME TO teams;
-- 2. Drop team_members table:
--    DROP TABLE team_members;
-- 3. Restart FastAPI backend

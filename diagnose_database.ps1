# Diagnostic Script for Windows - Check Database Status

Write-Host "=================================================="
Write-Host "HACKCSM DATABASE DIAGNOSTIC REPORT"
Write-Host "=================================================="
Write-Host ""

# Check if PostgreSQL is accessible
Write-Host "🔍 Checking PostgreSQL connection..."
try {
    $conn_test = psql -U postgres -d hackcsm_db -c "SELECT version();" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ Cannot connect to database" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error connecting to database: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔍 Checking teams table structure..."
Write-Host "=================================================="

$teams_cols = @"
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'teams' 
ORDER BY ordinal_position;
"@

psql -U postgres -d hackcsm_db -c $teams_cols

Write-Host ""
Write-Host "🔍 Checking team_members table..."
Write-Host "=================================================="

$check_table = psql -U postgres -d hackcsm_db -t -c `
  "SELECT count(*) FROM information_schema.tables WHERE table_name = 'team_members';"

if ($check_table -match "1") {
    Write-Host "✅ team_members table EXISTS" -ForegroundColor Green
    Write-Host ""
    
    $members_cols = @"
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'team_members' 
ORDER BY ordinal_position;
"@
    
    psql -U postgres -d hackcsm_db -c $members_cols
} else {
    Write-Host "❌ team_members table MISSING - needs to be created" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔍 Checking for conflicting columns..."
Write-Host "=================================================="

$old_cols = psql -U postgres -d hackcsm_db -t -c `
  "SELECT count(*) FROM information_schema.columns WHERE table_name = 'teams' AND column_name IN ('leader_name', 'leader_email', 'leader_phone', 'year');" 2>$null

if ($old_cols -gt 0) {
    Write-Host "⚠️  WARNING: Old columns still exist ($old_cols found)" -ForegroundColor Yellow
    Write-Host "   This is causing the database error!" -ForegroundColor Yellow
    Write-Host ""
    
    $old_cols_details = @"
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'teams' 
AND column_name IN ('leader_name', 'leader_email', 'leader_phone', 'year', 'access_key', 'attendance_status');
"@
    
    psql -U postgres -d hackcsm_db -c $old_cols_details
} else {
    Write-Host "✅ Old columns have been removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔍 Summary..."
Write-Host "=================================================="
Write-Host "Database Status Report:"
Write-Host ""

if ($old_cols -gt 0) {
    Write-Host "❌ DATABASE NEEDS FIX" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run this command:" -ForegroundColor Yellow
    Write-Host "  psql -U postgres -d hackcsm_db -f quick_fix_database.sql" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then restart:" -ForegroundColor Yellow
    Write-Host "  docker-compose down && docker-compose up -d" -ForegroundColor Cyan
} else {
    Write-Host "✅ DATABASE SCHEMA IS CORRECT" -ForegroundColor Green
}

Write-Host ""
Write-Host "=================================================="

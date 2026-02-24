#!/usr/bin/env bash
# Diagnostic Script - Check Database Status

echo "=================================================="
echo "HACKCSM DATABASE DIAGNOSTIC REPORT"
echo "=================================================="
echo ""

# Check if PostgreSQL is accessible
echo "🔍 Checking PostgreSQL connection..."
psql -U postgres -d hackcsm_db -c "SELECT version();" 2>/dev/null && echo "✅ Database accessible" || { echo "❌ Cannot connect to database"; exit 1; }

echo ""
echo "🔍 Checking teams table structure..."
echo "=================================================="
psql -U postgres -d hackcsm_db << EOF
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'teams' 
ORDER BY ordinal_position;
EOF

echo ""
echo "🔍 Checking team_members table..."
echo "=================================================="
TABLE_EXISTS=$(psql -U postgres -d hackcsm_db -t -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_name = 'team_members';")

if [ "$TABLE_EXISTS" -eq "1" ]; then
    echo "✅ team_members table EXISTS"
    echo ""
    psql -U postgres -d hackcsm_db << EOF
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'team_members' 
ORDER BY ordinal_position;
EOF
else
    echo "❌ team_members table MISSING - needs to be created"
fi

echo ""
echo "🔍 Checking for conflicting columns..."
echo "=================================================="
HAS_OLD_COLS=$(psql -U postgres -d hackcsm_db -t -c \
  "SELECT count(*) FROM information_schema.columns WHERE table_name = 'teams' AND column_name IN ('leader_name', 'leader_email', 'leader_phone', 'year');")

if [ "$HAS_OLD_COLS" -gt "0" ]; then
    echo "⚠️  WARNING: Old columns still exist ($HAS_OLD_COLS found)"
    echo "   This is causing the database error!"
    echo ""
    psql -U postgres -d hackcsm_db << EOF
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'teams' 
AND column_name IN ('leader_name', 'leader_email', 'leader_phone', 'year', 'access_key', 'attendance_status');
EOF
else
    echo "✅ Old columns have been removed"
fi

echo ""
echo "🔍 Summary..."
echo "=================================================="
echo "Database Status Report:"
echo ""

if [ "$HAS_OLD_COLS" -gt "0" ]; then
    echo "❌ DATABASE NEEDS FIX"
    echo ""
    echo "Run this command:"
    echo "  psql -U postgres -d hackcsm_db -f quick_fix_database.sql"
    echo ""
    echo "Then restart:"
    echo "  docker-compose down && docker-compose up -d"
else
    echo "✅ DATABASE SCHEMA IS CORRECT"
fi

echo ""
echo "=================================================="

#!/bin/bash

# Script to apply user preferences migration
# Adds preferences column to users table

set -e

echo "🔄 Applying user preferences migration..."

# Get database connection details from environment or use defaults
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-orkestrai}"
DB_USER="${DB_USER:-postgres}"

# Check if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "ℹ️  Using DATABASE_URL from environment"
    PSQL_COMMAND="psql $DATABASE_URL"
else
    echo "ℹ️  Using individual DB connection parameters"
    PSQL_COMMAND="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
fi

# Apply migration
echo "📝 Executing migration: add_user_preferences.sql"
$PSQL_COMMAND -f migrations/add_user_preferences.sql

echo "✅ Migration applied successfully!"
echo ""
echo "📊 Verifying column was added..."
$PSQL_COMMAND -c "\d users" | grep preferences && echo "✅ preferences column verified!" || echo "❌ preferences column not found"

echo ""
echo "🎉 User preferences migration complete!"


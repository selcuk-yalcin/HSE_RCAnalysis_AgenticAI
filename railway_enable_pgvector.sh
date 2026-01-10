#!/bin/bash
# Railway PostgreSQL pgvector Extension Enabler
# Run this in Railway Backend Terminal

echo "🔧 Installing PostgreSQL client..."
apt-get update -qq && apt-get install -y postgresql-client > /dev/null 2>&1

echo ""
echo "📡 Connecting to PostgreSQL and enabling pgvector..."
psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo ""
echo "✅ Checking if vector extension is enabled..."
psql $DATABASE_URL -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"

echo ""
echo "🎉 Done! pgvector extension is now active."

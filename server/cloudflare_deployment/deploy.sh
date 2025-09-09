#!/bin/bash

# Cloudflare Workers Deployment Script for Token Anomaly Detector
# This script sets up and deploys the application to Cloudflare Workers

set -e

echo "🚀 Starting Cloudflare Workers deployment..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found. Please install it first:"
    echo "   npm install -g wrangler"
    exit 1
fi

# Check if user is logged in to Cloudflare
if ! wrangler whoami &> /dev/null; then
    echo "🔐 Please log in to Cloudflare first:"
    echo "   wrangler login"
    exit 1
fi

echo "✅ Wrangler CLI found and authenticated"

# Create D1 database if it doesn't exist
echo "📊 Setting up D1 database..."
DB_NAME="token-detector-db"

# Check if database already exists
if ! wrangler d1 list | grep -q "$DB_NAME"; then
    echo "Creating new D1 database: $DB_NAME"
    wrangler d1 create $DB_NAME
    echo "⚠️  Please update wrangler.jsonc with the database ID shown above"
    echo "   Update the 'database_id' field in the d1_databases section"
    read -p "Press enter after updating wrangler.jsonc with the database ID..."
else
    echo "✅ D1 database '$DB_NAME' already exists"
fi

# Apply database schema
echo "🗄️  Applying database schema..."
wrangler d1 execute $DB_NAME --file=./schema.sql

echo "✅ Database schema applied successfully"

# Set up secrets (if not already set)
echo "🔑 Setting up secrets..."

# Check if REPLICATE_API_TOKEN is already set
if ! wrangler secret list | grep -q "REPLICATE_API_TOKEN"; then
    echo "Setting up Replicate API token..."
    echo "Please enter your Replicate API token (or press enter to skip):"
    read -s REPLICATE_TOKEN
    if [ ! -z "$REPLICATE_TOKEN" ]; then
        echo "$REPLICATE_TOKEN" | wrangler secret put REPLICATE_API_TOKEN
        echo "✅ Replicate API token set"
    else
        echo "⚠️  Skipping Replicate API token - ML predictions will use local fallback"
    fi
else
    echo "✅ Replicate API token already configured"
fi

# Deploy the worker
echo "🚀 Deploying to Cloudflare Workers..."
wrangler deploy

echo "✅ Deployment completed successfully!"
echo ""
echo "🎉 Your Token Anomaly Detector is now live on Cloudflare Workers!"
echo ""
echo "Next steps:"
echo "1. Test your deployment by visiting the worker URL"
echo "2. Try analyzing some tokens using the /predict/{token_id} endpoint"
echo "3. Check the dashboard for statistics at /api/stats"
echo ""
echo "For more information, see README.md"

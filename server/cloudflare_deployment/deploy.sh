# Create D1 database if it doesn't exist
echo "📊 Setting up D1 database..."
DB_NAME="token-detector-db"

# Apply database schema
echo "🗄️  Applying database schema..."
wrangler d1 execute $DB_NAME --file=./schema.sql

# Deploy the worker
echo "🚀 Deploying to Cloudflare Workers..."
wrangler deploy
/**
 * Database utilities for D1 integration
 * Handles all database operations for token analysis data
 */

/**
 * Initialize database with schema (if needed)
 * @param {D1Database} db - D1 database instance
 */
export async function initDatabase(db) {
    // The schema should be applied via wrangler d1 migrations
    // This function can be used for any runtime initialization if needed
    console.log('Database initialized');
}

/**
 * Save token report to database
 * @param {D1Database} db - D1 database instance
 * @param {Object} tokenData - Token analysis data
 * @returns {Promise<Object>} - Database result
 */
export async function saveTokenReport(db, tokenData) {
    try {
        const stmt = db.prepare(`
            INSERT INTO token_reports (
                token_id, name, symbol, score_normalised, risk_level,
                price, holders, liquidity, market_cap, creator_holdings_pct,
                detected_at, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        const result = await stmt.bind(
            tokenData.token_id,
            tokenData.name,
            tokenData.symbol,
            tokenData.score_normalised || 0,
            tokenData.risk_level,
            tokenData.price || 0,
            tokenData.holders || 0,
            tokenData.liquidity || 0,
            tokenData.market_cap || 0,
            tokenData.creator_holdings_pct || 0,
            tokenData.detected_at,
            JSON.stringify(tokenData.raw_data || {})
        ).run();

        return result;
    } catch (error) {
        console.error('Error saving token report:', error);
        throw error;
    }
}

/**
 * Get cached token report if within TTL
 * @param {D1Database} db - D1 database instance
 * @param {string} tokenId - Token ID to search for
 * @param {number} ttlHours - TTL in hours (default: 24)
 * @returns {Promise<Object|null>} - Cached token data or null
 */
export async function getCachedTokenReport(db, tokenId, ttlHours = 24) {
    try {
        const stmt = db.prepare(`
            SELECT * FROM token_reports 
            WHERE token_id = ? 
            AND datetime(fetched_at) >= datetime('now', '-' || ? || ' hours')
            ORDER BY fetched_at DESC 
            LIMIT 1
        `);

        const result = await stmt.bind(tokenId, ttlHours).first();
        
        if (result) {
            // Parse raw_json if it exists
            if (result.raw_json) {
                try {
                    result.raw_data = JSON.parse(result.raw_json);
                } catch (e) {
                    console.warn('Failed to parse raw_json for token:', tokenId);
                    result.raw_data = {};
                }
            }
        }

        return result;
    } catch (error) {
        console.error('Error getting cached token report:', error);
        return null;
    }
}

/**
 * Get paginated list of recent tokens with optimized query
 * @param {D1Database} db - D1 database instance
 * @param {number} page - Page number (1-based)
 * @param {number} perPage - Items per page
 * @returns {Promise<Object>} - Paginated results with metadata
 */
export async function getRecentTokens(db, page = 1, perPage = 20) {
    try {
        // Limit per_page to prevent abuse
        perPage = Math.min(perPage, 100);
        const offset = (page - 1) * perPage;

        // Use a single query with window function to get both count and data
        const stmt = db.prepare(`
            SELECT 
                id, token_id, name, symbol, risk_level, score_normalised,
                price, market_cap, liquidity, holders, creator_holdings_pct,
                detected_at, fetched_at,
                COUNT(*) OVER() as total_count
            FROM token_reports 
            ORDER BY fetched_at DESC 
            LIMIT ? OFFSET ?
        `);

        const results = await stmt.bind(perPage, offset).all();
        const tokens = results.results || [];
        
        // Extract total count from first row (if any)
        const total = tokens.length > 0 ? tokens[0].total_count : 0;
        
        // Remove total_count from each token object
        tokens.forEach(token => delete token.total_count);

        return {
            tokens,
            pagination: {
                page,
                per_page: perPage,
                total,
                pages: Math.ceil(total / perPage)
            }
        };
    } catch (error) {
        console.error('Error getting recent tokens:', error);
        throw error;
    }
}

/**
 * Get database statistics with a single optimized query
 * @param {D1Database} db - D1 database instance
 * @returns {Promise<Object>} - Database statistics
 */
export async function getDatabaseStats(db) {
    try {
        // Single query to get all statistics at once
        const stmt = db.prepare(`
            SELECT 
                COUNT(*) as total_tokens,
                SUM(CASE WHEN risk_level = 'Fraud' THEN 1 ELSE 0 END) as fraud_tokens,
                SUM(CASE WHEN risk_level = 'Safe' THEN 1 ELSE 0 END) as safe_tokens,
                SUM(CASE WHEN datetime(fetched_at) >= datetime('now', '-24 hours') THEN 1 ELSE 0 END) as recent_24h
            FROM token_reports
        `);
        
        const result = await stmt.first();
        
        const totalTokens = result?.total_tokens || 0;
        const fraudCount = result?.fraud_tokens || 0;
        const safeCount = result?.safe_tokens || 0;
        const recentCount = result?.recent_24h || 0;

        // Calculate fraud percentage
        const fraudPercentage = totalTokens > 0 
            ? Math.round((fraudCount / totalTokens) * 100 * 10) / 10 
            : 0;

        return {
            total_tokens: totalTokens,
            fraud_tokens: fraudCount,
            safe_tokens: safeCount,
            recent_24h: recentCount,
            fraud_percentage: fraudPercentage
        };
    } catch (error) {
        console.error('Error getting database stats:', error);
        throw error;
    }
}

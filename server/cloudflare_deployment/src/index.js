/**
 * Token Anomaly Detector - Cloudflare Worker
 * Complete migration from Python Flask API to JavaScript
 * Includes D1 database integration and ML-based prediction capabilities
 */

import { predictTokenRiskAPI, predictTokenRiskLocal } from './model.js';
import { 
    saveTokenReport, 
    getCachedTokenReport, 
    getRecentTokens, 
    getDatabaseStats 
} from './database.js';

export default {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);
        
        // Add CORS headers
        const corsHeaders = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        };

        // Handle CORS preflight requests
        if (request.method === 'OPTIONS') {
            return new Response(null, { headers: corsHeaders });
        }

        try {
            // Route handling
            if (url.pathname.startsWith('/predict/')) {
                const tokenId = url.pathname.split('/predict/')[1];
                if (!tokenId) {
                    return createErrorResponse('Token ID is required', 'Please provide a valid token ID', 400, corsHeaders);
                }
                return await handlePredictToken(tokenId, url.searchParams, env, corsHeaders);
            } else if (url.pathname.startsWith('/api/tokens')) {
                return await handleGetTokens(url.searchParams, env, corsHeaders);
            } else if (url.pathname.startsWith('/api/stats')) {
                return await handleGetStats(env, corsHeaders);
            } else if (url.pathname === '/' || url.pathname === '') {
                // Serve static files from assets
                return env.ASSETS.fetch(request);
            } else {
                return createErrorResponse('Not Found', 'Endpoint not found', 404, corsHeaders);
            }
        } catch (error) {
            console.error('Unhandled error:', error);
            return createErrorResponse(error.message, 'An unexpected error occurred', 500, corsHeaders);
        }
    },
};

/**
 * Handle token prediction requests with caching
 * Equivalent to Flask's /predict/<token_id> endpoint
 */
async function handlePredictToken(tokenId, searchParams, env, corsHeaders) {
    const forceRefresh = searchParams.get('force_refresh') === 'true';
    const TTL_HOURS = 24;

    try {
        // Check cache first (unless force refresh is requested)
        if (!forceRefresh) {
            const cachedReport = await getCachedTokenReport(env.DB, tokenId, TTL_HOURS);
            if (cachedReport) {
                // Calculate cache age
                const now = new Date();
                const fetchedAt = new Date(cachedReport.fetched_at);
                const cacheAgeHours = Math.round((now - fetchedAt) / (1000 * 60 * 60) * 10) / 10;

                // Get ML prediction from cached data if available
                let mlPrediction = null;
                if (cachedReport.raw_data) {
                    try {
                        mlPrediction = predictTokenRiskLocal(cachedReport.raw_data);
                    } catch (error) {
                        console.warn('Failed to generate ML prediction from cache:', error);
                    }
                }

                return new Response(JSON.stringify({
                    token_id: tokenId,
                    status: 'success',
                    name: cachedReport.name || 'Unknown Token',
                    symbol: cachedReport.symbol || 'UNK',
                    risk_level: cachedReport.risk_level || 'Safe',
                    market_cap: cachedReport.market_cap || 0,
                    liquidity: cachedReport.liquidity || 0,
                    holders: cachedReport.holders || 0,
                    creation_date: cachedReport.detected_at || '',
                    price: cachedReport.price || 0,
                    ml_prediction: mlPrediction,
                    raw_data: cachedReport.raw_data || {},
                    cached: true,
                    fetched_at: cachedReport.fetched_at,
                    cache_age_hours: cacheAgeHours
                }), {
                    status: 200,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                });
            }
        }

        // Fetch fresh data from RugCheck API
        const apiUrl = `https://api.rugcheck.xyz/v1/tokens/${tokenId}/report`;
        const response = await fetch(apiUrl);

        if (!response.ok) {
            return createErrorResponse(
                `API returned status code: ${response.status}`,
                'Failed to fetch token data',
                response.status,
                corsHeaders
            );
        }

        const data = await response.json();

        // Process the API response (same logic as Flask app)
        const tokenMeta = data.tokenMeta || {};
        const scoreNormalised = data.score_normalised || 0;
        const creatorBalance = data.creatorBalance || 0;
        const totalSupply = data.token?.supply || 1000000000000;
        const totalHolders = data.totalHolders || 0;
        const totalLiquidity = data.totalMarketLiquidity || 0;
        const price = data.price || 0;

        // Calculate market cap
        const decimals = data.token?.decimals || 6;
        const marketCap = price * (totalSupply / (10 ** decimals));

        // Calculate creator holdings percentage
        const creatorHoldingsPct = totalSupply > 0 ? (creatorBalance / totalSupply) * 100 : 0;

        // Use ML model to predict risk
        let mlPrediction = null;
        try {
            if (env.REPLICATE_API_TOKEN) {
                mlPrediction = await predictTokenRiskAPI(data, env.REPLICATE_API_TOKEN);
            } else {
                mlPrediction = predictTokenRiskLocal(data);
            }
        } catch (error) {
            console.warn('ML prediction failed:', error);
        }

        const processedData = {
            token_id: tokenId,
            status: 'success',
            name: tokenMeta.name || 'Unknown Token',
            symbol: tokenMeta.symbol || 'UNK',
            risk_level: scoreNormalised >= 62 ? 'Fraud' : 'Safe',
            market_cap: marketCap,
            liquidity: totalLiquidity,
            holders: totalHolders,
            creation_date: data.detectedAt || '',
            price: price,
            ml_prediction: mlPrediction,
            raw_data: data,
            cached: false,
            fetched_at: new Date().toISOString(),
            cache_age_hours: 0
        };

        // Save to database for caching and history
        try {
            await saveTokenReport(env.DB, {
                token_id: tokenId,
                name: processedData.name,
                symbol: processedData.symbol,
                score_normalised: scoreNormalised,
                risk_level: processedData.risk_level,
                price: price,
                holders: totalHolders,
                liquidity: totalLiquidity,
                market_cap: marketCap,
                creator_holdings_pct: creatorHoldingsPct,
                detected_at: data.detectedAt || '',
                raw_data: data
            });
        } catch (error) {
            console.warn('Failed to save token report to database:', error);
            // Don't fail the request if DB write fails
        }

        return new Response(JSON.stringify(processedData), {
            status: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Error in handlePredictToken:', error);
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return createErrorResponse(
                error.message,
                'Network error occurred while fetching token data',
                500,
                corsHeaders
            );
        } else {
            return createErrorResponse(
                error.message,
                'An unexpected error occurred',
                500,
                corsHeaders
            );
        }
    }
}

/**
 * Handle get tokens requests with pagination
 * Equivalent to Flask's /api/tokens endpoint
 */
async function handleGetTokens(searchParams, env, corsHeaders) {
    try {
        const page = parseInt(searchParams.get('page')) || 1;
        const perPage = Math.min(parseInt(searchParams.get('per_page')) || 20, 100);

        const result = await getRecentTokens(env.DB, page, perPage);

        return new Response(JSON.stringify(result), {
            status: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    } catch (error) {
        console.error('Error in handleGetTokens:', error);
        return createErrorResponse(
            error.message,
            'Failed to retrieve tokens',
            500,
            corsHeaders
        );
    }
}

/**
 * Handle get statistics requests
 * Equivalent to Flask's /api/stats endpoint
 */
async function handleGetStats(env, corsHeaders) {
    try {
        const stats = await getDatabaseStats(env.DB);

        return new Response(JSON.stringify(stats), {
            status: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    } catch (error) {
        console.error('Error in handleGetStats:', error);
        return createErrorResponse(
            error.message,
            'Failed to retrieve statistics',
            500,
            corsHeaders
        );
    }
}

/**
 * Create standardized error response
 */
function createErrorResponse(error, message, status, corsHeaders) {
    return new Response(JSON.stringify({
        status: 'error',
        error: error,
        message: message
    }), {
        status: status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
}
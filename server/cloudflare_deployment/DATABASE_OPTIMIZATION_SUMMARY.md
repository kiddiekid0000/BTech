# Database Query Optimization - Fix for Query Spam Issue

## Problem Identified

When refreshing the website, the server was receiving 20-30+ database queries due to:

1. **Multiple separate database queries per API call**:
   - `/api/stats` endpoint executed 4 separate queries
   - `/api/tokens` endpoint executed 2 separate queries

2. **Frequent API calls from frontend**:
   - Page refresh triggered immediate API calls
   - Auto-refresh timers: stats every 30s, tokens every 2min
   - Multiple browser tabs multiplied the problem
   - No caching mechanism in frontend

3. **Total queries per page refresh**: 6 immediate + ongoing auto-refresh

## Solutions Implemented

### Backend Optimizations (src/database.js)

#### 1. Optimized getDatabaseStats() function
**Before**: 4 separate queries
```sql
SELECT COUNT(*) as total FROM token_reports
SELECT COUNT(*) as count FROM token_reports WHERE risk_level = 'Fraud'
SELECT COUNT(*) as count FROM token_reports WHERE risk_level = 'Safe'  
SELECT COUNT(*) as count FROM token_reports WHERE datetime(fetched_at) >= datetime('now', '-24 hours')
```

**After**: 1 optimized query
```sql
SELECT 
    COUNT(*) as total_tokens,
    SUM(CASE WHEN risk_level = 'Fraud' THEN 1 ELSE 0 END) as fraud_tokens,
    SUM(CASE WHEN risk_level = 'Safe' THEN 1 ELSE 0 END) as safe_tokens,
    SUM(CASE WHEN datetime(fetched_at) >= datetime('now', '-24 hours') THEN 1 ELSE 0 END) as recent_24h
FROM token_reports
```

**Result**: 75% reduction in database queries for stats (4 → 1)

#### 2. Optimized getRecentTokens() function
**Before**: 2 separate queries
```sql
SELECT COUNT(*) as total FROM token_reports  -- For pagination
SELECT ... FROM token_reports ORDER BY fetched_at DESC LIMIT ? OFFSET ?  -- For data
```

**After**: 1 query with window function
```sql
SELECT 
    id, token_id, name, symbol, risk_level, score_normalised,
    price, market_cap, liquidity, holders, creator_holdings_pct,
    detected_at, fetched_at,
    COUNT(*) OVER() as total_count  -- Window function for total count
FROM token_reports 
ORDER BY fetched_at DESC 
LIMIT ? OFFSET ?
```

**Result**: 50% reduction in database queries for tokens (2 → 1)

### Frontend Optimizations (public/index.html)

#### 1. Added Client-Side Caching
- **Stats cache**: 30-second TTL
- **Tokens cache**: 1-minute TTL per page
- Cache includes timestamp and TTL validation
- Force refresh option for manual updates

#### 2. Reduced Auto-Refresh Frequency
- **Stats refresh**: 30s → 60s (50% reduction)
- **Tokens refresh**: 2min → 5min (60% reduction)

#### 3. Smart Cache Management
- Cache used on page refresh unless expired
- Force refresh only when:
  - Manual refresh button clicked
  - After token analysis (to show new data)
  - Auto-refresh timers (to get fresh data)

## Performance Impact

### Database Query Reduction
- **Page refresh**: 6 queries → 2 queries (67% reduction)
- **Stats endpoint**: 4 queries → 1 query (75% reduction)
- **Tokens endpoint**: 2 queries → 1 query (50% reduction)

### Network Request Reduction
- **Immediate page load**: Still 2 API calls, but cached for subsequent refreshes
- **Auto-refresh frequency**: Reduced by 50-60%
- **Browser tab multiplication**: Mitigated by caching

### Expected Results
- **20-30 queries per refresh** → **2-6 queries per refresh**
- Reduced database load by ~70-80%
- Improved page load performance
- Better user experience with cached data
- Reduced Cloudflare D1 database costs

## Backward Compatibility
- All API endpoints maintain the same response format
- Frontend functionality unchanged for users
- No breaking changes to existing integrations

## Monitoring Recommendations
1. Monitor database query counts in Cloudflare D1 dashboard
2. Track page load performance
3. Verify cache hit rates in browser dev tools
4. Monitor auto-refresh behavior across multiple tabs

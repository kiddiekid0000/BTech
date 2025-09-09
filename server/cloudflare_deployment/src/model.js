/**
 * ML model for token fraud detection in Cloudflare Workers
 * Uses decision tree logic and external API calls for predictions
 */

// Decision tree thresholds derived from the Python RandomForest model
// These values are simplified approximations
const THRESHOLDS = {
  LIQUIDITY_MIN: 1000,  // Minimum acceptable liquidity in USD
  HOLDERS_MIN: 50,      // Minimum number of holders
  CREATOR_MAX_PCT: 80,  // Maximum creator holdings percentage
  TOP_HOLDER_MAX_PCT: 90 // Maximum top holder percentage
};

/**
 * Extract features from token data similar to the Python model
 * @param {Object} data - Token data from API
 * @returns {Object} - Extracted features
 */
function extractFeatures(data) {
  return {
    totalMarketLiquidity: data.totalMarketLiquidity || 0,
    totalHolders: data.totalHolders || 0,
    creatorBalance: data.creatorBalance || 0,
    totalSupply: data.token?.supply || 1,
    price: data.price || 0,
    topHolderPct: data.topHolders?.[0]?.pct || 0,
    scoreNormalised: data.score_normalised || 0,
    hasLowLiquidityRisk: (data.risks || []).some(risk => risk.name === 'Low Liquidity'),
    hasLowLpProvidersRisk: (data.risks || []).some(risk => risk.name === 'Low amount of LP Providers')
  };
}

/**
 * Normalize features to 0-1 range for model input
 * @param {Object} features - Raw features
 * @returns {Float32Array} - Normalized features
 */
function normalizeFeatures(features) {
  // Simple min-max scaling with preset bounds
  const normalized = new Float32Array(4);
  
  // Feature 1: Normalized liquidity (0-1)
  normalized[0] = Math.min(features.totalMarketLiquidity / 10000, 1);
  
  // Feature 2: Normalized holder count (0-1)
  normalized[1] = Math.min(features.totalHolders / 1000, 1);
  
  // Feature 3: Creator holdings percentage (0-1)
  const creatorHoldingsPct = features.totalSupply > 0 
    ? (features.creatorBalance / features.totalSupply) * 100 
    : 0;
  normalized[2] = Math.min(creatorHoldingsPct / 100, 1);
  
  // Feature 4: Top holder percentage (0-1)
  normalized[3] = Math.min(features.topHolderPct / 100, 1);

  return normalized;
}

/**
 * Decision tree implementation as a simple rule-based system
 * @param {Float32Array} features - Normalized features
 * @returns {Object} - Prediction results
 */
function decisionTree(features) {
  // Unpack normalized features
  const [liquidity, holders, creatorPct, topHolderPct] = features;
  
  // Simple decision tree logic
  let fraudProbability = 0;
  
  // Insufficient liquidity is a major red flag
  if (liquidity < 0.1) fraudProbability += 0.4;
  
  // Few holders is suspicious
  if (holders < 0.05) fraudProbability += 0.3;
  
  // Creator holding too much is suspicious
  if (creatorPct > 0.8) fraudProbability += 0.2;
  
  // Single holder dominating is suspicious
  if (topHolderPct > 0.9) fraudProbability += 0.3;
  
  // Normalize probability to 0-1
  fraudProbability = Math.min(fraudProbability, 1);
  
  // Make prediction
  const prediction = fraudProbability >= 0.5 ? 1 : 0;
  
  return {
    prediction,
    is_fraud: prediction === 1,
    fraud_probability: fraudProbability,
    prediction_confidence: Math.max(fraudProbability, 1 - fraudProbability),
    label: prediction === 1 ? 'Fraud' : 'Legitimate'
  };
}

/**
 * Predict token risk using external ML API (Replicate)
 * @param {Object} tokenData - Token data from API
 * @param {string} replicateToken - Replicate API token
 * @returns {Promise<Object>} - Prediction results
 */
export async function predictTokenRiskAPI(tokenData, replicateToken) {
    try {
        const response = await fetch('https://api.replicate.com/v1/predictions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${replicateToken}`,
                'Content-Type': 'application/json',
                'Prefer': 'wait'
            },
            body: JSON.stringify({
                version: "enhance-replicate/tcap_finale:6975488a19ab9c27d9656ea29a711dd0471b53e6ec15cb17699f9cbd714980cc",
                input: {
                    token_data: JSON.stringify(tokenData)
                }
            })
        });

        if (response.ok) {
            const result = await response.json();
            return result.output;
        } else {
            console.warn('Replicate API failed, falling back to local prediction');
            return predictTokenRiskLocal(tokenData);
        }
    } catch (error) {
        console.warn('Error calling Replicate API, falling back to local prediction:', error);
        return predictTokenRiskLocal(tokenData);
    }
}

/**
 * Local token risk prediction using decision tree logic
 * @param {Object} tokenData - Token data from API
 * @returns {Object} - Prediction results
 */
export function predictTokenRiskLocal(tokenData) {
    // Extract features from token data
    const features = extractFeatures(tokenData);
    
    // Normalize features for model input
    const normalizedFeatures = normalizeFeatures(features);
    
    // Use decision tree for prediction
    return decisionTree(normalizedFeatures);
}

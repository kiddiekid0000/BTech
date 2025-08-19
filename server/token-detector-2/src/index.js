/**
 * Token Anomaly Detector - Cloudflare Worker
 * Converted from Python Flask API to JavaScript
 */

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
			if (url.pathname.startsWith('/detect/')) {
				const tokenId = url.pathname.split('/detect/')[1];
				if (!tokenId) {
					return new Response(JSON.stringify({
						status: 'error',
						error: 'Token ID is required',
						message: 'Please provide a valid token ID'
					}), {
						status: 400,
						headers: { ...corsHeaders, 'Content-Type': 'application/json' }
					});
				}
				return await detectToken(tokenId, corsHeaders);
			} else if (url.pathname === '/' || url.pathname === '') {
				return await serveHomePage(corsHeaders);
			} else {
				return new Response(JSON.stringify({
					status: 'error',
					error: 'Not Found',
					message: 'Endpoint not found'
				}), {
					status: 404,
					headers: { ...corsHeaders, 'Content-Type': 'application/json' }
				});
			}
		} catch (error) {
			return new Response(JSON.stringify({
				status: 'error',
				error: error.message,
				message: 'An unexpected error occurred'
			}), {
				status: 500,
				headers: { ...corsHeaders, 'Content-Type': 'application/json' }
			});
		}
	},
};

async function detectToken(tokenId, corsHeaders) {
	const apiUrl = `https://api.rugcheck.xyz/v1/tokens/${tokenId}/report`;
	
	try {
		const response = await fetch(apiUrl);
		
		if (response.ok) {
			const data = await response.json();
			
			// Extract relevant data and process it from the actual API structure
			const tokenMeta = data.tokenMeta || {};
			const scoreNormalised = data.score_normalised || 0; // Note: 'normalised' not 'normalized'
			const risks = data.risks || [];
			const creatorBalance = data.creatorBalance || 0;
			const totalSupply = data.token?.supply || 1000000000000; // Default to avoid division by zero
			const totalHolders = data.totalHolders || 0;
			const totalLiquidity = data.totalMarketLiquidity || 0;
			const price = data.price || 0;
			
			// Calculate market cap: price * total supply
			const decimals = data.token?.decimals || 6;
			const marketCap = price * (totalSupply / (10 ** decimals));
			
			// Calculate creator holdings percentage
			const creatorHoldingsPct = totalSupply > 0 ? (creatorBalance / totalSupply) * 100 : 0;
			
			// Extract anomalies from risks
			let anomalies = [];
			for (const risk of risks) {
				let riskDesc = risk.description || risk.name || 'Unknown risk';
				if (risk.value) {
					riskDesc += ` (${risk.value})`;
				}
				anomalies.push(riskDesc);
			}
			
			if (anomalies.length === 0) {
				anomalies = ['No specific risks detected in API response'];
			}
			
			const processedData = {
				token_id: tokenId,
				status: 'success',
				name: tokenMeta.name || 'Unknown Token',
				symbol: tokenMeta.symbol || 'UNK',
				score_normalized: scoreNormalised,
				risk_level: scoreNormalised >= 63 ? 'Fraud' : 'Safe',
				market_cap: marketCap,
				liquidity: totalLiquidity,
				volume_24h: 0, // Not available in this API
				holders: totalHolders,
				creation_date: data.detectedAt || '',
				creator_holdings: creatorHoldingsPct,
				anomalies: anomalies,
				price: price,
				raw_data: data // Include full raw data for debugging
			};
			
			return new Response(JSON.stringify(processedData), {
				status: 200,
				headers: { ...corsHeaders, 'Content-Type': 'application/json' }
			});
		} else {
			return new Response(JSON.stringify({
				token_id: tokenId,
				status: 'error',
				error: `API returned status code: ${response.status}`,
				message: 'Failed to fetch token data'
			}), {
				status: response.status,
				headers: { ...corsHeaders, 'Content-Type': 'application/json' }
			});
		}
	} catch (error) {
		if (error.name === 'TypeError' && error.message.includes('fetch')) {
			return new Response(JSON.stringify({
				token_id: tokenId,
				status: 'error',
				error: error.message,
				message: 'Network error occurred while fetching token data'
			}), {
				status: 500,
				headers: { ...corsHeaders, 'Content-Type': 'application/json' }
			});
		} else {
			return new Response(JSON.stringify({
				token_id: tokenId,
				status: 'error',
				error: error.message,
				message: 'An unexpected error occurred'
			}), {
				status: 500,
				headers: { ...corsHeaders, 'Content-Type': 'application/json' }
			});
		}
	}
}

async function serveHomePage(corsHeaders) {
	const html = `
	<!DOCTYPE html>
	<html lang="en">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Token Anomaly Detector</title>
		<style>
			body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
			.container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
			.endpoint { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }
			code { background: #e8e8e8; padding: 2px 5px; border-radius: 3px; }
		</style>
	</head>
	<body>
		<div class="container">
			<h1>Token Anomaly Detector API</h1>
			<p>This API helps detect potential fraud and anomalies in cryptocurrency tokens.</p>
			
			<div class="endpoint">
				<h3>Detect Token Anomalies</h3>
				<p><strong>Endpoint:</strong> <code>GET /detect/{token_id}</code></p>
				<p><strong>Description:</strong> Analyzes a token for potential fraud indicators and returns risk assessment.</p>
				<p><strong>Example:</strong> <code>/detect/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v</code></p>
			</div>
			
			<h3>Response Format</h3>
			<pre>{
  "token_id": "string",
  "status": "success|error",
  "name": "Token Name",
  "symbol": "TKN",
  "score_normalized": 0-100,
  "risk_level": "Safe|Fraud",
  "market_cap": 0,
  "liquidity": 0,
  "holders": 0,
  "creator_holdings": 0,
  "anomalies": ["list of detected issues"],
  "price": 0
}</pre>
		</div>
	</body>
	</html>
	`;
	
	return new Response(html, {
		status: 200,
		headers: { ...corsHeaders, 'Content-Type': 'text/html' }
	});
}

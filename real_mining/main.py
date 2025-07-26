import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any
import requests
from tqdm import tqdm
import glob
from concurrent.futures import ThreadPoolExecutor

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjI5MjU5ZTg3LWM1MzMtNDhhMy04NzlmLTJhNDFjZTAxOWYzOCIsIm9yZ0lkIjoiNDYxNTMxIiwidXNlcklkIjoiNDc0ODI1IiwidHlwZUlkIjoiODdjOWEwZTItYTQ1OS00M2QzLWExN2YtMTZhYjJmYjRiMTVlIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NTM1MTQ4NjQsImV4cCI6NDkwOTI3NDg2NH0.qI1YZRDuI1pB6mY1z3z-fD-lNuvIXW-gIRXrW2fcCmY"
BASE_URL = "https://solana-gateway.moralis.io"

def fetch_label_on_rugcheck(token_id: str) -> int:
    '''Fetch label from RugCheck API for the given token ID.'''
    url = f'https://api.rugcheck.xyz/v1/tokens/{token_id}/report'
    
    response = requests.get(url)
    if response.ok:
        data = response.json()
        return data.get('score_normalised', -1)
    return -1

def fetch_json(url: str) -> Dict[str, Any]:
    '''Fetch JSON data from the given URL with API key authentication'''
    headers = {
        'X-API-Key': API_KEY,
        'accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def main(token: str, is_fraud_label: int, output_dir: str = 'json_output') -> None:
    try:
        data = { 'label': is_fraud_label }

        # Fetch metadata
        metadata_url = f'{BASE_URL}/token/mainnet/{token}/metadata'
        metadata_data = fetch_json(metadata_url)
        data['mint'] = metadata_data.get('mint', '')
        data['name'] = metadata_data.get('name', '')
        data['symbol'] = metadata_data.get('symbol', '')
        data['decimals'] = metadata_data.get('decimals', '')
        data['totalSupply'] = metadata_data.get('totalSupply', '')
        data['totalSupplyFormatted'] = metadata_data.get('totalSupplyFormatted', '')
        data['sellerFeeBasisPoints'] = metadata_data.get('metaplex', {}).get('sellerFeeBasisPoints', 0)
        data['isMutable'] = metadata_data.get('metaplex', {}).get('isMutable', False)
        data['primarySaleHappened'] = metadata_data.get('metaplex', {}).get('primarySaleHappened', 0)
        data['updateAuthority'] = metadata_data.get('metaplex', {}).get('updateAuthority', '')

        # Fetch price
        price_url = f'{BASE_URL}/token/mainnet/{token}/price'
        price_data = fetch_json(price_url)
        data['usdPrice'] = price_data.get('usdPrice', 0.0)
        data['nativePriceValue'] = price_data.get('nativePrice', {}).get('value', '')
        data['exchangeName'] = price_data.get('exchangeName', '')
        data['exchangeAddress'] = price_data.get('exchangeAddress', '')

        # Fetch swaps
        swaps_url = f'{BASE_URL}/token/mainnet/{token}/swaps?order=ASC&limit=1'
        swaps_data = fetch_json(swaps_url)

        # Initialize swap variables
        data['firstSwapTimestamp'] = ''
        data['firstSwapType'] = ''
        data['firstBuyerOrSeller'] = ''
        data['firstTradeValueUsd'] = 0.0
        
        swaps = swaps_data.get('result', [])
        if len(swaps) > 0:
            first = swaps[0]  # Oldest
            timestamp_str = first.get('blockTimestamp', '')
            if timestamp_str:
                first_swap_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                first_swap_time = datetime.now()

            data['firstSwapTimestamp'] = first_swap_time.isoformat() if first_swap_time else ''
            data['firstSwapType'] = first.get('transactionType', '')
            data['firstBuyerOrSeller'] = first.get('walletAddress', '')
            data['firstTradeValueUsd'] = first.get('totalValueUsd', 0.0)
        
        # Convert to JSON
        json_data = json.dumps(data, indent=4)
        
        # Create filename with timestamp
        timestamp = int(time.time())
        filename = f'token_data_{token}_{timestamp}.json'
        file_path = os.path.join(output_dir, filename)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f'Token data successfully exported to: {file_path}')
        
    except requests.RequestException as e:
        print(f'API request failed: {e}')
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    output_dir = 'json_output'
    os.makedirs(output_dir, exist_ok=True)

    with open('coins.txt', 'r', encoding='utf-8') as file:
        coins = [line.strip() for line in file.readlines() if line.strip()]

    futures = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for coin in tqdm(coins, total=len(coins), desc='Mint Tokens', colour='green'):
            if len(glob.glob(f'{output_dir}/token_data_{coin}_*.json')) > 0:

                continue
            futures.append(
                executor.submit(
                    main,
                    token=coin,
                    is_fraud_label=fetch_label_on_rugcheck(coin)
                )
            )

    for future in tqdm(futures, desc='Processing Futures', colour='blue'):
        try:
            future.result()  # Wait for each future to complete
        except Exception as e:
            print(f'Error processing future: {e}')
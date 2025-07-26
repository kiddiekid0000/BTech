import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import requests
from tqdm import tqdm

API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjVjZDZjZDk5LTg5MjUtNGRiYS1iZWQyLWJjNzNkYzQ3ZTVmYSIsIm9yZ0lkIjoiNDU5ODY2IiwidXNlcklkIjoiNDczMTE4IiwidHlwZUlkIjoiOTVjZGQwYmMtNDViYi00MWVhLWEwMGItMWRhODZjZDNiM2Q2IiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NTI3NjcyNjUsImV4cCI6NDkwODUyNzI2NX0.BOMHcWhyTzWhnT3an-pporsYhIGm0yGyCO2CZ381liY"
BASE_URL="https://solana-gateway.moralis.io"

def fetch_label_on_rugcheck(token_id: str) -> int:
    """Fetch label from RugCheck API for the given token ID."""
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_id}/report"
    
    response = requests.get(url)
    if response.ok:
        data = response.json()
        return data.get("score_normalised", -1)
    return -1

class MetadataResponse:
    def __init__(self, data: Dict[str, Any]):
        self.mint = data.get("mint", "")
        self.name = data.get("name", "")
        self.symbol = data.get("symbol", "")
        self.decimals = data.get("decimals", "")
        self.total_supply = data.get("totalSupply", "")
        self.total_supply_formatted = data.get("totalSupplyFormatted", "")
        
        metaplex = data.get("metaplex", {})
        self.seller_fee_basis_points = metaplex.get("sellerFeeBasisPoints", 0)
        self.is_mutable = metaplex.get("isMutable", False)
        self.primary_sale_happened = metaplex.get("primarySaleHappened", 0)
        self.update_authority = metaplex.get("updateAuthority", "")


class PriceResponse:
    def __init__(self, data: Dict[str, Any]):
        self.usd_price = data.get("usdPrice", 0.0)
        native_price = data.get("nativePrice", {})
        self.native_price_value = native_price.get("value", "")
        self.exchange_name = data.get("exchangeName", "")
        self.exchange_address = data.get("exchangeAddress", "")


class SwapResult:
    def __init__(self, data: Dict[str, Any]):
        self.transaction_type = data.get("transactionType", "")
        # Parse ISO timestamp to datetime
        timestamp_str = data.get("blockTimestamp", "")
        if timestamp_str:
            self.block_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            self.block_timestamp = datetime.now()
        self.wallet_address = data.get("walletAddress", "")
        self.total_value_usd = data.get("totalValueUsd", 0.0)


class SwapsResponse:
    def __init__(self, data: Dict[str, Any]):
        result_data = data.get("result", [])
        self.result = [SwapResult(item) for item in result_data]

def check_for_duplicate_mint(mint: str) -> None:
    """Check if the given mint address already exists in any JSON file"""
    output_dir = Path("json_output")
    
    # Check if directory exists
    if not output_dir.exists():
        # Directory doesn't exist, no duplicates possible
        return
    
    # Check each JSON file
    for file_path in output_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            # Check if mint matches
            if token_data.get("mint") == mint:
                raise Exception(f"duplicate mint address detected: {mint} already exists in file: {file_path}")
                
        except json.JSONDecodeError:
            print(f"Warning: failed to parse JSON in file {file_path}")
            continue
        except FileNotFoundError:
            print(f"Warning: failed to read file {file_path}")
            continue


def fetch_json(url: str) -> Dict[str, Any]:
    """Fetch JSON data from the given URL with API key authentication"""
    headers = {
        "X-API-Key": API_KEY,
        "accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def main(token: str, is_fraud_label: int):
    # Check for duplicate mint address before processing
    try:
        check_for_duplicate_mint(token)
    except Exception as e:
        print(f"Duplicate check failed: {e}")
        return
    
    try:
        # Fetch metadata
        metadata_url = f"{BASE_URL}/token/mainnet/{token}/metadata"
        metadata_data = fetch_json(metadata_url)
        meta = MetadataResponse(metadata_data)
        
        # Fetch price
        price_url = f"{BASE_URL}/token/mainnet/{token}/price"
        price_data = fetch_json(price_url)
        price = PriceResponse(price_data)
        
        # Fetch swaps
        swaps_url = f"{BASE_URL}/token/mainnet/{token}/swaps?order=ASC&limit=1"
        swaps_data = fetch_json(swaps_url)
        swaps = SwapsResponse(swaps_data)
        
        # Initialize swap variables
        first_swap_time = None
        first_buyer_or_seller = ""
        first_type = ""
        first_total_usd = 0.0
        
        if len(swaps.result) > 0:
            first = swaps.result[0]  # Oldest
            first_swap_time = first.block_timestamp
            first_buyer_or_seller = first.wallet_address
            first_type = first.transaction_type
            first_total_usd = first.total_value_usd
        
        # Convert to JSON
        json_data = json.dumps({
            "mint": meta.mint,
            "name": meta.name,
            "symbol": meta.symbol,
            "decimals": meta.decimals,
            "totalSupply": meta.total_supply,
            "totalSupplyFormatted": meta.total_supply_formatted,
            "sellerFeeBasisPoints": meta.seller_fee_basis_points,
            "isMutable": meta.is_mutable,
            "primarySaleHappened": meta.primary_sale_happened,
            "updateAuthority": meta.update_authority,
            "usdPrice": price.usd_price,
            "nativePriceValue": price.native_price_value,
            "exchangeName": price.exchange_name,
            "exchangeAddress": price.exchange_address,
            "firstSwapTimestamp": first_swap_time.isoformat() if first_swap_time else "",
            "firstSwapType": first_type,
            "firstBuyerOrSeller": first_buyer_or_seller,
            "firstTradeValueUsd": first_total_usd,
            "label": is_fraud_label 
        }, indent=4)
        
        # Create json_output directory if it doesn't exist
        output_dir = Path("json_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp
        timestamp = int(time.time())
        filename = f"token_data_{token}_{timestamp}.json"
        file_path = output_dir / filename
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f"Token data successfully exported to: {file_path}")
        
    except requests.RequestException as e:
        print(f"API request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    with open('coins.txt', 'r', encoding='utf-8') as file:
        coins = [line.strip() for line in file.readlines() if line.strip()]

    for coin in tqdm(coins, total=len(coins), desc="Processing tokens", colour="green"):
        print(f"Processing token: {coin}")
        is_fraud_label = fetch_label_on_rugcheck(coin)
        if is_fraud_label == -1:
            print(f"Failed to fetch label for token {coin}, skipping...")
            continue
        main(
            token=coin.strip(),
            is_fraud_label=is_fraud_label
        )
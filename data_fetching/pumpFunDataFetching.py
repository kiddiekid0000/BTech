import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjVjZDZjZDk5LTg5MjUtNGRiYS1iZWQyLWJjNzNkYzQ3ZTVmYSIsIm9yZ0lkIjoiNDU5ODY2IiwidXNlcklkIjoiNDczMTE4IiwidHlwZUlkIjoiOTVjZGQwYmMtNDViYi00MWVhLWEwMGItMWRhODZjZDNiM2Q2IiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NTI3NjcyNjUsImV4cCI6NDkwODUyNzI2NX0.BOMHcWhyTzWhnT3an-pporsYhIGm0yGyCO2CZ381liY"
BASE_URL = "https://solana-gateway.moralis.io"

# Set this to the token mint address you want to test
TOKEN_MINT = "CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump"  # Using a token from the actual response
IS_FRAUD_LABEL = 0  # 1 = Fraud, 0 = Legit


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


class UnifiedTokenData:
    def __init__(self):
        self.mint = ""
        self.name = ""
        self.symbol = ""
        self.decimals = ""
        self.total_supply = ""
        self.total_supply_formatted = ""
        self.seller_fee_basis_points = 0
        self.is_mutable = False
        self.primary_sale_happened = False
        self.update_authority = ""
        
        self.usd_price = 0.0
        self.native_price_value = ""
        self.exchange_name = ""
        self.exchange_address = ""
        
        self.first_swap_timestamp = None
        self.first_swap_type = ""
        self.first_buyer_or_seller = ""
        self.first_trade_value_usd = 0.0
        
        self.label = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mint": self.mint,
            "name": self.name,
            "symbol": self.symbol,
            "decimals": self.decimals,
            "totalSupply": self.total_supply,
            "totalSupplyFormatted": self.total_supply_formatted,
            "sellerFeeBasisPoints": self.seller_fee_basis_points,
            "isMutable": self.is_mutable,
            "primarySaleHappened": self.primary_sale_happened,
            "updateAuthority": self.update_authority,
            "usdPrice": self.usd_price,
            "nativePriceValue": self.native_price_value,
            "exchangeName": self.exchange_name,
            "exchangeAddress": self.exchange_address,
            "firstSwapTimestamp": self.first_swap_timestamp.isoformat() if self.first_swap_timestamp else "",
            "firstSwapType": self.first_swap_type,
            "firstBuyerOrSeller": self.first_buyer_or_seller,
            "firstTradeValueUsd": self.first_trade_value_usd,
            "label": self.label
        }


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


def main():
    token = TOKEN_MINT
    
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
        
        # Aggregate
        aggregated = UnifiedTokenData()
        aggregated.mint = meta.mint
        aggregated.name = meta.name
        aggregated.symbol = meta.symbol
        aggregated.decimals = meta.decimals
        aggregated.total_supply = meta.total_supply
        aggregated.total_supply_formatted = meta.total_supply_formatted
        aggregated.seller_fee_basis_points = meta.seller_fee_basis_points
        aggregated.is_mutable = meta.is_mutable
        aggregated.primary_sale_happened = meta.primary_sale_happened == 1
        aggregated.update_authority = meta.update_authority
        aggregated.usd_price = price.usd_price
        aggregated.native_price_value = price.native_price_value
        aggregated.exchange_name = price.exchange_name
        aggregated.exchange_address = price.exchange_address
        aggregated.first_swap_timestamp = first_swap_time
        aggregated.first_swap_type = first_type
        aggregated.first_buyer_or_seller = first_buyer_or_seller
        aggregated.first_trade_value_usd = first_total_usd
        aggregated.label = IS_FRAUD_LABEL  # Set label based on fraud status
        
        # Convert to JSON
        json_data = json.dumps(aggregated.to_dict(), indent=2)
        
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
    main()

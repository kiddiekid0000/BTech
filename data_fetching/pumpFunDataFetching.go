package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

const apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjVjZDZjZDk5LTg5MjUtNGRiYS1iZWQyLWJjNzNkYzQ3ZTVmYSIsIm9yZ0lkIjoiNDU5ODY2IiwidXNlcklkIjoiNDczMTE4IiwidHlwZUlkIjoiOTVjZGQwYmMtNDViYi00MWVhLWEwMGItMWRhODZjZDNiM2Q2IiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NTI3NjcyNjUsImV4cCI6NDkwODUyNzI2NX0.BOMHcWhyTzWhnT3an-pporsYhIGm0yGyCO2CZ381liY"
const baseURL = "https://solana-gateway.moralis.io"

// Set this to the token mint address you want to test
var tokenMint = "CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump" // Using a token from the actual response
const isFraudLabel = 0                                         // 1 = Fraud, 0 = Legit


// Structs

// Metadata
type MetadataResponse struct {
	Mint                 string `json:"mint"`
	Name                 string `json:"name"`
	Symbol               string `json:"symbol"`
	Decimals             string `json:"decimals"`
	TotalSupply          string `json:"totalSupply"`
	TotalSupplyFormatted string `json:"totalSupplyFormatted"`
	Metaplex             struct {
		SellerFeeBasisPoints int    `json:"sellerFeeBasisPoints"`
		IsMutable            bool   `json:"isMutable"`
		PrimarySaleHappened  int    `json:"primarySaleHappened"`
		UpdateAuthority      string `json:"updateAuthority"`
	} `json:"metaplex"`
}

// Price
type PriceResponse struct {
	UsdPrice    float64 `json:"usdPrice"`
	NativePrice struct {
		Value string `json:"value"`
	} `json:"nativePrice"`
	ExchangeName    string `json:"exchangeName"`
	ExchangeAddress string `json:"exchangeAddress"`
}

// Swap
type SwapsResponse struct {
	Result []struct {
		TransactionType string    `json:"transactionType"`
		BlockTimestamp  time.Time `json:"blockTimestamp"`
		WalletAddress   string    `json:"walletAddress"`
		TotalValueUsd   float64   `json:"totalValueUsd"`
	} `json:"result"`
}

// Unified Schema
type UnifiedTokenData struct {
	Mint                 string `json:"mint"`
	Name                 string `json:"name"`
	Symbol               string `json:"symbol"`
	Decimals             string `json:"decimals"`
	TotalSupply          string `json:"totalSupply"`
	TotalSupplyFormatted string `json:"totalSupplyFormatted"`
	SellerFeeBasisPoints int    `json:"sellerFeeBasisPoints"`
	IsMutable            bool   `json:"isMutable"`
	PrimarySaleHappened  bool   `json:"primarySaleHappened"`
	UpdateAuthority      string `json:"updateAuthority"`

	UsdPrice         float64 `json:"usdPrice"`
	NativePriceValue string  `json:"nativePriceValue"`
	ExchangeName     string  `json:"exchangeName"`
	ExchangeAddress  string  `json:"exchangeAddress"`

	FirstSwapTimestamp time.Time `json:"firstSwapTimestamp"`
	FirstSwapType      string    `json:"firstSwapType"`
	FirstBuyerOrSeller string    `json:"firstBuyerOrSeller"`
	FirstTradeValueUsd float64   `json:"firstTradeValueUsd"`

	Label int `json:"label"` // Added label field
}

func fetchJSON(url string, result interface{}) error {
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Add("X-API-Key", apiKey)
	req.Header.Add("accept", "application/json")
	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()
	body, _ := ioutil.ReadAll(res.Body)
	return json.Unmarshal(body, result)
}

func main() {
	token := tokenMint

	// Fetch metadata
	meta := MetadataResponse{}
	err := fetchJSON(fmt.Sprintf("%s/token/mainnet/%s/metadata", baseURL, token), &meta)
	if err != nil {
		log.Fatal("Metadata fetch failed:", err)
	}

	// Fetch price
	price := PriceResponse{}
	err = fetchJSON(fmt.Sprintf("%s/token/mainnet/%s/price", baseURL, token), &price)
	if err != nil {
		log.Fatal("Price fetch failed:", err)
	}

	// Fetch swaps
	swaps := SwapsResponse{}
	err = fetchJSON(fmt.Sprintf("%s/token/mainnet/%s/swaps?order=ASC&limit=1", baseURL, token), &swaps)
	if err != nil {
		log.Fatal("Swap fetch failed:", err)
	}
	var firstSwapTime time.Time
	var firstBuyerOrSeller string
	var firstType string
	var firstTotalUSD float64
	if len(swaps.Result) > 0 {
		first := swaps.Result[0] // Oldest
		firstSwapTime = first.BlockTimestamp
		firstBuyerOrSeller = first.WalletAddress
		firstType = first.TransactionType
		firstTotalUSD = first.TotalValueUsd
	}

	// Aggregate
	aggregated := UnifiedTokenData{
		Mint:                 meta.Mint,
		Name:                 meta.Name,
		Symbol:               meta.Symbol,
		Decimals:             meta.Decimals,
		TotalSupply:          meta.TotalSupply,
		TotalSupplyFormatted: meta.TotalSupplyFormatted,
		SellerFeeBasisPoints: meta.Metaplex.SellerFeeBasisPoints,
		IsMutable:            meta.Metaplex.IsMutable,
		PrimarySaleHappened:  meta.Metaplex.PrimarySaleHappened == 1,
		UpdateAuthority:      meta.Metaplex.UpdateAuthority,
		UsdPrice:             price.UsdPrice,
		NativePriceValue:     price.NativePrice.Value,
		ExchangeName:         price.ExchangeName,
		ExchangeAddress:      price.ExchangeAddress,
		FirstSwapTimestamp:   firstSwapTime,
		FirstSwapType:        firstType,
		FirstBuyerOrSeller:   firstBuyerOrSeller,
		FirstTradeValueUsd:   firstTotalUSD,
		Label:                isFraudLabel, // Set label based on fraud status
	}

	jsonData, err := json.MarshalIndent(aggregated, "", "  ")
	if err != nil {
		log.Fatal("JSON marshaling failed:", err)
	}

	// Create json_output directory if it doesn't exist
	outputDir := "json_output"
	err = os.MkdirAll(outputDir, 0755)
	if err != nil {
		log.Fatal("Directory creation failed:", err)
	}

	// Create filename with timestamp
	filename := fmt.Sprintf("token_data_%s_%d.json", token, time.Now().Unix())
	filePath := filepath.Join(outputDir, filename)

	// Write to file
	err = ioutil.WriteFile(filePath, jsonData, 0644)
	if err != nil {
		log.Fatal("File writing failed:", err)
	}

	fmt.Printf("Token data successfully exported to: %s\n", filePath)
}

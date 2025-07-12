// This code fetch info for "Raydium Hot Wallet"   (Well I don't understand what it is much yet)

import { Connection, PublicKey } from "@solana/web3.js";

async function fetchTransactionLogs(walletAddress, limit = 10) { // Increased limit
  const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");
  const publicKey = new PublicKey(walletAddress);

  const transactionSignatures = await connection.getSignaturesForAddress(publicKey, { 
    limit, 
    before: undefined, // Fetch newest first
  });

  if (transactionSignatures.length === 0) {
    console.log("No transactions found.");
    return;
  }

  transactionSignatures.forEach((tx, index) => {
    const time = new Date(tx.blockTime * 1000).toString();
    console.log(`Transaction No: ${index + 1}`);
    console.log(`Signature: ${tx.signature}`);
    console.log(`Time: ${time}`);
    console.log(`Status: ${tx.confirmationStatus || "finalized"}\n`);
  });
}

// Try a more active wallet (e.g., Raydium or Orca)
const WALLET_ADDRESS = "vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg"; // Example: Raydium Hot Wallet
fetchTransactionLogs(WALLET_ADDRESS, 10); // Fetch 10 most recent txs
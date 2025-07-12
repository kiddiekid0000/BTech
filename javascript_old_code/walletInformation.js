// This code is tested for fetching data of a wallet address, my idea is to get a punch of wallet address from the 'walletaddress.js' file, but it doesn't work then to run this code on the collected wallet address
// The wallet address is just an example address from file 'index.js' which I watch on youtube of Solana official channel --> I 
import { Connection, PublicKey } from "@solana/web3.js";

async function fetchTransactionLogs(walletAddress, limit = 3) {
  const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");
  const publicKey = new PublicKey(walletAddress);

  // Fetch confirmed signatures (transactions) for the wallet
  const transactionSignatures = await connection.getSignaturesForAddress(publicKey, { limit });

  if (transactionSignatures.length === 0) {
    console.log("No transactions found for this wallet.");
    return;
  }

  // Print formatted logs
  transactionSignatures.forEach((tx, index) => {
    const time = new Date(tx.blockTime * 1000).toString();
    console.log(`Transaction No: ${index + 1}`);
    console.log(`Signature: ${tx.signature}`);
    console.log(`Time: ${time}`);
    console.log(`Status: ${tx.confirmationStatus || "finalized"}\n`);
  });
}

// Example: Fetch logs for a wallet (replace with your target address)
const WALLET_ADDRESS = "GXjTyatXj6fgXxKXW3LgbQDH1Y4UffLQw5x6MrLWyAe1"; // Replace with any Solana wallet
fetchTransactionLogs(WALLET_ADDRESS, 3); // Fetch 3 most recent transactions


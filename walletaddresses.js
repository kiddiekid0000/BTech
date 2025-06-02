import { Connection, PublicKey } from "@solana/web3.js";

const PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"; // this is the Pump.fun program ID, this code aim to get fetch the wallet addresses from pump.fun, but it doesn't fully work yet
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchWalletAddressesFromProgram(programId, limit = 5) {
  const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");
  const programPublicKey = new PublicKey(programId);

  console.log(`🔍 Fetching up to ${limit} transactions for program: ${programId}...\n`);

  const signatures = await connection.getSignaturesForAddress(programPublicKey, { limit });

  if (signatures.length === 0) {
    console.log("❌ No transactions found for this program.");
    return;
  }

  const wallets = new Set();

  for (const sig of signatures) {
    try {
      console.log(`⏳ Fetching tx: ${sig.signature}`);
      await sleep(1200); // Avoid 429 error by delaying
      const tx = await connection.getTransaction(sig.signature, {
        maxSupportedTransactionVersion: 0,
      });

      if (!tx || !tx.transaction) {
        console.warn(`⚠️ Skipped tx ${sig.signature} — no transaction data.`);
        continue;
      }

      tx.transaction.message.accountKeys.forEach(account => {
        wallets.add(account.toBase58());
      });

    } catch (err) {
      console.warn(`⚠️ Error fetching tx ${sig.signature}: ${err.message}`);
    }
  }

  console.log(`\n✅ Found ${wallets.size} unique wallet addresses:\n`);
  [...wallets].forEach((wallet, index) => {
    console.log(`${index + 1}. ${wallet}`);
  });

  // Return list if you want to use it elsewhere
  return [...wallets];
}

// 🔥 Run it
fetchWalletAddressesFromProgram(PROGRAM_ID, 1);

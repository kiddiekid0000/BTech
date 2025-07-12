// This code get info from a token account (I dont understand this much, just copy it from a solana official website to test)
import { Connection, PublicKey } from "@solana/web3.js";

async function getTokenAccountInfo() {
  try {
    const connection = new Connection('https://api.mainnet-beta.solana.com');
    const usdcTokenAccount = new PublicKey('GXjTyatXj6fgXxKXW3LgbQDH1Y4UffLQw5x6MrLWyAe1'); 
    const usdcTokenAccountInfo = await connection.getAccountInfo(usdcTokenAccount); 
    console.log(usdcTokenAccountInfo);
  } catch (error) {
    console.error("Error:", error);
  }
}

getTokenAccountInfo();
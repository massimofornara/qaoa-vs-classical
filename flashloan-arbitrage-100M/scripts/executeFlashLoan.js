require("dotenv").config();
const { ethers } = require("ethers");
const fs = require("fs");

const abi = JSON.parse(fs.readFileSync("./artifacts/contracts/FlashLoanArbitrage.sol/FlashLoanArbitrage.json")).abi;

const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
const contractAddress = process.env.CONTRACT_ADDRESS;

async function main() {
  const contract = new ethers.Contract(contractAddress, abi, wallet);
  const amount = ethers.utils.parseUnits("100000000", 6); // 100M USDC
  const tx = await contract.executeFlashLoan(amount);
  console.log("📤 TX inviata:", tx.hash);
  await tx.wait();
  console.log("✅ FlashLoan completato.");
}

main();

// scripts/deploy.js
// Deploys ForensicAuditLedger to the local Hardhat node and writes the
// contract address + ABI to deployed/contract_info.json for the FastAPI backend.

const { ethers } = require("hardhat");
const path = require("path");
const fs = require("fs");

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("=".repeat(60));
  console.log("Anvex — Deploying ForensicAuditLedger");
  console.log("=".repeat(60));
  console.log(`Deployer address : ${deployer.address}`);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`Deployer balance : ${ethers.formatEther(balance)} ETH`);

  // Deploy
  const ForensicAuditLedger = await ethers.getContractFactory("ForensicAuditLedger");
  const contract = await ForensicAuditLedger.deploy();
  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log(`\n✅ ForensicAuditLedger deployed at: ${contractAddress}`);

  // Extract ABI from the compiled artifact
  const artifactPath = path.join(
    __dirname,
    "..",
    "artifacts",
    "contracts",
    "ForensicAuditLedger.sol",
    "ForensicAuditLedger.json"
  );
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

  // Write shared contract_info.json — FastAPI backend reads this at startup
  const deployedDir = path.join(__dirname, "..", "deployed");
  if (!fs.existsSync(deployedDir)) {
    fs.mkdirSync(deployedDir, { recursive: true });
  }

  const contractInfo = {
    address: contractAddress,
    abi: artifact.abi,
    network: "localhost",
    chainId: 31337,
    deployedAt: new Date().toISOString(),
    deployer: deployer.address,
  };

  const outputPath = path.join(deployedDir, "contract_info.json");
  fs.writeFileSync(outputPath, JSON.stringify(contractInfo, null, 2));

  console.log(`📄 Contract info written to: ${outputPath}`);
  console.log("\nNext steps:");
  console.log("  1. Keep `npx hardhat node` running in a terminal.");
  console.log("  2. Start the FastAPI backend: cd ../dashboard_backend && uvicorn main:app --reload");
  console.log("  3. Start the React frontend: cd ../soc_frontend && npm run dev");
  console.log("=".repeat(60));
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});

const { spawn } = require("child_process");
const path = require("path");
const proc = spawn("C:\\nvm4w\\nodejs\\npx.cmd", ["hardhat", "node"], {
  cwd: path.join(__dirname, "trust_layer"),
  stdio: "inherit",
  shell: true,
});
proc.on("exit", (code) => process.exit(code));

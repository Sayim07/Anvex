const { spawn } = require("child_process");
const proc = spawn("C:\\nvm4w\\nodejs\\npx.cmd", ["hardhat", "node"], {
  cwd: "C:\\Users\\sayim\\OneDrive\\Documents\\Avnex\\trust_layer",
  stdio: "inherit",
  shell: true,
});
proc.on("exit", (code) => process.exit(code));

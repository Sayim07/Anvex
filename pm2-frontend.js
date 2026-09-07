const { spawn } = require("child_process");
const path = require("path");
const proc = spawn("C:\\nvm4w\\nodejs\\npm.cmd", ["run", "dev"], {
  cwd: path.join(__dirname, "soc_frontend"),
  stdio: "inherit",
  shell: true,
});
proc.on("exit", (code) => process.exit(code));

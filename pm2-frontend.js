const { spawn } = require("child_process");
const proc = spawn("C:\\nvm4w\\nodejs\\npm.cmd", ["run", "dev"], {
  cwd: "C:\\Users\\sayim\\OneDrive\\Documents\\Avnex\\soc_frontend",
  stdio: "inherit",
  shell: true,
});
proc.on("exit", (code) => process.exit(code));

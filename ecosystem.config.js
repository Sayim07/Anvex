module.exports = {
  apps: [
    {
      name: "anvex-blockchain",
      script: "C:/Users/sayim/OneDrive/Documents/Avnex/pm2-blockchain.js",
      autorestart: true,
      watch: false,
      max_memory_restart: "512M",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
    {
      name: "anvex-backend",
      cwd: "C:/Users/sayim/OneDrive/Documents/Avnex/dashboard_backend",
      script: "C:/Users/sayim/AppData/Local/Programs/Python/Python311/python.exe",
      args: "-m uvicorn main:app --host 0.0.0.0 --port 8000",
      autorestart: true,
      watch: false,
      max_memory_restart: "512M",
      restart_delay: 5000,
      env: { PYTHONUNBUFFERED: "1" },
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
    {
      name: "anvex-frontend",
      script: "C:/Users/sayim/OneDrive/Documents/Avnex/pm2-frontend.js",
      autorestart: true,
      watch: false,
      max_memory_restart: "512M",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
  ],
};

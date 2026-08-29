@echo off
title Anvex Services
cd /d "C:\Users\sayim\OneDrive\Documents\Avnex"
echo Starting Anvex services via PM2...
call "%APPDATA%\npm\pm2.cmd" resurrect
echo All Anvex services started!

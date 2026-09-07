@echo off
title Anvex Services
cd /d "%~dp0"
echo Starting Anvex services via PM2...
call "%APPDATA%\npm\pm2.cmd" resurrect
echo All Anvex services started!

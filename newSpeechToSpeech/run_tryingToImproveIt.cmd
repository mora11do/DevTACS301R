@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%tryingToImproveIt"

cd /d "%APP_DIR%"
npm.cmd run dev


@echo off
setlocal EnableDelayedExpansion

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator
    pause
    exit /b 1
)

REM Install Chocolatey if missing
where choco >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Chocolatey...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy AllSigned -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
)

REM Create .env file with necessary variables
echo Creating .env file...
if exist .env (
    echo .env file already exists. Skipping creation.
) else (
    set /p ETSY_CLIENT_ID="Enter ETSY_CLIENT_ID: "
    set /p ETSY_ACCESS_TOKEN="Enter ETSY_ACCESS_TOKEN: "
    set /p ETSY_REFRESH_TOKEN="Enter ETSY_REFRESH_TOKEN: "
    (
        echo ETSY_CLIENT_ID=%ETSY_CLIENT_ID%
        echo ETSY_ACCESS_TOKEN=%ETSY_ACCESS_TOKEN%
        echo ETSY_REFRESH_TOKEN=%ETSY_REFRESH_TOKEN%
        echo PORT=8000
    ) > .env
)

REM Install Python if not installed
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Python...
    choco install python -y
    set PATH=%PATH%;C:\Python311\Scripts;C:\Python311
)

REM Install Node.js if not installed
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Node.js...
    choco install nodejs -y
    set PATH=%PATH%;C:\Program Files\nodejs
)

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo requirements.txt not found!
    pause
    exit /b 1
)

REM Create and activate virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate
if %errorLevel% neq 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check if frontend directory exists
if not exist my-app (
    echo Frontend directory 'my-app' not found!
    pause
    exit /b 1
)

REM Setup frontend
cd my-app
echo Installing Node.js dependencies...
call npm install
if %errorLevel% neq 0 (
    echo Failed to install Node.js dependencies
    cd ..
    pause
    exit /b 1
)

echo Building the frontend...
call npm run build
cd ..

REM Start servers
echo Starting the FastAPI backend...
start cmd /k "venv\Scripts\activate && python app.py"

echo Starting the frontend development server...
cd my-app
start cmd /k "npm run dev"

echo Setup complete! Check the opened terminals for the backend and frontend servers.
pause
@echo off
REM Create .env file with necessary variables
echo Creating .env file...
(
  echo ETSY_CLIENT_ID=your_client_id_here
  echo ETSY_ACCESS_TOKEN=your_access_token_here
  echo ETSY_REFRESH_TOKEN=your_refresh_token_here
  echo PORT=8000
) > .env

REM update
echo Updating...
apt update
REM Upgrade
echo Upgrading...
apt upgrade
REM Install Python
echo Installing Python...
choco install python -y
REM Install Node.js
echo Installing Node.js...
choco install nodejs -y
REM Create a virtual environment
echo Creating a virtual environment...
python -m venv venv
REM activate the virtual environment
echo Activating the virtual environment...
venv\Scripts\activate
REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Navigate to the frontend directory (assuming it's named 'my-app')
echo Setting up the frontend...
cd my-app

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

REM Build the frontend (if needed)
echo Building the frontend...
npm run build

REM Return to the root directory
cd ..

REM Run the FastAPI backend
echo Starting the FastAPI backend...
start python app.py

REM Run the frontend development server
echo Starting the frontend development server...
cd my-app
start npm run dev

echo Setup complete! Check the opened terminals for the backend and frontend servers.
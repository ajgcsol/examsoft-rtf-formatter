#!/usr/bin/env powershell
# ExamSoft Formatter Startup Script
# This script starts both the Streamlit app and the LibreOffice conversion service

Write-Host "🚀 Starting ExamSoft Formatter..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start LibreOffice conversion service in background
Write-Host "🐳 Starting LibreOffice conversion service..."
Start-Process -WindowStyle Hidden -FilePath "docker" -ArgumentList "run", "-p", "8080:8080", "libreoffice-converter"
Start-Sleep -Seconds 3

# Test if conversion service is ready
$maxAttempts = 10
$attempt = 0
$serviceReady = $false

Write-Host "⏳ Waiting for conversion service to be ready..."
while ($attempt -lt $maxAttempts -and -not $serviceReady) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8080/convert" -Method GET -TimeoutSec 2 -ErrorAction Stop | Out-Null
        $serviceReady = $true
    } catch {
        $attempt++
        Start-Sleep -Seconds 2
        Write-Host "   Attempt $attempt/$maxAttempts..." -ForegroundColor Yellow
    }
}

if ($serviceReady) {
    Write-Host "✅ Conversion service ready at http://localhost:8080" -ForegroundColor Green
} else {
    Write-Host "⚠️  Conversion service may not be ready, but continuing..." -ForegroundColor Yellow
}

# Activate virtual environment and start Streamlit
Write-Host "🎨 Starting Streamlit app..."
Write-Host ""
Write-Host "📱 Streamlit app will open at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "🔧 Conversion API available at: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow
Write-Host ""

& "./.venv_new/Scripts/Activate.ps1"
streamlit run examsoft_formatter_updated.py

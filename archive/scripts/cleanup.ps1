#!/usr/bin/env powershell
# ExamSoft Formatter Cleanup Script
# This script stops all running Docker containers and cleans up

Write-Host "🧹 Cleaning up ExamSoft Formatter services..." -ForegroundColor Yellow
Write-Host ""

# Stop all libreoffice-converter containers
Write-Host "🛑 Stopping LibreOffice conversion service containers..."
$containers = docker ps --filter "ancestor=libreoffice-converter" --format "{{.ID}}"

if ($containers) {
    foreach ($container in $containers) {
        Write-Host "   Stopping container: $container"
        docker stop $container | Out-Null
    }
    Write-Host "✅ All LibreOffice containers stopped" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No LibreOffice containers running" -ForegroundColor Blue
}

# Optionally remove stopped containers
Write-Host ""
$choice = Read-Host "Remove stopped containers? (y/N)"
if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host "🗑️  Removing stopped containers..."
    docker container prune -f | Out-Null
    Write-Host "✅ Stopped containers removed" -ForegroundColor Green
}

# Show running processes that might be Streamlit
Write-Host ""
Write-Host "📊 Checking for running Streamlit processes..."
$streamlitProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*streamlit*" } -ErrorAction SilentlyContinue

if ($streamlitProcesses) {
    Write-Host "⚠️  Found Streamlit processes. You may need to close them manually:" -ForegroundColor Yellow
    $streamlitProcesses | ForEach-Object { Write-Host "   PID: $($_.Id) - $($_.ProcessName)" }
} else {
    Write-Host "ℹ️  No Streamlit processes found" -ForegroundColor Blue
}

Write-Host ""
Write-Host "✅ Cleanup complete!" -ForegroundColor Green

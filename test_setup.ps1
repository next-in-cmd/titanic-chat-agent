# Titanic Chatbot - Local Test Script
# Run this to verify your setup before deploying

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚢 TITANIC CHATBOT - LOCAL TEST SCRIPT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Test 1: Python Version
Write-Host "Test 1: Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host $pythonVersion -ForegroundColor Green
Write-Host ""

# Test 2: Virtual Environment
Write-Host "Test 2: Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\activate") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found" -ForegroundColor Red
    Write-Host "Run: python -m venv venv" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: Dataset
Write-Host "Test 3: Checking dataset..." -ForegroundColor Yellow
if (Test-Path "data\Titanic-Dataset.csv") {
    $rows = (Get-Content "data\Titanic-Dataset.csv" | Measure-Object -Line).Lines - 1
    Write-Host "✓ Dataset found with $rows passengers" -ForegroundColor Green
} else {
    Write-Host "✗ Dataset not found at data\Titanic-Dataset.csv" -ForegroundColor Red
}
Write-Host ""

# Test 4: Environment File
Write-Host "Test 4: Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found (OK if using Streamlit secrets)" -ForegroundColor Yellow
}

if (Test-Path ".streamlit\secrets.toml") {
    Write-Host "✓ Streamlit secrets.toml exists" -ForegroundColor Green
} else {
    Write-Host "⚠ .streamlit\secrets.toml not found" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Git Status
Write-Host "Test 5: Checking Git status..." -ForegroundColor Yellow
$gitStatus = git status --short
if ($gitStatus) {
    Write-Host "⚠ Uncommitted changes:" -ForegroundColor Yellow
    git status --short
} else {
    Write-Host "✓ Git repository is clean" -ForegroundColor Green
}
Write-Host ""

# Test 6: Package Imports
Write-Host "Test 6: Testing package imports..." -ForegroundColor Yellow

Write-Host "  Activating virtual environment..." -ForegroundColor Gray
.\venv\Scripts\activate

$tests = @(
    @{Name="Streamlit"; Command="import streamlit; print('OK')"},
    @{Name="Pandas"; Command="import pandas; print('OK')"},
    @{Name="Matplotlib"; Command="import matplotlib; print('OK')"},
    @{Name="LangChain"; Command="import langchain; print('OK')"},
    @{Name="LangChain-Groq"; Command="from langchain_groq import ChatGroq; print('OK')"},
    @{Name="Groq"; Command="import groq; print('OK')"}
)

foreach ($test in $tests) {
    try {
        $result = python -c $test.Command 2>&1
        if ($result -eq "OK") {
            Write-Host "  ✓ $($test.Name)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $($test.Name) - $result" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ $($test.Name) - Import failed" -ForegroundColor Red
    }
}
Write-Host ""

# Test 7: Package Versions
Write-Host "Test 7: Checking package versions..." -ForegroundColor Yellow
$packages = @("streamlit", "langchain", "langchain-groq", "groq", "pandas")

foreach ($pkg in $packages) {
    $version = pip show $pkg 2>$null | Select-String "Version:"
    if ($version) {
        Write-Host "  $pkg - $version" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $pkg - Not installed" -ForegroundColor Red
    }
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If all tests passed (✓), you can:" -ForegroundColor White
Write-Host "1. Test locally: streamlit run streamlit_app.py" -ForegroundColor Cyan
Write-Host "2. Push to GitHub: git push origin main" -ForegroundColor Cyan
Write-Host "3. Deploy on Streamlit Cloud" -ForegroundColor Cyan
Write-Host ""
Write-Host "If any tests failed (✗):" -ForegroundColor White
Write-Host "1. Install missing packages: pip install -r requirements.txt" -ForegroundColor Yellow
Write-Host "2. Check data/Titanic-Dataset.csv exists" -ForegroundColor Yellow
Write-Host "3. Review FINAL_DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
Write-Host ""

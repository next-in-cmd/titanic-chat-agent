# Quick Deployment Script for Streamlit Cloud
# Run this script to prepare and push your project to GitHub

Write-Host "🚢 Titanic Chat Agent - Streamlit Cloud Deployment" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if git is initialized
Write-Host "Step 1: Checking Git repository..." -ForegroundColor Yellow
if (Test-Path .git) {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
} else {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
}

Write-Host ""

# Step 2: Add files
Write-Host "Step 2: Adding files to Git..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files added" -ForegroundColor Green

Write-Host ""

# Step 3: Commit
Write-Host "Step 3: Committing changes..." -ForegroundColor Yellow
$commitMessage = "Prepare for Streamlit Cloud deployment"
git commit -m $commitMessage
Write-Host "✓ Changes committed" -ForegroundColor Green

Write-Host ""

# Step 4: Get GitHub username and repo
Write-Host "Step 4: GitHub Configuration" -ForegroundColor Yellow
Write-Host ""
$githubUsername = Read-Host "Enter your GitHub username"
$repoName = "titanic-chat-agent"

Write-Host ""
Write-Host "Repository URL will be: https://github.com/$githubUsername/$repoName" -ForegroundColor Cyan

# Step 5: Add remote (if not exists)
Write-Host ""
Write-Host "Step 5: Configuring remote repository..." -ForegroundColor Yellow

$remoteExists = git remote | Select-String -Pattern "origin"
if ($remoteExists) {
    Write-Host "Remote 'origin' already exists. Removing..." -ForegroundColor Yellow
    git remote remove origin
}

$remoteUrl = "https://github.com/$githubUsername/$repoName.git"
git remote add origin $remoteUrl
Write-Host "✓ Remote configured: $remoteUrl" -ForegroundColor Green

Write-Host ""

# Step 6: Push to GitHub
Write-Host "Step 6: Pushing to GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT: Make sure you've created the repository on GitHub first!" -ForegroundColor Red
Write-Host "Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "Repository name: $repoName" -ForegroundColor Cyan
Write-Host "Do NOT initialize with README" -ForegroundColor Red
Write-Host ""

$continue = Read-Host "Have you created the GitHub repository? (Y/N)"
if ($continue -eq "Y" -or $continue -eq "y") {
    git branch -M main
    git push -u origin main
    Write-Host "✓ Pushed to GitHub successfully!" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ DEPLOYMENT PREPARATION COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Go to: https://share.streamlit.io/" -ForegroundColor White
    Write-Host "2. Sign in with GitHub" -ForegroundColor White
    Write-Host "3. Click 'New app'" -ForegroundColor White
    Write-Host "4. Select repository: $githubUsername/$repoName" -ForegroundColor White
    Write-Host "5. Branch: main" -ForegroundColor White
    Write-Host "6. Main file: streamlit_app.py" -ForegroundColor White
    Write-Host "7. Click 'Advanced settings' and add secrets:" -ForegroundColor White
    Write-Host ""
    Write-Host "   Secrets to add (copy from .streamlit/secrets.toml):" -ForegroundColor Yellow
    Write-Host "   GROQ_API_KEY = `"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`"" -ForegroundColor Gray
    Write-Host "   MODEL_NAME = `"llama-3.3-70b-versatile`"" -ForegroundColor Gray
    Write-Host "   TEMPERATURE = `"0`"" -ForegroundColor Gray
    Write-Host "   CHART_DPI = `"100`"" -ForegroundColor Gray
    Write-Host ""
    Write-Host "8. Click 'Deploy'!" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Your app will be live at:" -ForegroundColor Cyan
    Write-Host "https://$githubUsername-$repoName-main.streamlit.app" -ForegroundColor Green
    Write-Host ""
    
} else {
    Write-Host ""
    Write-Host "⏸ Deployment paused. Please:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
    Write-Host "2. Create repository: $repoName" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
    Write-Host ""
}

Write-Host "📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

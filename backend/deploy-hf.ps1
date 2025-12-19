# Hugging Face Spaces Deployment Script
# Run this after creating a space at https://huggingface.co/new-space

param(
    [Parameter(Mandatory=$true)]
    [string]$Username
)

$SpaceName = "brazeup-demo"

Write-Host "Deploying to Hugging Face Spaces..." -ForegroundColor Green

# Clone the space
Write-Host "Cloning space..." -ForegroundColor Yellow
git clone "https://huggingface.co/spaces/$Username/$SpaceName" "../hf-deploy-temp"

# Copy files
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item -Path ".\*" -Destination "..\hf-deploy-temp\" -Recurse -Force -Exclude @(".git", "__pycache__", "*.pyc", "uploads", "storage", "hf-deploy-temp")

# Deploy
Set-Location "..\hf-deploy-temp"
git add .
git commit -m "Deploy BrazeUp API"
git push

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Visit: https://huggingface.co/spaces/$Username/$SpaceName" -ForegroundColor Cyan

# Cleanup
Set-Location "..\backend"
Remove-Item -Path "..\hf-deploy-temp" -Recurse -Force

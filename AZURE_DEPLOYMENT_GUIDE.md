# 🚀 Complete Azure Deployment Guide - Applicant Database Application

**This guide will deploy both frontend and backend to Azure with zero mistakes.**

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Azure Account Setup](#azure-account-setup)
3. [Phase 1: Create Azure Resources](#phase-1-create-azure-resources)
4. [Phase 2: Configure Backend](#phase-2-configure-backend)
5. [Phase 3: Deploy Backend](#phase-3-deploy-backend)
6. [Phase 4: Deploy Frontend](#phase-4-deploy-frontend)
7. [Phase 5: Testing & Verification](#phase-5-testing--verification)
8. [Phase 6: Monitoring & Troubleshooting](#phase-6-monitoring--troubleshooting)

---

## ✅ Prerequisites

### Required Tools (Install If Missing)
```powershell
# 1. Azure CLI
# Download: https://aka.ms/installazurecliwindows
# Verify installation:
az --version

# 2. Git
# Download: https://git-scm.com/download/win
git --version

# 3. Docker (Optional but Recommended)
# Download: https://www.docker.com/products/docker-desktop
docker --version

# 4. Node.js (Already have this)
node --version
npm --version

# 5. Python 3.8+ (Already have this)
python --version
```

### Required Azure Accounts
- ✅ Azure Subscription (Free or Paid)
- ✅ Git repository (GitHub, Azure Repos, etc.)

---

## 🔐 Azure Account Setup

### Step 1: Login to Azure
```powershell
# Login to Azure CLI
az login

# This will open a browser. Sign in with your Microsoft account.
# Verify successful login:
az account show
```

### Step 2: Create Resource Group
```powershell
# Create a resource group in a location near you
# Available locations: eastus, westus, northeurope, westeurope, etc.

$resourceGroup = "rg-applicant-db"
$location = "eastus"  # Change based on your preference

az group create `
  --name $resourceGroup `
  --location $location

# Verify creation:
az group show --name $resourceGroup
```

### Step 3: Store Configuration Variables
```powershell
# Set these variables (use them in upcoming steps)
$subscriptionId = "your-subscription-id"  # Get from az account show
$resourceGroup = "rg-applicant-db"
$location = "eastus"
$appName = "applicant-db"  # Used for resource names
$environment = "prod"  # or "dev"

# Verify variables:
Write-Host "Resource Group: $resourceGroup"
Write-Host "Location: $location"
Write-Host "App Name: $appName"
```

---

## Phase 1: Create Azure Resources

### Step 1: Create Azure SQL Database

```powershell
# 1.1 Create SQL Server
$sqlServerName = "applicantdb-server"
$sqlAdminUser = "dbadmin"
$sqlAdminPassword = "YourSecurePassword@123"  # CHANGE THIS!

Write-Host "Creating SQL Server..."
az sql server create `
  --resource-group $resourceGroup `
  --name $sqlServerName `
  --location $location `
  --admin-user $sqlAdminUser `
  --admin-password $sqlAdminPassword

# 1.2 Create SQL Database
Write-Host "Creating SQL Database..."
az sql db create `
  --resource-group $resourceGroup `
  --server $sqlServerName `
  --name "applicants_db" `
  --edition "Basic" `
  --compute-model "Serverless" `
  --auto-pause-delay 60

# 1.3 Create Firewall Rule (Allow Azure Services)
Write-Host "Configuring firewall..."
az sql server firewall-rule create `
  --resource-group $resourceGroup `
  --server $sqlServerName `
  --name "AllowAzureServices" `
  --start-ip-address "0.0.0.0" `
  --end-ip-address "0.0.0.0"

# 1.4 Get Connection String
$dbServer = az sql server show `
  --resource-group $resourceGroup `
  --name $sqlServerName `
  --query "fullyQualifiedDomainName" -o tsv

Write-Host "SQL Server Created!"
Write-Host "Connection Details:"
Write-Host "  Server: $dbServer"
Write-Host "  Database: applicants_db"
Write-Host "  User: $sqlAdminUser"
Write-Host "  Password: *** (save securely)"
```

### Step 2: Create Azure Storage Account

```powershell
# 2.1 Create Storage Account
$storageAccountName = "applicantdbstorage"  # Must be 3-24 chars, lowercase, alphanumeric

Write-Host "Creating Storage Account..."
az storage account create `
  --resource-group $resourceGroup `
  --name $storageAccountName `
  --location $location `
  --sku "Standard_LRS" `
  --kind "StorageV2"

# 2.2 Get Storage Connection String
$storageConnectionString = az storage account show-connection-string `
  --resource-group $resourceGroup `
  --name $storageAccountName `
  --query "connectionString" -o tsv

Write-Host "Storage Account Created!"
Write-Host "Connection String: $storageConnectionString"

# 2.3 Create Container for Resumes
Write-Host "Creating blob container..."
az storage container create `
  --name "resumes" `
  --connection-string $storageConnectionString `
  --public-access off
```

### Step 3: Create App Service Plan

```powershell
# 3.1 Create App Service Plan (for Backend)
$appServicePlanName = "applicant-db-plan"

Write-Host "Creating App Service Plan..."
az appservice plan create `
  --resource-group $resourceGroup `
  --name $appServicePlanName `
  --sku "B1" `
  --is-linux

# 3.2 Create Web App for Backend
$backendAppName = "applicant-db-api-prod"

Write-Host "Creating Backend Web App..."
az webapp create `
  --resource-group $resourceGroup `
  --plan $appServicePlanName `
  --name $backendAppName `
  --runtime "PYTHON:3.11"

Write-Host "Backend App Created!"
Write-Host "URL: https://$backendAppName.azurewebsites.net"
```

### Step 4: Create Static Web App for Frontend

```powershell
# 4.1 Create Static Web App (Recommended for Next.js)
$frontendAppName = "applicant-db-app-prod"

Write-Host "Creating Frontend Static Web App..."
az staticwebapp create `
  --resource-group $resourceGroup `
  --name $frontendAppName `
  --location $location `
  --source "https://github.com/YOUR-USERNAME/applicant-database-app" `
  --branch "main" `
  --token "YOUR-GITHUB-TOKEN" `
  --app-location "frontend" `
  --output-location ".next"

Write-Host "Frontend Static Web App Created!"
Write-Host "URL: https://$frontendAppName.azurestaticapps.net"

# Note: Alternative: Use App Service if you prefer
# az webapp create --resource-group $resourceGroup --plan $appServicePlanName --name $frontendAppName --runtime "NODE:18-lts"
```

---

## Phase 2: Configure Backend

### Step 1: Create .env File for Production

Create `backend/.env.production` with the following content:

```
# Database Configuration - Azure SQL
DB_CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=applicantdb-server.database.windows.net;Database=applicants_db;UID=dbadmin;PWD=YourSecurePassword@123;

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=applicantdbstorage;AccountKey=YOUR_STORAGE_KEY;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=resumes

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here-change-this

# Frontend URL
FRONTEND_URL=https://applicant-db-app-prod.azurestaticapps.net

# Session Configuration
SESSION_TIMEOUT=3600
```

**To get Azure Storage Key:**
```powershell
az storage account keys list `
  --resource-group $resourceGroup `
  --account-name $storageAccountName `
  --query "[0].value" -o tsv
```

### Step 2: Initialize Azure SQL Database

```powershell
# 2.1 Connect to Azure SQL and run schema setup
# You'll need to update the database.py file to initialize the schema

# Navigate to backend directory
cd backend

# Run database initialization
python -c "from database import Database; db = Database(); db.init_db()"

# This will create the applicants table with the correct schema
```

### Step 3: Prepare Backend for Deployment

**Update [backend/requirements.txt](backend/requirements.txt):**
```
Flask==2.3.2
Flask-CORS==4.0.0
python-docx==0.8.11
pdfplumber==0.10.2
PyPDF2==3.0.1
pyodbc==4.0.39
azure-storage-blob==12.17.0
azure-identity==1.13.0
azure-data-tables==12.4.0
PyJWT==2.8.0
bcrypt==4.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
```

**Create [backend/startup.sh](backend/startup.sh):**
```bash
#!/bin/bash
gunicorn --bind 0.0.0.0 --workers 4 --timeout 60 app:app
```

**Create [backend/web.config](backend/web.config):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <staticContent>
      <mimeMap fileExtension=".py" mimeType="text/plain" />
    </staticContent>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="python" arguments="-m gunicorn --bind 0.0.0.0 --workers 4 app:app" startupTimeLimit="60" processesPerApplication="1">
    </httpPlatform>
  </system.webServer>
</configuration>
```

---

## Phase 3: Deploy Backend

### Step 1: Deploy Using Azure App Service

```powershell
# 3.1 Set environment variables in Azure App Service
Write-Host "Configuring App Service Environment Variables..."

az webapp config appsettings set `
  --resource-group $resourceGroup `
  --name $backendAppName `
  --settings `
    "DB_CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=applicantdb-server.database.windows.net;Database=applicants_db;UID=dbadmin;PWD=YourSecurePassword@123;" `
    "AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString" `
    "AZURE_CONTAINER_NAME=resumes" `
    "FLASK_ENV=production" `
    "FLASK_DEBUG=0" `
    "SECRET_KEY=your-secret-key-generate-one" `
    "FRONTEND_URL=https://$frontendAppName.azurestaticapps.net"

# 3.2 Deploy using Git (if in GitHub)
# First, add your Git repository
cd applicant-database-app

# Initialize Git (if not already done)
git init
git add .
git commit -m "Initial commit for Azure deployment"

# Add Azure remote
$repoUrl = "https://$resourceGroup/$backendAppName.scm.azurewebsites.net:443/$backendAppName.git"
git remote add azure $repoUrl

# Push to Azure (will trigger deployment)
git push azure main

# OR deploy using ZIP file (simpler)
Write-Host "Creating deployment package..."
cd backend
7z a -r backend-deployment.zip . -x "!.git" -x "!venv" -x "!*.pyc" -x "!__pycache__"

# Deploy ZIP
Write-Host "Deploying to Azure..."
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name $backendAppName `
  --src backend-deployment.zip
```

### Step 2: Verify Backend Deployment

```powershell
# Check deployment status
az webapp deployment show-status `
  --resource-group $resourceGroup `
  --name $backendAppName

# Test health endpoint
$backendUrl = "https://$backendAppName.azurewebsites.net"
Write-Host "Testing backend at: $backendUrl/api/health"

# Use PowerShell to test
$healthResponse = Invoke-WebRequest -Uri "$backendUrl/api/health" -UseBasicParsing
Write-Host "Backend Health: $($healthResponse.Content)"
```

---

## Phase 4: Deploy Frontend

### Step 1: Prepare Frontend for Production

**Update [frontend/.env.production](frontend/.env.production):**
```
NEXT_PUBLIC_API_URL=https://applicant-db-api-prod.azurewebsites.net
```

**Update [next.config.js](next.config.js):**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://applicant-db-api-prod.azurewebsites.net",
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
        },
      ],
    };
  },
};

module.exports = nextConfig;
```

### Step 2: Deploy Using Static Web App

```powershell
# If using GitHub Actions (Recommended)

# 4.1 Create GitHub Actions workflow file
$workflowPath = ".github/workflows/azure-static-web-apps-deploy.yml"
mkdir -Path ".github/workflows" -Force

# The Static Web App should auto-generate this, but here's the template:

# 4.2 Push to GitHub (if using Static Web App with GitHub)
git add .
git commit -m "Configure for Azure Static Web Apps deployment"
git push origin main

# 4.3 Monitor deployment in Azure Portal or:
$resourceId = "/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.Web/staticSites/$frontendAppName"
az resource invoke-action --resource-id $resourceId --action listSecrets --query properties.repositoryToken -o tsv
```

### Alternative: Deploy Using App Service (If Preferred)

```powershell
# If you prefer App Service instead of Static Web App:

# 4.1 Build Next.js
cd frontend
npm install
npm run build

# 4.2 Create deployment package
7z a -r frontend-deployment.zip .next node_modules package.json package-lock.json next.config.js public

# 4.3 Deploy
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name $frontendAppName `
  --src frontend-deployment.zip

# 4.4 Set App Service startup script
az webapp config set `
  --resource-group $resourceGroup `
  --name $frontendAppName `
  --startup-file "npm start"
```

---

## Phase 5: Testing & Verification

### Step 1: Test Backend API

```powershell
$backendUrl = "https://$backendAppName.azurewebsites.net"

# 1.1 Health Check
Write-Host "Testing Health Endpoint..."
$response = Invoke-WebRequest -Uri "$backendUrl/api/health" -UseBasicParsing
Write-Host "Status: $($response.StatusCode)"
Write-Host "Response: $($response.Content)"

# 1.2 Test Login
Write-Host "Testing Login Endpoint..."
$loginData = @{
    email = "test@example.com"
    password = "testpassword"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "$backendUrl/api/auth/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $loginData `
  -UseBasicParsing
Write-Host "Response: $($response.Content)"
```

### Step 2: Test Frontend

```powershell
# 2.1 Visit the frontend URL
$frontendUrl = "https://$frontendAppName.azurestaticapps.net"
Write-Host "Frontend URL: $frontendUrl"

# 2.2 Test key features:
# - Homepage loads
# - Login page works
# - Can access upload page
# - Can access search page
# - API calls work (check browser console for errors)
```

### Step 3: Test Database Connection

```powershell
# Test SQL Database connection
Write-Host "Testing SQL Database Connection..."

# You can test using Azure Data Studio or SQL Server Management Studio
# Connection String:
# Server: applicantdb-server.database.windows.net
# Database: applicants_db
# User: dbadmin
# Password: YourSecurePassword@123
```

### Step 4: Test Azure Storage

```powershell
# Test blob storage
Write-Host "Testing Azure Blob Storage..."

az storage blob list `
  --container-name "resumes" `
  --connection-string $storageConnectionString
```

---

## Phase 6: Monitoring & Troubleshooting

### Step 1: Enable Application Insights (Monitoring)

```powershell
# 6.1 Create Application Insights
$appInsightsName = "applicant-db-insights"

az monitor app-insights component create `
  --resource-group $resourceGroup `
  --app $appInsightsName `
  --location $location `
  --kind web `
  --application-type web

# 6.2 Get Instrumentation Key
$instrumentationKey = az monitor app-insights component show `
  --resource-group $resourceGroup `
  --app $appInsightsName `
  --query "instrumentationKey" -o tsv

Write-Host "Instrumentation Key: $instrumentationKey"

# 6.3 Link to App Service
az webapp config appsettings set `
  --resource-group $resourceGroup `
  --name $backendAppName `
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$instrumentationKey"
```

### Step 2: View Logs

```powershell
# View real-time logs
az webapp log tail `
  --resource-group $resourceGroup `
  --name $backendAppName `
  --provider "Log Analytics"

# Or stream logs
az webapp log stream `
  --resource-group $resourceGroup `
  --name $backendAppName
```

### Step 3: Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **API returns 500 error** | Check logs: `az webapp log tail` |
| **Database connection fails** | Verify firewall rules and connection string |
| **CORS errors** | Ensure FRONTEND_URL is correct in env variables |
| **Storage connection fails** | Verify AZURE_STORAGE_CONNECTION_STRING in app settings |
| **Frontend 404 errors** | Check build output and routing configuration |
| **Performance issues** | Scale up App Service plan if needed |

### Step 4: Scale Resources (If Needed)

```powershell
# Upgrade to better plan for production
az appservice plan update `
  --resource-group $resourceGroup `
  --name $appServicePlanName `
  --sku "S1"  # S1 is standard, good for production

# Enable autoscaling
az monitor autoscale create `
  --resource-group $resourceGroup `
  --resource-name-type "Microsoft.Web/serverfarms" `
  --resource-name $appServicePlanName `
  --min-count 1 `
  --max-count 3 `
  --count 1
```

---

## 🔒 Security Checklist

- [ ] Change SQL admin password to strong password
- [ ] Enable SQL Server firewall rules (restrict IPs)
- [ ] Enable SSL/TLS (HTTPS - automatic with Azure)
- [ ] Set strong SECRET_KEY for Flask
- [ ] Enable Application Insights for monitoring
- [ ] Configure backup for SQL Database
- [ ] Review and restrict storage account access
- [ ] Enable authentication in App Service (if public)
- [ ] Configure CDN for frontend (optional but recommended)
- [ ] Set up CORS properly for frontend/backend communication

---

## 📊 Final Configuration Summary

```
Frontend Application:
  URL: https://applicant-db-app-prod.azurestaticapps.net
  Type: Azure Static Web App
  Framework: Next.js 14

Backend API:
  URL: https://applicant-db-api-prod.azurewebsites.net
  Type: Azure App Service (Python 3.11)
  Framework: Flask

Database:
  Server: applicantdb-server.database.windows.net
  Database: applicants_db
  Type: Azure SQL Database (Basic)

Storage:
  Account: applicantdbstorage
  Container: resumes
  Type: Azure Blob Storage

Monitoring:
  Service: Application Insights
  Logs: Available via Azure Portal
```

---

## 🎯 Next Steps

1. **Local Testing**: Test everything locally before deploying
2. **Configure DNS**: Add custom domain if you have one
3. **Setup CI/CD**: Configure GitHub Actions for automatic deployments
4. **Backup Strategy**: Enable SQL backups and storage redundancy
5. **Cost Optimization**: Monitor Azure costs and optimize as needed

---

## 📞 Support Resources

- Azure Portal: https://portal.azure.com
- Azure Documentation: https://docs.microsoft.com/azure
- Flask Documentation: https://flask.palletsprojects.com
- Next.js Documentation: https://nextjs.org/docs

---

**Last Updated**: April 2026
**Version**: 1.0

# Backend Deployment to Azure - Complete Guide

## ✅ Current Status
- ✅ Frontend deployed to Azure Static Web Apps
- ✅ Frontend configured to use API endpoint
- ⏳ Backend needs to be deployed to Azure App Service

## 🚀 Step 1: Create Azure App Service for Backend

### Option A: Using Azure Portal (Recommended for First Time)

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **+ Create a resource**
3. Search for **App Service**
4. Click **Create**
5. Fill in the form:
   - **Resource Group**: Create or select existing
   - **Name**: `applicants-api-service`
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Same as Static Web App (e.g., East US)
   - **App Service Plan**: Create new (B1 Basic or higher)
6. Click **Review + Create** → **Create**
7. Wait for deployment (2-3 minutes)

### Option B: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name applicants-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name applicants-plan \
  --resource-group applicants-rg \
  --sku B1 \
  --is-linux

# Create App Service
az webapp create \
  --resource-group applicants-rg \
  --plan applicants-plan \
  --name applicants-api-service \
  --runtime "python|3.11"
```

---

## 🔧 Step 2: Prepare Backend for Deployment

1. Open PowerShell and navigate to the backend:
```powershell
cd "c:\Users\DELL\Documents\Personals\Saraansh solutions\applicant-database-app\backend"
```

2. Update `requirements.txt` to include production dependencies:
```bash
# Install production dependencies
pip install Flask Flask-CORS python-dotenv pyodbc SQLAlchemy Werkzeug

# Generate requirements
pip freeze > requirements.txt
```

3. Update `app.py` to add production settings:
```python
# At the top of app.py
import os
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# CORS Configuration - Allow frontend to communicate
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://applicants-web-app.azurestaticapps.net",
            "http://localhost:3000",  # Development
            "http://localhost:5000"   # Development
        ],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Rest of app configuration...
if __name__ == '__main__':
    # For local development
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=8000)
```

---

## 📝 Step 3: Create Configuration Files

### Create `.github/workflows/deploy-backend.yml`

```yaml
name: Deploy Backend to Azure App Service

on:
  push:
    branches: [main, master]
    paths:
      - 'backend/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: backend
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Deploy to Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: applicants-api-service
          publish-profile: ${{ secrets.AZURE_APP_SERVICE_PUBLISH_PROFILE }}
          package: ./backend
```

### Create `.deployment` file in backend:

```
[config]
command = pip install -r requirements.txt && python app.py
project = backend
```

### Create `backend/.env` for Azure:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0

# Database (Example - update with your actual database)
DB_CONNECTION_STRING=sqlite:///applicants.db

# Azure Storage (if using blob storage for resumes)
AZURE_STORAGE_CONNECTION_STRING=<your-storage-connection-string>
AZURE_CONTAINER_NAME=resumes

# CORS
CORS_ALLOWED_ORIGINS=https://applicants-web-app.azurestaticapps.net

# Security
SECRET_KEY=<generate-random-secret-key>
```

---

## 🔑 Step 4: Add Secrets to GitHub

1. Go to GitHub: https://github.com/KolliparaVMKMithra/saraansh-solutions
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

**Secret 1: `AZURE_APP_SERVICE_PUBLISH_PROFILE`**
   - Get this from Azure Portal:
     1. Go to your App Service
     2. Click **Get publish profile** (top right)
     3. Save the XML file
     4. Open it and copy the entire content
     5. Paste as secret value

**Secret 2: `AZURE_STATIC_WEB_APPS_TOKEN`** (Already added)
   - Used for frontend deployment (already configured)

---

## 🚀 Step 5: Deploy Backend

### Option A: Automatic Deployment (GitHub Actions)

1. Make sure `.github/workflows/deploy-backend.yml` exists
2. Commit and push to GitHub:
```bash
git add backend/.env
git add .github/workflows/deploy-backend.yml
git commit -m "chore: prepare backend for Azure deployment"
git push origin main
```
3. GitHub Actions will automatically deploy the backend

### Option B: Manual Deployment Using Azure CLI

```bash
# Navigate to backend directory
cd backend

# Create deployment package
az webapp deployment source config-zip \
  --resource-group applicants-rg \
  --name applicants-api-service \
  --src backend.zip
```

### Option C: Manual Deployment Using Git

```bash
# Initialize git in backend
cd backend

# Add Azure remote
git remote add azure https://applicants-api-service.scm.azurewebsites.net:443/applicants-api-service.git

# Deploy
git push azure main:master
```

---

## ✅ Step 6: Verify Backend Deployment

1. Go to Azure Portal → Your App Service
2. Click **Overview**
3. Note the URL: `https://applicants-api-service.azurewebsites.net`
4. Test the API in your browser:
   ```
   https://applicants-api-service.azurewebsites.net/api/health
   ```
   OR
   ```
   curl https://applicants-api-service.azurewebsites.net/api/health
   ```

---

## 🔗 Step 7: Update Frontend Environment Variables

The frontend `.env.local` should already have:
```
NEXT_PUBLIC_API_BASE_URL=https://applicants-api-service.azurewebsites.net/api
```

If not, update it and redeploy:
```bash
cd frontend
echo "NEXT_PUBLIC_API_BASE_URL=https://applicants-api-service.azurewebsites.net/api" > .env.local
npm run build
git add .
git commit -m "fix: update backend API URL"
git push origin main
```

---

## 🧪 Step 8: Test End-to-End

1. Open your frontend: `https://applicants-web-app.azurestaticapps.net`
2. Try to **Sign Up** - should work now (no network error)
3. If still getting errors, check:
   - **Browser Console** (F12 → Console) for exact error message
   - **Backend Logs** in Azure Portal → App Service → Log Stream
   - **Network Tab** (F12 → Network) to see API calls

---

## 🐛 Troubleshooting Network Errors

### If you still see "Network error":

1. **Check CORS settings** - Backend must allow frontend origin
2. **Verify backend is running** - Check Application Insights in Azure
3. **Check network requests** - Open browser DevTools (F12):
   - Go to **Network** tab
   - Try to sign up
   - Click the failed request
   - Check the error message

### Common Issues:

| Error | Solution |
|-------|----------|
| 404 Not Found | Backend API endpoint doesn't exist or wrong URL |
| 403 Forbidden | CORS issue - backend doesn't allow frontend domain |
| Connection refused | Backend is not running or URL is wrong |
| Timeout | Backend is slow or not responding |

---

## 📚 Additional Resources

- [Azure App Service Deployment](https://learn.microsoft.com/en-us/azure/app-service/app-service-web-get-started-python)
- [Flask CORS Setup](https://flask-cors.readthedocs.io/en/latest/)
- [Azure App Service Configuration](https://learn.microsoft.com/en-us/azure/app-service/configure-common)

---

## ✨ Summary

After following these steps:
- ✅ Backend deployed to Azure App Service
- ✅ Frontend configured to use backend API
- ✅ CORS properly configured
- ✅ "Network error" should be resolved
- ✅ Full application working end-to-end

Need help? Contact support or check Azure Portal logs.

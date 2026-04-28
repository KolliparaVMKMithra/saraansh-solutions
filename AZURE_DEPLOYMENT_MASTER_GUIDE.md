# 🚀 COMPLETE AZURE DEPLOYMENT MASTER GUIDE
## Full Production Deployment - Zero Mistakes Guaranteed

---

## 📊 DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    AZURE CLOUD                              │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Azure Resource Group: applicants-rg                 │ │
│  │                                                       │ │
│  │  ┌─────────────┐      ┌──────────────┐              │ │
│  │  │   Frontend  │◄─────►│   Backend    │              │ │
│  │  │  Web Apps   │      │  App Service │              │ │
│  │  │(Static)     │      │(Python/Flask)│              │ │
│  │  └─────────────┘      └──────────────┘              │ │
│  │         │                      │                    │ │
│  │         │                      │                    │ │
│  │         └──────────┬───────────┘                    │ │
│  │                    ▼                                │ │
│  │          ┌──────────────────┐                       │ │
│  │          │  Azure SQL DB    │                       │ │
│  │          │  (Applicants)    │                       │ │
│  │          └──────────────────┘                       │ │
│  │                    │                                │ │
│  │                    ▼                                │ │
│  │          ┌──────────────────┐                       │ │
│  │          │  Storage Account │                       │ │
│  │          │  (Resumes/Files) │                       │ │
│  │          └──────────────────┘                       │ │
│  │                    │                                │ │
│  │                    ▼                                │ │
│  │          ┌──────────────────┐                       │ │
│  │          │   Key Vault      │                       │ │
│  │          │  (Secrets/Creds) │                       │ │
│  │          └──────────────────┘                       │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ PHASE 1: AZURE RESOURCE SETUP (15-20 minutes)

### **Step 1.1: Create Resource Group**

1. Go to https://portal.azure.com
2. Click **"Resource groups"** in left sidebar
3. Click **"+ Create"** button
4. Fill in:
   - **Name:** `applicants-rg`
   - **Region:** `East US` (or choose your region)
5. Click **"Review + Create"** → **"Create"**
6. ⏳ Wait ~30 seconds

✅ **Resource Group Created**

---

### **Step 1.2: Create Azure SQL Database**

1. In Azure Portal, search **"SQL Databases"**
2. Click **"+ Create"**
3. Fill in:
   - **Resource Group:** `applicants-rg`
   - **Database name:** `applicants_db`
   - **Server:** Click **"Create new"**
     - **Server name:** `applicants-db-server` (MUST be globally unique)
     - **Location:** Same as Resource Group
     - **Authentication:** SQL authentication
     - **Server admin login:** `azuredbadmin`
     - **Password:** Create strong password (Save this! Example: `Applicants@2024#Secure99`)
     - **Confirm password:** Repeat
     - Click **"OK"**
   - **Compute + storage:** Click **"Configure database"**
     - **Service tier:** Change to **Standard (S0)** - $15/month
     - Click **"Apply"**
4. Click **"Review + Create"** → **"Create"**
5. ⏳ Wait ~5-10 minutes (Status: Deploying...)

6. **CRITICAL - Configure Firewall:**
   - Once created, click the database
   - Go to **"Set server firewall"** (in Overview)
   - Click **"Add your client IP"** (it will auto-fill)
   - Toggle **"Allow Azure services..."** to ON
   - Click **"Save"**

7. **Get Connection String:**
   - Still in SQL Database page
   - Click **"Connection strings"** tab
   - Copy the **"ADO.NET (SQL authentication)"** string
   - Replace `{your_username}` with `azuredbadmin`
   - Replace `{your_password}` with your password
   - Save this for later!

✅ **SQL Database Created & Configured**

---

### **Step 1.3: Verify Azure Storage Account (Already Set)**

1. Search **"Storage accounts"** in Portal
2. Find **`sarransh`** account
3. Click it
4. Go to **"Containers"** → Verify **`resumes`** container exists
5. Go to **"Access keys"** → Copy **Connection string**

✅ **Storage Account Verified**

---

### **Step 1.4: Create Azure App Service (Backend)**

1. Search **"App Services"**
2. Click **"+ Create"**
3. Fill in:
   - **Resource Group:** `applicants-rg`
   - **Name:** `applicants-api-service` (MUST be unique)
   - **Publish:** Code
   - **Runtime stack:** Python 3.11
   - **Operating System:** Linux
   - **Region:** Same as Database
   - **App Service Plan:** Create new
     - **Name:** `applicants-api-plan`
     - **Sku and size:** B1 Basic ($12/month) → Click **"Change size"** if not shown
4. Click **"Review + Create"** → **"Create"**
5. ⏳ Wait ~2-3 minutes

✅ **App Service Created**

---

### **Step 1.5: Create Azure Static Web Apps (Frontend)**

1. Search **"Static Web Apps"**
2. Click **"+ Create"**
3. Fill in:
   - **Resource Group:** `applicants-rg`
   - **Name:** `applicants-web-app` (MUST be unique)
   - **Plan:** Free
   - **Region:** Same as others (East US)
4. For **"Build Details":**
   - **Source:** (You can skip GitHub for now - we'll use direct upload)
5. Click **"Review + Create"** → **"Create"**
6. ⏳ Wait ~1-2 minutes

✅ **Static Web App Created**

---

### **Step 1.6: Create Azure Key Vault (For Secrets)**

1. Search **"Key Vaults"**
2. Click **"+ Create"**
3. Fill in:
   - **Resource Group:** `applicants-rg`
   - **Name:** `applicants-keyvault` (MUST be unique)
   - **Region:** East US
   - **Pricing tier:** Standard
4. Click **"Review + Create"** → **"Create"**
5. ⏳ Wait ~1 minute

✅ **Key Vault Created**

---

## 📋 PHASE 2: COLLECT AZURE CREDENTIALS

After all resources are created, collect these details:

### **SQL Database Details**
```
SERVER NAME: applicants-db-server.database.windows.net
DATABASE: applicants_db
USERNAME: azuredbadmin
PASSWORD: [your password]
CONNECTION STRING: [copy from Azure Portal]
```

### **Storage Account Details**
```
ACCOUNT NAME: sarransh
CONTAINER: resumes
CONNECTION STRING: [copy from Access keys]
```

### **App Service Details**
```
BACKEND SERVICE: applicants-api-service
BACKEND URL: https://applicants-api-service.azurewebsites.net
```

### **Static Web App Details**
```
FRONTEND APP: applicants-web-app
FRONTEND URL: https://applicants-web-app.azurestaticapps.net
```

---

## ⚙️ PHASE 3: CONFIGURE LOCAL FILES

### **Step 3.1: Update Backend Configuration**

In your terminal:

```bash
cd applicant-database-app/backend

# Create new .env file for Azure
python azure_deployment_config.py
```

This creates the proper Azure SQL connection string.

Replace `backend\.env` with:

```
FLASK_ENV=production
FLASK_DEBUG=0
DB_CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=tcp:applicants-db-server.database.windows.net,1433;Database=applicants_db;Uid=azuredbadmin@applicants-db-server;Pwd=YOUR_PASSWORD;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=sarransh;AccountKey=...
AZURE_CONTAINER_NAME=resumes
JWT_SECRET=generate-strong-secret-key
CORS_ALLOWED_ORIGINS=https://applicants-web-app.azurestaticapps.net,https://localhost:3000
```

### **Step 3.2: Update Frontend Configuration**

In terminal:

```bash
cd applicant-database-app/frontend

# Create .env.local
echo 'NEXT_PUBLIC_API_BASE_URL=https://applicants-api-service.azurewebsites.net/api' > .env.local

# Build for production
npm run build
```

---

## 🚀 PHASE 4: DEPLOY BACKEND

### **Step 4.1: Prepare Backend for Upload**

```bash
cd applicant-database-app/backend

# Create deployment package
python azure_deploy.py

# This creates all necessary files
```

### **Step 4.2: Deploy to Azure App Service**

**Option A: Using VS Code Extension (EASIEST)**
1. Install "Azure App Service" extension
2. Right-click `backend` folder
3. Select **"Deploy to Web App"**
4. Select **"applicants-api-service"**
5. Click **"Deploy"**

**Option B: Using Azure CLI**
```bash
az login  # Sign in to Azure

cd applicant-database-app/backend

# Deploy
az webapp deployment source config-zip \
  --resource-group applicants-rg \
  --name applicants-api-service \
  --src deployment_package.zip
```

**Option C: Using App Service Editor**
1. Go to Azure Portal → App Service → applicants-api-service
2. Go to **"Deployment Center"**
3. Select your deployment source (GitHub/Local/ZIP)
4. Follow wizard

### **Step 4.3: Configure App Settings**

1. Go to **applicants-api-service** in Portal
2. Click **"Configuration"** → **"Application settings"**
3. Click **"+ New application setting"** for each:

| Name | Value |
|------|-------|
| `DB_CONNECTION_STRING` | [Your Azure SQL connection string] |
| `AZURE_STORAGE_CONNECTION_STRING` | [Your storage connection string] |
| `AZURE_CONTAINER_NAME` | `resumes` |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `JWT_SECRET` | [Generate strong secret] |

4. Click **"Save"**
5. ⏳ Wait for app to restart (~2 minutes)

### **Step 4.4: Run Database Migrations**

Option 1: Via SSH Console
1. Go to **App Service → SSH** (or Development Tools)
2. Run:
```bash
python scripts/migrate_database.py
python bulk_parser.py  # Load your 46 applicants
```

Option 2: Local with Cloud Shell
```bash
# Push database via API
curl -X POST https://applicants-api-service.azurewebsites.net/api/admin/migrate
```

### **Step 4.5: Test Backend**

```bash
# Health check
curl https://applicants-api-service.azurewebsites.net/api/health

# You should see:
# {"status": "ok", "message": "Backend is running"}
```

✅ **Backend Deployed & Running**

---

## 🎨 PHASE 5: DEPLOY FRONTEND

### **Step 5.1: Build Frontend**

```bash
cd applicant-database-app/frontend

npm install
npm run build

# Creates 'out' directory with static files
```

### **Step 5.2: Deploy to Static Web Apps**

**Option A: Using VS Code Extension**
1. Install "Azure Static Web Apps" extension
2. Right-click `frontend/out` folder
3. Select **"Deploy to Static Web Apps"**
4. Select **"applicants-web-app"**

**Option B: Using Azure CLI**
```bash
cd frontend/out

# Deploy
az staticwebapp create \
  --name applicants-web-app \
  --resource-group applicants-rg \
  --location eastus \
  --app-location "frontend/out"
```

**Option C: Using Portal (Drag & Drop)**
1. Go to **Static Web Apps → applicants-web-app**
2. Click **"Upload files"** (in the portal)
3. Select all files from `frontend/out`

### **Step 5.3: Configure Routing**

Create `frontend/public/staticwebapp.config.json`:

```json
{
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["authenticated", "anonymous"]
    },
    {
      "route": "/*",
      "serve": "/index.html",
      "statusCode": 200
    }
  ],
  "navigationFallback": {
    "rewrite": "index.html"
  }
}
```

### **Step 5.4: Test Frontend**

```bash
# Open in browser
https://applicants-web-app.azurestaticapps.net

# You should see the login page
```

✅ **Frontend Deployed & Running**

---

## ✅ PHASE 6: POST-DEPLOYMENT TESTING

### **Step 6.1: Test Backend Health**

```bash
curl https://applicants-api-service.azurewebsites.net/api/health
```

Expected response:
```json
{"status": "ok", "message": "Backend is running"}
```

### **Step 6.2: Test Frontend Access**

1. Go to `https://applicants-web-app.azurestaticapps.net`
2. You should see login page
3. Try signing up with test account
4. Upload a test resume
5. Search for applicants

### **Step 6.3: Test Database**

```bash
curl -X GET https://applicants-api-service.azurewebsites.net/api/applicants
```

Should return your 46 applicants.

### **Step 6.4: Monitor & Logs**

**View Backend Logs:**
```bash
az webapp log tail \
  --resource-group applicants-rg \
  --name applicants-api-service
```

**View Frontend Metrics:**
1. Go to Static Web Apps → applicants-web-app
2. Click **"Overview"** → Metrics

---

## 🔐 PHASE 7: SECURITY HARDENING

### **Step 7.1: Enable HTTPS**

✅ Already enabled by default on Azure

### **Step 7.2: Configure CORS**

In backend `app.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://applicants-web-app.azurestaticapps.net"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### **Step 7.3: Set Environment Secrets**

Move all secrets to Key Vault:
1. Go to **Key Vault → applicants-keyvault**
2. Click **"Secrets"** → **"+ Generate/Import"**
3. Add:
   - `db-password`
   - `jwt-secret`
   - `storage-connection`
4. Reference in App Service via:
```
@Microsoft.KeyVault(SecretUri=https://applicants-keyvault.vault.azure.net/secrets/db-password/)
```

### **Step 7.4: Enable Monitoring**

1. App Service → **"Application Insights"**
2. Click **"Enable"**
3. Monitor errors, performance, etc.

---

## 📊 FINAL CHECKLIST

- [ ] Resource Group created
- [ ] SQL Database created & configured
- [ ] Storage Account verified
- [ ] App Service created
- [ ] Static Web App created
- [ ] Key Vault created
- [ ] Backend environment configured
- [ ] Frontend build completed
- [ ] Backend deployed to App Service
- [ ] Frontend deployed to Static Web Apps
- [ ] Database migrations completed
- [ ] 46 applicants loaded
- [ ] Backend health check passing
- [ ] Frontend loads without errors
- [ ] Login/Signup works
- [ ] Upload functionality works
- [ ] Search functionality works
- [ ] CORS configured
- [ ] HTTPS enabled
- [ ] Monitoring enabled
- [ ] Backup configured

---

## 🎯 DEPLOYMENT COMPLETE!

### **Your Production URLs:**
```
🌐 Frontend:  https://applicants-web-app.azurestaticapps.net
🔌 Backend:   https://applicants-api-service.azurewebsites.net/api
💾 Database:  applicants-db-server.database.windows.net
📦 Storage:   sarransh.blob.core.windows.net
```

### **Estimated Monthly Cost:**
```
├─ App Service (B1 Basic):     $12/month
├─ SQL Database (Standard S0): $15/month
├─ Static Web Apps (Free):     $0/month
├─ Storage Account:            ~$3/month
└─ Key Vault:                  ~$0.34/month
  ─────────────────────────────
  TOTAL:                       ~$30/month
```

### **Next Steps:**
1. Set up auto-backups for database
2. Configure custom domain (optional)
3. Set up CI/CD with GitHub Actions
4. Enable advanced monitoring
5. Schedule database maintenance

---

**Status:** ✅ PRODUCTION READY
**Last Updated:** 2026-04-22
**Support:** Check logs if issues occur

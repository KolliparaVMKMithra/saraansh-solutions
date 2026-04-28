# Azure Blob Storage Setup Guide

## Overview
This guide helps you set up Azure Blob Storage for storing resume files in your applicant database app.

## Option 1: Local Development with Azurite (Recommended for Development)

### Install Azurite
```bash
npm install -g azurite
```

### Start Azurite
```bash
azurite --silent --location c:\azurite --debug c:\azurite\debug.log
```

### Set Environment Variables
Create a `.env` file in the backend directory:
```
AZURE_STORAGE_CONNECTION_STRING=UseDevelopmentStorage=true
AZURE_CONTAINER_NAME=resumes
```

## Option 2: Azure Production Storage

### Create Azure Storage Account
1. Go to Azure Portal
2. Create a Storage Account
3. Get the connection string from "Access keys"

### Set Environment Variables
```
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=resumes
```

## Testing Setup

Run the test script:
```bash
python test_azure.py
```

## App Behavior

- **With Azure configured**: Resume files are uploaded to Azure Blob Storage
- **Without Azure**: Files are stored locally in the `uploads/` directory
- **Download functionality**: Works in both cases

## Troubleshooting

1. **Connection issues**: Check your connection string
2. **Container not found**: The app creates containers automatically
3. **Permissions**: Ensure your storage account has blob write permissions

## Security Notes

- Never commit connection strings to version control
- Use Azure Key Vault for production secrets
- Consider using Managed Identity for Azure-hosted apps
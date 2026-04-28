"""
Azure Blob Storage Setup Guide
===============================

This script helps you set up Azure Blob Storage for storing resume files.

For Local Development (Azurite):
1. Install Azurite: npm install -g azurite
2. Start Azurite: azurite --silent --location c:\azurite --debug c:\azurite\debug.log
3. Set environment variable: AZURE_STORAGE_CONNECTION_STRING=UseDevelopmentStorage=true

For Azure Production:
1. Create Azure Storage Account
2. Get connection string from Azure Portal
3. Set environment variables:
   - AZURE_STORAGE_CONNECTION_STRING=your_connection_string
   - AZURE_CONTAINER_NAME=resumes

Environment Variables:
- AZURE_STORAGE_CONNECTION_STRING: Your Azure Storage connection string
- AZURE_CONTAINER_NAME: Container name for resumes (default: 'resumes')

If Azure is not configured, the app will work with local file storage only.
"""

import os

def check_azure_config():
    """Check if Azure Blob Storage is properly configured"""
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_CONTAINER_NAME', 'resumes')

    if connection_string:
        print("✅ Azure Blob Storage configured")
        print(f"   Connection: {'Azure Production' if not connection_string.startswith('UseDevelopmentStorage') else 'Azurite (Local)'}")
        print(f"   Container: {container_name}")
        return True
    else:
        print("⚠️  Azure Blob Storage not configured")
        print("   Using local file storage only")
        print("   To enable Azure storage, set AZURE_STORAGE_CONNECTION_STRING environment variable")
        return False

if __name__ == "__main__":
    print("Azure Blob Storage Configuration Check")
    print("=" * 50)
    check_azure_config()
    print("\nFor setup instructions, see the comments in this file.")
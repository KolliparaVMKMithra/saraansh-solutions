"""
Azure Deployment Configuration Generator
This script prepares all necessary configurations for Azure deployment
Run this AFTER you have Azure resources created
"""

import os
import json
from pathlib import Path


def generate_backend_env_azure(
    sql_server: str,
    sql_database: str,
    sql_username: str,
    sql_password: str,
    storage_connection: str,
    container_name: str,
    jwt_secret: str = None,
    environment: str = "production"
) -> str:
    """
    Generate .env file for Azure deployment
    
    Args:
        sql_server: Azure SQL Server name (e.g., server.database.windows.net)
        sql_database: Azure SQL Database name
        sql_username: Azure SQL admin username
        sql_password: Azure SQL admin password
        storage_connection: Azure Storage connection string
        container_name: Blob container name
        jwt_secret: JWT secret (auto-generated if not provided)
        environment: Environment type (development/production)
    
    Returns:
        Complete .env file content
    """
    
    if jwt_secret is None:
        jwt_secret = "your-jwt-secret-change-in-production-" + os.urandom(16).hex()
    
    # Build Azure SQL connection string
    azure_sql_connection = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server=tcp:{sql_server},1433;"
        f"Database={sql_database};"
        f"Uid={sql_username}@{sql_server.split('.')[0]};"
        f"Pwd={sql_password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    
    env_content = f"""# Azure Deployment Environment Variables
# Generated: {json.dumps({'timestamp': str(os.urandom(1))})}
# Environment: {environment}

# Flask Configuration
FLASK_ENV={environment}
FLASK_DEBUG=0
FLASK_APP=app.py

# Azure SQL Database Connection
DB_CONNECTION_STRING={azure_sql_connection}

# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING={storage_connection}
AZURE_CONTAINER_NAME={container_name}

# Authentication
JWT_SECRET={jwt_secret}
JWT_ALGORITHM=HS256
TOKEN_EXPIRY_HOURS=24

# CORS Configuration (Update with your frontend domain)
CORS_ALLOWED_ORIGINS=https://applicants-web-app.azurestaticapps.net,https://localhost:3000

# Application Configuration
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,doc
MAX_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FILE=/tmp/applicants-api.log

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
"""
    
    return env_content


def generate_frontend_env_azure(
    api_base_url: str = "https://applicants-api-service.azurewebsites.net/api"
) -> str:
    """
    Generate .env.local for Next.js frontend in Azure
    
    Args:
        api_base_url: Base URL for backend API
    
    Returns:
        Complete .env.local content
    """
    
    env_content = f"""# Frontend Environment Variables
# Azure Production Deployment

# API Configuration
NEXT_PUBLIC_API_BASE_URL={api_base_url}

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_LOGGING=true

# Application
NEXT_PUBLIC_APP_NAME=Applicant Database System
NEXT_PUBLIC_APP_VERSION=1.0.0
"""
    
    return env_content


def generate_azure_sql_schema() -> str:
    """
    Generate SQL schema for Azure SQL Database
    Must be executed AFTER deploying backend
    """
    
    schema = """
-- Azure SQL Database Schema for Applicants System
-- This script creates all necessary tables and indexes

-- Drop existing tables (if re-deploying)
-- DROP TABLE IF EXISTS Users;
-- DROP TABLE IF EXISTS Applicants;
-- DROP TABLE IF EXISTS SearchHistory;

-- Users Table (for authentication)
CREATE TABLE IF NOT EXISTS Users (
    PartitionKey NVARCHAR(50),
    RowKey NVARCHAR(255) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL UNIQUE,
    fullName NVARCHAR(255),
    passwordHash NVARCHAR(500),
    createdAt DATETIME DEFAULT GETUTCDATE(),
    lastLogin DATETIME,
    isActive BIT DEFAULT 1,
    CONSTRAINT UQ_Email UNIQUE(email)
);

-- Create index on Users
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_active ON Users(isActive);

-- Applicants Table (main data)
CREATE TABLE IF NOT EXISTS Applicants (
    applicationId NVARCHAR(36) PRIMARY KEY,
    applicantName NVARCHAR(255) NOT NULL,
    emailAddress NVARCHAR(255),
    mobileNumber NVARCHAR(20),
    city NVARCHAR(100),
    state NVARCHAR(50),
    applicantStatus NVARCHAR(50) DEFAULT 'Active',
    jobTitle NVARCHAR(255),
    ownership NVARCHAR(100),
    workAuthorization NVARCHAR(100),
    source NVARCHAR(100) DEFAULT 'Resume Upload',
    createdBy NVARCHAR(255) DEFAULT 'System',
    createdOn DATETIME DEFAULT GETUTCDATE(),
    modifiedOn DATETIME,
    techSkills NVARCHAR(MAX),
    resumeText NVARCHAR(MAX),
    blobUrl NVARCHAR(500),
    CONSTRAINT PK_Applicants PRIMARY KEY(applicationId)
);

-- Create indexes on Applicants for search performance
CREATE INDEX idx_applicants_name ON Applicants(applicantName);
CREATE INDEX idx_applicants_email ON Applicants(emailAddress);
CREATE INDEX idx_applicants_city ON Applicants(city);
CREATE INDEX idx_applicants_state ON Applicants(state);
CREATE INDEX idx_applicants_jobtitle ON Applicants(jobTitle);
CREATE INDEX idx_applicants_status ON Applicants(applicantStatus);
CREATE INDEX idx_applicants_workauth ON Applicants(workAuthorization);
CREATE INDEX idx_applicants_created ON Applicants(createdOn DESC);

-- Search History Table (optional, for analytics)
CREATE TABLE IF NOT EXISTS SearchHistory (
    searchId NVARCHAR(36) PRIMARY KEY,
    userId NVARCHAR(255),
    keywords NVARCHAR(MAX),
    filters NVARCHAR(MAX),
    resultCount INT,
    executedAt DATETIME DEFAULT GETUTCDATE(),
    FOREIGN KEY(userId) REFERENCES Users(RowKey)
);

-- Create index on SearchHistory
CREATE INDEX idx_search_user ON SearchHistory(userId);
CREATE INDEX idx_search_executed ON SearchHistory(executedAt DESC);

-- Grant necessary permissions (update with your app service identity)
-- This ensures the App Service can read/write data
-- GRANT SELECT, INSERT, UPDATE, DELETE ON Applicants TO [applicants-api-service];
-- GRANT SELECT, INSERT, UPDATE ON Users TO [applicants-api-service];
-- GRANT SELECT, INSERT ON SearchHistory TO [applicants-api-service];
"""
    
    return schema


def print_deployment_summary(azure_info: dict) -> None:
    """Print deployment summary"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          AZURE DEPLOYMENT CONFIGURATION GENERATED              ║
    ╚════════════════════════════════════════════════════════════════╝
    
    ✅ Backend .env generated
    ✅ Frontend .env.local generated  
    ✅ SQL schema ready
    
    📋 NEXT STEPS:
    
    1. Update backend/.env with the content above
    2. Update frontend/.env.local with the content above
    3. Run backend database migration:
       python -m scripts.migrate_database
    4. Deploy backend to Azure App Service
    5. Deploy frontend to Azure Static Web Apps
    6. Run post-deployment tests
    
    🔗 DEPLOYMENT URLS:
    ├─ Backend: https://applicants-api-service.azurewebsites.net
    ├─ Frontend: https://applicants-web-app.azurestaticapps.net
    └─ Database: applicants-db-server.database.windows.net
    
    """)


if __name__ == "__main__":
    print("Azure Deployment Configuration Generator")
    print("=" * 60)
    print("\nThis script generates Azure deployment configurations.")
    print("Use the functions to generate .env files.")

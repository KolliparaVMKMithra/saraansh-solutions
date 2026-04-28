# Applicant Database Application Configuration

## Environment Variables
# Create a .env file in the backend directory with:

# Database Configuration (choose one)
# For Azure SQL Database:
# DB_CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=SERVER_NAME.database.windows.net;Database=database_name;UID=user@server;PWD=password;

# For SQLite (default, no need to set):
# DB_CONNECTION_STRING=sqlite:////path/to/applicants.db

# Azure Blob Storage Configuration
# For Azure Production:
# AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
# AZURE_CONTAINER_NAME=resumes

# For Local Development (Azurite):
# AZURE_STORAGE_CONNECTION_STRING=UseDevelopmentStorage=true
# AZURE_CONTAINER_NAME=resumes

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- Git

### Backend Setup

1. Navigate to backend directory:
   cd backend

2. Create virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set up Azure Blob Storage (optional):
   python azure_setup.py

5. Create Azure SQL Database connection string in .env (if using Azure)

5. Run database initialization and bulk parse resumes:
   python bulk_parser.py

6. Start the backend server:
   python app.py
   
   Backend will be running at: http://localhost:5000

### Frontend Setup

1. Navigate to frontend directory:
   cd frontend

2. Install dependencies:
   npm install

3. Run development server:
   npm run dev

4. Frontend will be available at: http://localhost:3000

### Complete Application Setup (Windows)

# Terminal 1: Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python bulk_parser.py
python app.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

## Azure Blob Storage Setup

The application supports storing resume files in Azure Blob Storage for secure access and sharing.

### Local Development (Azurite)
1. Install Azurite globally:
   ```bash
   npm install -g azurite
   ```

2. Create a directory for Azurite data:
   ```bash
   mkdir c:\azurite
   ```

3. Start Azurite:
   ```bash
   azurite --silent --location c:\azurite --debug c:\azurite\debug.log
   ```

4. Set environment variable:
   ```bash
   set AZURE_STORAGE_CONNECTION_STRING=UseDevelopmentStorage=true
   ```

### Azure Production Setup
1. Create Azure Storage Account in Azure Portal
2. Get the connection string from Storage Account > Access Keys
3. Set environment variables:
   ```bash
   set AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
   set AZURE_CONTAINER_NAME=resumes
   ```

### Features
- **Automatic Upload**: Resume files are uploaded to Azure Blob Storage during upload
- **Secure Access**: Files are stored securely with unique names
- **Download Links**: Users can view/download original resume files
- **Fallback**: If Azure is not configured, files are stored locally only

## Azure Deployment

### 1. Create Azure SQL Database
```
- Resource Group: applicants-db-rg
- Server: applicants-db-server
- Database: applicants_db
- Authentication: SQL Authentication
```

### 2. Deploy Backend to Azure App Service
```
# Using Azure CLI
az login
az webapp create --resource-group applicants-db-rg --plan applicants-plan --name applicants-api --runtime "PYTHON|3.11"
az webapp deployment source config-zip --resource-group applicants-db-rg --name applicants-api --src backend.zip
```

### 3. Deploy Frontend to Azure Static Web Apps
```
cd frontend
npm run build
# Deploy the 'out' directory to Azure Static Web Apps
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload and parse resumes (multipart/form-data)
- `POST /api/search` - Search applicants
- `GET /api/applicants` - Get all applicants
- `GET /api/applicants/<id>` - Get specific applicant
- `PUT /api/applicants/<id>` - Update applicant
- `DELETE /api/applicants/<id>` - Delete applicant

## Database Schema

Applicants table columns:
- applicationId (TEXT, PRIMARY KEY)
- applicantName (TEXT)
- emailAddress (TEXT)
- mobileNumber (TEXT)
- city (TEXT)
- state (TEXT)
- applicantStatus (TEXT)
- jobTitle (TEXT)
- ownership (TEXT)
- workAuthorization (TEXT)
- source (TEXT)
- createdBy (TEXT)
- createdOn (TIMESTAMP)
- modifiedOn (TIMESTAMP)

## Features

1. **Resume Upload & Parsing**
   - Support for DOCX, DOC, PDF formats
   - Automatic data extraction
   - Bulk upload capability

2. **Applicant Search**
   - Keyword search
   - Filter by job title, city, state
   - Pagination support

3. **Database**
   - Azure SQL Database support
   - SQLite for local development
   - Flexible schema matching provided columns

4. **UI**
   - Clean, modern interface
   - Responsive design
   - Drag-and-drop file upload

## Testing

To test locally with sample resumes:

1. Place resume files in `Sample Resumes/` directory
2. Run bulk parser:
   ```
   python backend/bulk_parser.py "path/to/Sample Resumes"
   ```
3. Start both servers
4. Test upload: http://localhost:3000/upload
5. Test search: http://localhost:3000/search

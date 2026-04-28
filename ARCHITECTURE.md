# Authentication System Architecture

## User Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER SIGNUP FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

User enters email, password, full name
    ↓
Frontend validates input (email format, password length, confirmation)
    ↓
POST /api/auth/signup with {email, password, fullName}
    ↓
Backend validates input
    ↓
Check if user already exists in Azure Table Storage
    ↓
If exists: Return error "User already exists"
    ↓
If new: Hash password with bcrypt, store in Azure Table Storage
    ↓
Return success message and redirect to login
    ↓
User logs in with new credentials


┌─────────────────────────────────────────────────────────────────────┐
│                        USER LOGIN FLOW                               │
└─────────────────────────────────────────────────────────────────────┘

User enters email and password
    ↓
Frontend validates input
    ↓
POST /api/auth/login with {email, password}
    ↓
Backend queries Azure Table Storage for user
    ↓
If not found: Return error "Invalid email or password"
    ↓
If found: Verify password with bcrypt
    ↓
If password invalid: Return error "Invalid email or password"
    ↓
If password valid: Generate JWT token with:
    - email
    - fullName
    - exp (24 hours from now)
    - iat (current time)
    ↓
Return JWT token and user info
    ↓
Frontend stores token in localStorage
    ↓
Frontend stores user info in React context
    ↓
Redirect to home page
    ↓
User is now authenticated


┌─────────────────────────────────────────────────────────────────────┐
│                  PROTECTED ENDPOINT ACCESS FLOW                      │
└─────────────────────────────────────────────────────────────────────┘

User clicks on protected page (Upload, Search, Resumes)
    ↓
ProtectedRoute component checks if authenticated
    ↓
If no token: Show loading, redirect to login
    ↓
If token exists: Render page
    ↓
Component uses useAuth hook to get token
    ↓
Component includes token in Authorization header:
    Authorization: Bearer <jwt_token>
    ↓
Sends request to backend endpoint
    ↓
Backend @token_required decorator intercepts request
    ↓
Extracts token from Authorization header
    ↓
Validates token with JWT (checks signature, expiration)
    ↓
If invalid/expired: Return 401 Unauthorized
    ↓
If valid: Decode token and extract user data
    ↓
Store user data in request.user
    ↓
Pass request to route handler
    ↓
Route handler can access request.user.email and request.user.fullName
    ↓
Execute the requested operation (upload, search, etc.)
    ↓
Return response to frontend


┌─────────────────────────────────────────────────────────────────────┐
│                    RESUME UPLOAD WITH CREATEDBY FLOW                │
└─────────────────────────────────────────────────────────────────────┘

User selects resumes to upload
    ↓
Frontend gets token from context
    ↓
POST /api/upload with files and Authorization header
    ↓
Backend verifies token -> request.user available
    ↓
Extract createdBy = request.user.get('fullName')
    ↓
For each resume file:
    1. Parse resume to extract applicant data
    2. Add createdBy to applicant_data
    3. Upload resume file to Azure Blob Storage
    4. Insert applicant record into database with createdBy
    ↓
Return success with list of inserted applicants
    ↓
Frontend displays success message
    ↓
User can see applicants in Resumes section with "createdBy" field


┌─────────────────────────────────────────────────────────────────────┐
│                        LOGOUT FLOW                                   │
└─────────────────────────────────────────────────────────────────────┘

User clicks Logout button
    ↓
logout() function called from Auth context
    ↓
Clear localStorage['authToken']
    ↓
Clear user state in React context
    ↓
Redirect to login page
    ↓
Next access to protected routes will redirect to login again
```

## Data Storage Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         AZURE TABLE STORAGE                           │
│                     (User Credentials - Users table)                  │
├──────────────────────────────────────────────────────────────────────┤
│  PartitionKey: "USER"                                                │
│  RowKey: user_email (e.g., "john@example.com")                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ email: "john@example.com"                                       │ │
│  │ fullName: "John Doe"                                            │ │
│  │ passwordHash: "$2b$12$..." (bcrypt hashed)                      │ │
│  │ createdAt: "2026-04-22T10:30:00.000000"                        │ │
│  │ isActive: true                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    AZURE SQL / SQLITE DATABASE                        │
│              (Applicant Data - Applicants table)                      │
├──────────────────────────────────────────────────────────────────────┤
│  applicationId | applicantName | emailAddress | mobileNumber         │
│  city          | state         | jobTitle     | workAuthorization   │
│  applicantStatus | ownership   | source       | createdBy ← NEW!    │
│  createdOn     | modifiedOn    | techSkills   | resumeText          │
│  blobUrl       |                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ createdBy is populated from JWT token during upload             │ │
│  │ Contains: User's full name (or email if not available)          │ │
│  │ Used for: Tracking which user uploaded the resume               │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    AZURE BLOB STORAGE                                 │
│              (Resume Files - resumes container)                       │
├──────────────────────────────────────────────────────────────────────┤
│  Container: "resumes"                                                │
│  Blobs: UUID-based filenames (e.g., "abc123-def456.pdf")            │
│  Access: Via blobUrl stored in Applicants table                      │
│  Uploaded by: User through authenticated /api/upload endpoint        │
└──────────────────────────────────────────────────────────────────────┘
```

## JWT Token Structure

```
JWT Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJmdWxsTmFtZSI6IkpvaG4gRG9lIiwiZXhwIjoxNjEzMDAwMDAwLCJpYXQiOjE2MTI5MTM2MDB9.signature...

Decoded Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Decoded Payload:
{
  "email": "john@example.com",
  "fullName": "John Doe",
  "exp": 1613000000,           ← Expires in 24 hours
  "iat": 1612913600            ← Created now
}

Signature: HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), JWT_SECRET)
```

## Component Hierarchy

```
_app.tsx
  └── AuthProvider (provides useAuth context)
       ├── Layout
       │    ├── Navigation (user info, logout)
       │    └── Main Content
       │         ├── Public Pages (login, signup, home)
       │         │    └── No ProtectedRoute wrapper
       │         │
       │         └── Protected Pages
       │              └── ProtectedRoute
       │                   ├── upload.tsx
       │                   ├── search.tsx
       │                   └── resumes.tsx
       │
       └── Global State
            ├── user (email, fullName)
            ├── token (JWT)
            ├── isAuthenticated (boolean)
            └── isLoading (during auth check)
```

## API Request/Response Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   AUTHENTICATED API REQUEST                          │
└─────────────────────────────────────────────────────────────────────┘

Frontend Component:
  const { token } = useAuth()
  axios.get('/api/endpoint', {
    headers: { 'Authorization': `Bearer ${token}` }
  })

HTTP Request:
  GET /api/endpoint HTTP/1.1
  Host: localhost:5000
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Backend Route Handler:
  @app.route('/api/endpoint')
  @token_required
  def my_endpoint():
    # request.user is automatically set by decorator
    user_email = request.user['email']
    user_name = request.user['fullName']
    # ... do something ...
    return jsonify({'success': True, 'data': ...})

HTTP Response:
  200 OK
  Content-Type: application/json
  
  {
    "success": true,
    "data": {...}
  }

Frontend Component:
  Processes response and updates UI
```

## Security Layers

```
Layer 1: Frontend
  ├── ProtectedRoute checks isAuthenticated
  └── Prevents rendering if token missing

Layer 2: HTTP Transport
  ├── Token sent in Authorization header
  └── Not exposed in URL or request body

Layer 3: Backend Route
  ├── @token_required decorator intercepts request
  └── Returns 401 if token missing or invalid

Layer 4: Token Validation
  ├── Verifies JWT signature with secret
  ├── Checks token expiration
  └── Decodes payload safely

Layer 5: User Data
  ├── Passwords hashed with bcrypt (12 rounds)
  └── Stored securely in Azure Table Storage

Layer 6: Authorization
  ├── User can only access their own data (future)
  └── Admin endpoints can be added (future)
```

## Error Handling Flow

```
Invalid Credentials
    └─→ Backend returns 401 Unauthorized
         └─→ Frontend catches error
              └─→ Display "Invalid email or password"
                   └─→ User can try again

Token Expired
    └─→ Backend returns 401 Token Expired
         └─→ Frontend decorator catches error
              └─→ Clear localStorage
                   └─→ Redirect to login
                        └─→ User must log in again

Network Error
    └─→ Frontend catch block
         └─→ Display "Network error"
              └─→ Retry button

Server Error
    └─→ Backend returns 500
         └─→ Frontend displays error message
              └─→ User can contact support
```

## Deployment Architecture (Future)

```
Production Environment:

┌─────────────────────┐
│   AWS S3 / Vercel   │
│   (Frontend)        │
│   - Next.js build   │
│   - Static assets   │
└──────────┬──────────┘
           │ HTTPS
           ↓
┌─────────────────────────────────────┐
│     Azure Web App / EC2             │
│     (Backend Flask API)             │
│     - Auth endpoints                │
│     - Applicant endpoints           │
│     - Protected with JWT            │
└──────────┬──────────────────────────┘
           │
           ├─→ Azure Table Storage (User credentials)
           ├─→ Azure SQL Database (Applicant data)
           └─→ Azure Blob Storage (Resume files)
```

This architecture ensures:
- Secure authentication with no direct password storage on backend
- Scalable Azure cloud storage
- Separation of concerns (users vs. applicants vs. files)
- Auditable user actions via createdBy field

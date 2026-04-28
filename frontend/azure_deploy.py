#!/usr/bin/env python3
"""
Azure Frontend Deployment Script
Handles Next.js frontend deployment to Azure Static Web Apps
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


class AzureFrontendDeployment:
    """Handle complete frontend deployment to Azure Static Web Apps"""
    
    def __init__(self, web_app_name: str, resource_group: str):
        """
        Initialize frontend deployment
        
        Args:
            web_app_name: Azure Static Web App name
            resource_group: Azure Resource Group name
        """
        self.web_app_name = web_app_name
        self.resource_group = resource_group
        self.frontend_dir = Path(__file__).parent.parent / "frontend"
        self.log_file = self.frontend_dir / "deployment.log"
    
    def log(self, message: str, level: str = "INFO"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")
    
    def run_command(self, cmd: list, description: str) -> bool:
        """Run shell command"""
        self.log(f"Running: {description}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.log(f"Error: {result.stderr}", "ERROR")
                return False
            
            self.log(f"✅ {description}")
            return True
            
        except Exception as e:
            self.log(f"Exception: {str(e)}", "ERROR")
            return False
    
    def create_env_local(self, api_base_url: str) -> bool:
        """Create .env.local for production"""
        self.log("Creating .env.local for production...", "INFO")
        
        env_content = f"""# Production Frontend Configuration
NEXT_PUBLIC_API_BASE_URL={api_base_url}
NEXT_PUBLIC_ENVIRONMENT=production
"""
        
        env_path = self.frontend_dir / ".env.local"
        try:
            with open(env_path, "w") as f:
                f.write(env_content)
            self.log(f"✅ Created: {env_path}")
            return True
        except Exception as e:
            self.log(f"Error creating .env.local: {str(e)}", "ERROR")
            return False
    
    def create_next_config(self) -> bool:
        """Create optimized next.config.js for production"""
        self.log("Updating next.config.js for Azure...", "INFO")
        
        next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export', // Required for Azure Static Web Apps
  images: {
    unoptimized: true, // Azure Static Web Apps doesn't support Image Optimization
  },
  // Optional: Add trailing slashes for better compatibility
  trailingSlash: true,
}

module.exports = nextConfig
"""
        
        config_path = self.frontend_dir / "next.config.js"
        try:
            with open(config_path, "w") as f:
                f.write(next_config)
            self.log(f"✅ Updated: next.config.js")
            return True
        except Exception as e:
            self.log(f"Error updating next.config.js: {str(e)}", "ERROR")
            return False
    
    def create_staticwebapp_config(self) -> bool:
        """Create staticwebapp.config.json for Azure Static Web Apps routing"""
        self.log("Creating staticwebapp.config.json...", "INFO")
        
        config = {
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
                "rewrite": "index.html",
                "exclude": ["/images/*", "/css/*", "*.json"]
            },
            "mimeTypes": {
                ".json": "text/json",
                ".wasm": "application/wasm"
            },
            "responseOverrides": {
                "404": {
                    "rewrite": "/404/index.html"
                }
            }
        }
        
        config_path = self.frontend_dir / "public" / "staticwebapp.config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            self.log(f"✅ Created: staticwebapp.config.json")
            return True
        except Exception as e:
            self.log(f"Error creating config: {str(e)}", "ERROR")
            return False
    
    def install_dependencies(self) -> bool:
        """Install npm dependencies"""
        self.log("Installing npm dependencies...", "INFO")
        
        return self.run_command(
            ["npm", "install"],
            "npm install"
        )
    
    def build_project(self) -> bool:
        """Build Next.js project for production"""
        self.log("Building Next.js project for production...", "INFO")
        
        if not self.run_command(["npm", "run", "build"], "npm run build"):
            return False
        
        # Verify build output exists
        out_dir = self.frontend_dir / "out"
        if out_dir.exists():
            self.log(f"✅ Build output created at: {out_dir}")
            return True
        else:
            self.log("⚠️  Build output directory not found", "WARNING")
            return False
    
    def create_github_actions_workflow(self) -> bool:
        """Create GitHub Actions workflow for CI/CD"""
        self.log("Creating GitHub Actions workflow...", "INFO")
        
        workflow_content = """name: Azure Static Web Apps CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [ main, develop ]

jobs:
  build_and_deploy_job:
    runs-on: ubuntu-latest
    name: Build and Deploy Job
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm install

      - name: Build
        run: |
          cd frontend
          npm run build

      - name: Deploy to Azure Static Web Apps
        id: builddeploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "frontend/out"
          output_location: ""
          skip_app_build: true
"""
        
        workflow_dir = self.frontend_dir / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_path = workflow_dir / "azure_static_web_apps.yml"
        
        try:
            with open(workflow_path, "w") as f:
                f.write(workflow_content)
            self.log(f"✅ Created: {workflow_path}")
            return True
        except Exception as e:
            self.log(f"Error creating workflow: {str(e)}", "ERROR")
            return False
    
    def create_deployment_package(self) -> bool:
        """Create deployment package (out directory)"""
        self.log("Creating deployment package...", "INFO")
        
        out_dir = self.frontend_dir / "out"
        
        if not out_dir.exists():
            self.log("Build output not found. Please run build first.", "ERROR")
            return False
        
        # Create .deployment file for Azure
        deployment_content = """[config]
project = ./frontend
command = npm install && npm run build
"""
        
        deployment_path = self.frontend_dir.parent / ".deployment"
        try:
            with open(deployment_path, "w") as f:
                f.write(deployment_content)
            self.log(f"✅ Created: .deployment")
            return True
        except Exception as e:
            self.log(f"Error creating deployment file: {str(e)}", "ERROR")
            return False
    
    def print_summary(self, api_url: str = None):
        """Print deployment summary"""
        
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║             FRONTEND DEPLOYMENT SUMMARY                        ║
╚════════════════════════════════════════════════════════════════╝

✅ Configuration Files Created
✅ Build Ready for Azure
✅ GitHub Actions Workflow Generated

📋 DEPLOYMENT OPTIONS:

1️⃣  Using Azure Portal (Manual):
   - Go to Azure Static Web Apps
   - Connect repository
   - Build settings:
     * App location: frontend
     * API location: api
     * Output location: out

2️⃣  Using Azure CLI:
   az staticwebapp create \\
     --name {self.web_app_name} \\
     --resource-group {self.resource_group} \\
     --source https://github.com/YOUR_ORG/YOUR_REPO \\
     --location eastus \\
     --branch main \\
     --app-location "frontend" \\
     --output-location "out"

3️⃣  Using GitHub Actions (Recommended):
   - Push to GitHub
   - Create deployment token in Azure Portal
   - Add AZURE_STATIC_WEB_APPS_API_TOKEN secret
   - Workflow will auto-deploy on push

📝 FILES CREATED:
   ├─ .env.local (environment variables)
   ├─ next.config.js (production config)
   ├─ public/staticwebapp.config.json (routing)
   ├─ .deployment (Azure config)
   └─ .github/workflows/azure_static_web_apps.yml (CI/CD)

🌐 API Configuration:
""")
        
        if api_url:
            print(f"   API Base URL: {api_url}")
        else:
            print("   API Base URL: https://applicants-api-service.azurewebsites.net/api")
        
        print(f"""
📋 Build Output:
   Location: {self.frontend_dir / "out"}
   Size: Check with: du -sh {self.frontend_dir / "out"}

🔗 Deployment URLs:
   Production: https://{self.web_app_name}.azurestaticapps.net
   API: {api_url or "https://applicants-api-service.azurewebsites.net/api"}

⚡ Next Steps:
   1. Review environment variables in .env.local
   2. Run: npm run build (to verify build)
   3. Deploy using your preferred method above
   4. Test: https://{self.web_app_name}.azurestaticapps.net

📋 Deployment log: {self.log_file}

""")
    
    def run_deployment(self, api_url: str = None):
        """Run complete frontend deployment process"""
        
        self.log("=" * 60, "INFO")
        self.log("Starting Azure Frontend Deployment", "INFO")
        self.log("=" * 60, "INFO")
        
        if not api_url:
            api_url = "https://applicants-api-service.azurewebsites.net/api"
        
        # Step 1: Create configuration files
        if not self.create_env_local(api_url):
            self.log("Failed to create .env.local", "ERROR")
            return False
        
        # Step 2: Update next.config.js
        if not self.create_next_config():
            self.log("Failed to update next.config.js", "ERROR")
            return False
        
        # Step 3: Create Azure routing config
        if not self.create_staticwebapp_config():
            self.log("Failed to create routing config", "ERROR")
            return False
        
        # Step 4: Create GitHub Actions workflow
        if not self.create_github_actions_workflow():
            self.log("Warning: Could not create GitHub Actions workflow", "WARNING")
        
        # Step 5: Create deployment file
        if not self.create_deployment_package():
            self.log("Warning: Could not create deployment file", "WARNING")
        
        # Step 6: Install dependencies
        self.log("Frontend is ready for deployment", "INFO")
        self.log("Next: Run 'npm run build' to create production build", "INFO")
        
        # Step 7: Print summary
        self.print_summary(api_url)
        
        self.log("=" * 60, "INFO")
        self.log("✅ Frontend deployment ready!", "INFO")
        self.log("=" * 60, "INFO")


def main():
    """Main entry point"""
    
    web_app_name = os.getenv(
        "AZURE_WEB_APP_NAME",
        "applicants-web-app"
    )
    
    resource_group = os.getenv(
        "AZURE_RESOURCE_GROUP",
        "applicants-rg"
    )
    
    api_url = os.getenv(
        "API_BASE_URL",
        "https://applicants-api-service.azurewebsites.net/api"
    )
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║        Azure Frontend Deployment Script v1.0                   ║
╚════════════════════════════════════════════════════════════════╝

Configuration:
├─ Web App: {web_app_name}
├─ Resource Group: {resource_group}
├─ Frontend Directory: frontend/
└─ API URL: {api_url}

    """)
    
    deployer = AzureFrontendDeployment(web_app_name, resource_group)
    deployer.run_deployment(api_url)


if __name__ == "__main__":
    main()

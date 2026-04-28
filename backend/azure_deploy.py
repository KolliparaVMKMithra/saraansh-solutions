#!/usr/bin/env python3
"""
Azure Backend Deployment Script
Handles all backend deployment steps to Azure App Service
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class AzureBackendDeployment:
    """Handle complete backend deployment to Azure"""
    
    def __init__(self, app_service_name: str, resource_group: str):
        """
        Initialize deployment handler
        
        Args:
            app_service_name: Azure App Service name
            resource_group: Azure Resource Group name
        """
        self.app_service_name = app_service_name
        self.resource_group = resource_group
        self.backend_dir = Path(__file__).parent
        self.project_root = self.backend_dir.parent
        self.log_file = self.backend_dir / "deployment.log"
        
    def log(self, message: str, level: str = "INFO"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")
    
    def run_command(self, cmd: list, description: str) -> bool:
        """
        Run shell command and log output
        
        Args:
            cmd: Command as list
            description: Description of command
            
        Returns:
            True if successful, False otherwise
        """
        self.log(f"Running: {description}")
        self.log(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                self.log(f"Output: {result.stdout[:200]}", "DEBUG")
            
            if result.returncode != 0:
                self.log(f"Error: {result.stderr}", "ERROR")
                return False
            
            self.log(f"✅ Completed: {description}")
            return True
            
        except Exception as e:
            self.log(f"Exception in {description}: {str(e)}", "ERROR")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        self.log("Installing Python dependencies...", "INFO")
        return self.run_command(
            ["pip", "install", "-r", "requirements.txt"],
            "Install requirements.txt"
        )
    
    def create_deployment_package(self) -> bool:
        """Create deployment package"""
        self.log("Creating deployment package...", "INFO")
        
        package_dir = self.backend_dir / "deployment_package"
        
        # Create clean package directory
        if package_dir.exists():
            import shutil
            shutil.rmtree(package_dir)
        
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy essential files
        files_to_copy = [
            "app.py",
            "database.py",
            "resume_parser.py",
            "auth_manager.py",
            "azure_storage.py",
            "bulk_parser.py",
            "requirements.txt",
            ".env",
            "web.config"  # Azure App Service config
        ]
        
        import shutil
        
        for file in files_to_copy:
            src = self.backend_dir / file
            if src.exists():
                dst = package_dir / file
                if src.is_file():
                    shutil.copy2(src, dst)
                    self.log(f"Copied: {file}")
            else:
                self.log(f"Skipped (not found): {file}", "WARNING")
        
        # Create uploads directory
        uploads_dir = package_dir / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        self.log(f"✅ Deployment package created at: {package_dir}")
        return True
    
    def create_web_config(self) -> bool:
        """Create web.config for Azure App Service"""
        self.log("Creating web.config for Azure App Service...", "INFO")
        
        web_config_content = """<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="Static Files" stopProcessing="true">
                    <match url="^(.*)$" />
                    <conditions logicalGrouping="MatchAll" trackAllCaptures="false">
                        <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
                        <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
                    </conditions>
                    <action type="Rewrite" url="app.py" />
                </rule>
            </rules>
        </rewrite>
        <security>
            <requestFiltering>
                <fileExtensions>
                    <add fileExtension=".py" allowed="true" />
                </fileExtensions>
            </requestFiltering>
        </security>
        <staticContent>
            <mimeMap fileExtension=".py" mimeType="text/plain" />
        </staticContent>
        <httpPlatform processPath="Python.exe" arguments="%%LAUNCHER_PATH%% --port %%%%HTTP_PLATFORM_PORT%%%%" 
            startupTimeLimit="60" requestTimeout="00:04:00">
            <environmentVariables>
                <environmentVariable name="PYTHONPATH" value="."/>
                <environmentVariable name="WSGI_LOG" value="\\\\?\%%APP_LOG_DIR%%\wfastcgi.log"/>
            </environmentVariables>
        </httpPlatform>
    </system.webServer>
</configuration>
"""
        
        web_config_path = self.backend_dir / "web.config"
        with open(web_config_path, "w") as f:
            f.write(web_config_content)
        
        self.log(f"✅ Created: {web_config_path}")
        return True
    
    def deploy_to_azure(self) -> bool:
        """Deploy package to Azure App Service using Git or ZIP"""
        self.log("Deploying to Azure App Service...", "INFO")
        
        # Using Azure CLI to deploy
        deploy_cmd = [
            "az", "webapp", "deployment", "source", "config-zip",
            "--resource-group", self.resource_group,
            "--name", self.app_service_name,
            "--src", str(self.backend_dir / "deployment_package.zip")
        ]
        
        self.log("Using Azure CLI for deployment...")
        self.log("Command: az webapp deployment source config-zip ...", "DEBUG")
        
        # Note: User will need to create ZIP manually in production
        self.log("⚠️  Manual deployment required", "WARNING")
        self.log("Please use one of these deployment methods:", "INFO")
        self.log("1. Azure App Service extension in VS Code", "INFO")
        self.log("2. Azure CLI: az webapp deployment source config-zip", "INFO")
        self.log("3. GitHub Actions for CI/CD", "INFO")
        
        return True
    
    def verify_deployment(self, app_url: str) -> bool:
        """Verify deployment by checking health endpoint"""
        self.log("Verifying deployment...", "INFO")
        
        import time
        
        for attempt in range(5):
            try:
                import requests
                response = requests.get(f"{app_url}/api/health", timeout=5)
                
                if response.status_code == 200:
                    self.log(f"✅ Health check passed: {response.json()}")
                    return True
                else:
                    self.log(f"Status code: {response.status_code}", "WARNING")
                    
            except Exception as e:
                self.log(f"Attempt {attempt + 1}/5 - Waiting for app startup: {str(e)}", "INFO")
                time.sleep(10)
        
        self.log("⚠️  Could not verify deployment", "WARNING")
        return False
    
    def create_startup_script(self) -> bool:
        """Create startup script for Azure App Service"""
        self.log("Creating startup script...", "INFO")
        
        startup_script = """#!/bin/bash
# Azure App Service Startup Script

echo "Starting Applicants API..."

# Install Python packages
pip install -r requirements.txt

# Collect static files (if needed)
# python manage.py collectstatic --noinput

# Run migrations (uncomment if needed)
# python scripts/migrate_database.py

# Start Flask app with Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 app:app
"""
        
        startup_path = self.backend_dir / "startup.sh"
        with open(startup_path, "w") as f:
            f.write(startup_script)
        
        self.log(f"✅ Created: {startup_path}")
        return True
    
    def print_summary(self, app_url: str = None):
        """Print deployment summary"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║             BACKEND DEPLOYMENT SUMMARY                         ║
╚════════════════════════════════════════════════════════════════╝

✅ Deployment Package Created
✅ Configuration Files Ready
✅ Startup Scripts Generated

📋 NEXT STEPS:

1. Verify requirements.txt has all dependencies
2. Deploy using Azure App Service extension:
   - Right-click backend folder
   - Select "Deploy to Web App"
   
3. OR use Azure CLI:
   cd backend
   az webapp deployment source config-zip \\
     --resource-group applicants-rg \\
     --name applicants-api-service \\
     --src ./deployment_package.zip

4. Set environment variables in Azure Portal:
   - Configuration → Application Settings
   - Add all variables from .env

5. Test the deployment:
   curl https://applicants-api-service.azurewebsites.net/api/health

""")
        
        if app_url:
            print(f"🌐 App URL: {app_url}")
        
        print(f"📋 Deployment log: {self.log_file}\n")
    
    def run_deployment(self, skip_deps: bool = False):
        """Run complete deployment process"""
        
        self.log("=" * 60, "INFO")
        self.log("Starting Azure Backend Deployment", "INFO")
        self.log("=" * 60, "INFO")
        
        # Step 1: Create configuration files
        if not self.create_web_config():
            self.log("Failed to create web.config", "ERROR")
            return False
        
        # Step 2: Create startup script
        if not self.create_startup_script():
            self.log("Failed to create startup script", "ERROR")
            return False
        
        # Step 3: Create deployment package
        if not self.create_deployment_package():
            self.log("Failed to create deployment package", "ERROR")
            return False
        
        # Step 4: Summary
        self.print_summary(f"https://{self.app_service_name}.azurewebsites.net")
        
        self.log("=" * 60, "INFO")
        self.log("✅ Deployment package ready!", "INFO")
        self.log("=" * 60, "INFO")


def main():
    """Main entry point"""
    
    # Get deployment parameters
    app_service_name = os.getenv(
        "AZURE_APP_SERVICE_NAME",
        "applicants-api-service"
    )
    
    resource_group = os.getenv(
        "AZURE_RESOURCE_GROUP",
        "applicants-rg"
    )
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║        Azure Backend Deployment Script v1.0                    ║
╚════════════════════════════════════════════════════════════════╝

Configuration:
├─ App Service: {app_service_name}
├─ Resource Group: {resource_group}
└─ Backend Directory: {Path(__file__).parent}

    """)
    
    # Create deployment handler
    deployer = AzureBackendDeployment(app_service_name, resource_group)
    
    # Run deployment
    deployer.run_deployment()


if __name__ == "__main__":
    main()

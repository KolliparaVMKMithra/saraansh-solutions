"""
Test Azure Blob Storage Integration
"""
import os

def test_azure_storage():
    """Test Azure Blob Storage functionality"""
    print("Testing Azure Blob Storage Integration")
    print("=" * 50)

    # Check environment variables
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_CONTAINER_NAME', 'resumes')

    print(f"Connection String: {'✅ Set' if connection_string else '❌ Not set'}")
    print(f"Container Name: {container_name}")

    if connection_string:
        print("✅ Azure Blob Storage environment configured")
        print(f"   Type: {'Azure Production' if not connection_string.startswith('UseDevelopmentStorage') else 'Azurite (Local)'}")

        # Try to import and initialize (without connecting)
        try:
            from azure_storage import azure_storage
            if azure_storage.blob_service_client:
                print("✅ Azure Blob Storage client initialized")
                print("   Resume files will be uploaded to Azure automatically")
            else:
                print("⚠️  Azure Blob Storage client not initialized")
                print("   Check your connection string and network")
        except Exception as e:
            print(f"❌ Failed to initialize Azure client: {str(e)}")
    else:
        print("⚠️  Azure Blob Storage not configured")
        print("   Using local file storage only")
        print("   To enable Azure storage:")
        print("   1. For local dev: set AZURE_STORAGE_CONNECTION_STRING=UseDevelopmentStorage=true")
        print("   2. For Azure: set your Azure Storage connection string")

    print("\nℹ️  The app will work with or without Azure Blob Storage")
    print("   Files are stored locally if Azure is not available")

if __name__ == "__main__":
    test_azure_storage()
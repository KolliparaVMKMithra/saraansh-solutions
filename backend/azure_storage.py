"""
Azure Blob Storage Module
Handles file uploads and downloads from Azure Blob Storage
"""
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from typing import Optional, Dict, Any
import uuid


class AzureBlobStorage:
    """
    Azure Blob Storage client for resume file management
    """

    def __init__(self):
        """Initialize Azure Blob Storage client"""
        self.connection_string = os.getenv(
            'AZURE_STORAGE_CONNECTION_STRING',
            'UseDevelopmentStorage=true'  # Use Azurite for local development
        )

        self.container_name = os.getenv('AZURE_CONTAINER_NAME', 'resumes')

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)

            # Create container if it doesn't exist
            try:
                self.container_client.create_container()
                print(f"✅ Created container: {self.container_name}")
            except ResourceExistsError:
                print(f"ℹ️  Container already exists: {self.container_name}")

        except Exception as e:
            print(f"⚠️  Azure Blob Storage not configured: {str(e)}")
            print("   Using local file storage only")
            self.blob_service_client = None

    def upload_file(self, file_path: str, filename: str) -> Optional[str]:
        """
        Upload a file to Azure Blob Storage

        Args:
            file_path: Local file path
            filename: Original filename

        Returns:
            Blob URL if successful, None if failed
        """
        if not self.blob_service_client:
            return None

        try:
            # Generate unique blob name to avoid conflicts
            file_extension = os.path.splitext(filename)[1]
            unique_name = f"{uuid.uuid4()}{file_extension}"

            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=unique_name
            )

            # Upload the file
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            # Return the blob URL
            blob_url = blob_client.url
            print(f"✅ Uploaded {filename} to Azure Blob: {blob_url}")
            return blob_url

        except Exception as e:
            print(f"❌ Failed to upload {filename} to Azure Blob: {str(e)}")
            return None

    def download_file(self, blob_url: str, download_path: str) -> bool:
        """
        Download a file from Azure Blob Storage

        Args:
            blob_url: Azure blob URL
            download_path: Local path to save the file

        Returns:
            True if successful, False otherwise
        """
        if not self.blob_service_client:
            return False

        try:
            # Extract blob name from URL
            blob_name = blob_url.split('/')[-1]

            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            with open(download_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())

            print(f"✅ Downloaded blob to: {download_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to download blob: {str(e)}")
            return False

    def delete_file(self, blob_url: str) -> bool:
        """
        Delete a file from Azure Blob Storage

        Args:
            blob_url: Azure blob URL

        Returns:
            True if successful, False otherwise
        """
        if not self.blob_service_client:
            return False

        try:
            # Extract blob name from URL
            blob_name = blob_url.split('/')[-1]

            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            blob_client.delete_blob()
            print(f"✅ Deleted blob: {blob_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to delete blob: {str(e)}")
            return False

    def delete_all_blobs(self) -> int:
        """
        Delete all files from Azure Blob Storage container

        Returns:
            Number of blobs deleted
        """
        if not self.blob_service_client:
            return 0

        try:
            blob_list = self.container_client.list_blobs()
            count = 0
            
            for blob in blob_list:
                self.container_client.delete_blob(blob.name)
                count += 1
                print(f"✅ Deleted blob: {blob.name}")
            
            print(f"✅ Successfully deleted {count} blobs from container")
            return count

        except Exception as e:
            print(f"❌ Failed to delete all blobs: {str(e)}")
            return 0


# Global instance
azure_storage = AzureBlobStorage()

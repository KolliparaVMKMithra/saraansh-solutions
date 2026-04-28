import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';

interface UploadResponse {
  success: boolean;
  message: string;
  data?: any;
}

export default function UploadComponent() {
  const { token } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      setMessage('No valid files selected');
      setMessageType('error');
      return;
    }

    setUploading(true);
    const formData = new FormData();

    acceptedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post<UploadResponse>(
        'http://localhost:5000/api/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          },
        }
      );

      setMessage(response.data.message);
      setMessageType('success');
    } catch (error: any) {
      setMessage(error.response?.data?.message || 'Upload failed');
      setMessageType('error');
    } finally {
      setUploading(false);
    }
  }, [token]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc', '.docx'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [
        '.docx',
      ],
    },
  });

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-900 mb-2">📤 Upload Resumes</h1>
      <p className="text-gray-600 mb-8">Add new applicants by uploading resumes</p>

      <div
        {...getRootProps()}
        className={`border-3 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-6xl mb-4">📁</div>
        {isDragActive ? (
          <p className="text-blue-600 font-bold text-lg">Drop resumes here...</p>
        ) : (
          <>
            <p className="text-gray-700 font-bold text-lg mb-2">
              Drag & drop resumes here
            </p>
            <p className="text-gray-500">or click to browse</p>
            <p className="text-gray-500 text-sm mt-2">Supported: PDF, DOCX, DOC</p>
          </>
        )}
      </div>

      {message && (
        <div
          className={`mt-6 p-4 rounded-lg text-center font-semibold ${
            messageType === 'success'
              ? 'bg-green-100 text-green-800 border-2 border-green-400'
              : 'bg-red-100 text-red-800 border-2 border-red-400'
          }`}
        >
          {uploading ? (
            <div className="flex items-center justify-center gap-2">
              <div className="animate-spin">⏳</div>
              <span>Processing resumes...</span>
            </div>
          ) : (
            <span>{messageType === 'success' ? '✅ ' : '❌ '} {message}</span>
          )}
        </div>
      )}

      {/* Supported Formats */}
      <div className="mt-8 grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-4 text-center border">
          <div className="text-3xl mb-2">📄</div>
          <p className="text-gray-700 font-semibold">PDF Files</p>
          <p className="text-sm text-gray-600">.pdf</p>
        </div>
        <div className="bg-white rounded-lg p-4 text-center border">
          <div className="text-3xl mb-2">📝</div>
          <p className="text-gray-700 font-semibold">Word Documents</p>
          <p className="text-sm text-gray-600">.docx, .doc</p>
        </div>
        <div className="bg-white rounded-lg p-4 text-center border">
          <div className="text-3xl mb-2">✨</div>
          <p className="text-gray-700 font-semibold">Auto-Extract</p>
          <p className="text-sm text-gray-600">Data parsed instantly</p>
        </div>
      </div>
    </div>
  );
}


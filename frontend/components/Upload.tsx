import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { getApiUrl } from '@/lib/api-config';

interface UploadResponse {
  success: boolean;
  message: string;
  data?: {
    parsed: any[];
    errors: { file: string; error: string }[];
  };
}

interface FileStatus {
  name: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export default function UploadComponent() {
  const { token } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');
  const [fileStatuses, setFileStatuses] = useState<FileStatus[]>([]);
  const [progress, setProgress] = useState(0);
  const [successCount, setSuccessCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      setMessage('No valid files selected');
      setMessageType('error');
      return;
    }

    // Reset state
    setUploading(true);
    setMessage('');
    setProgress(0);
    setSuccessCount(0);
    setErrorCount(0);
    setTotalCount(acceptedFiles.length);

    // Initialize all files as pending
    setFileStatuses(
      acceptedFiles.map((file) => ({
        name: file.name,
        status: 'pending',
      }))
    );

    // Upload files one by one so we can track per-file progress
    let successTotal = 0;
    let errorTotal = 0;

    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];

      // Mark current file as uploading
      setFileStatuses((prev) =>
        prev.map((f, idx) =>
          idx === i ? { ...f, status: 'uploading' } : f
        )
      );

      try {
        const formData = new FormData();
        formData.append('files', file);

        const apiUrl = getApiUrl();
        const response = await axios.post<UploadResponse>(
          `${apiUrl}/upload`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const hasErrors =
          response.data.data?.errors && response.data.data.errors.length > 0;
        const hasParsed =
          response.data.data?.parsed && response.data.data.parsed.length > 0;

        if (hasParsed) {
          successTotal++;
          setSuccessCount(successTotal);
          setFileStatuses((prev) =>
            prev.map((f, idx) =>
              idx === i ? { ...f, status: 'success' } : f
            )
          );
        } else {
          const errMsg =
            response.data.data?.errors?.[0]?.error || 'Parse failed';
          errorTotal++;
          setErrorCount(errorTotal);
          setFileStatuses((prev) =>
            prev.map((f, idx) =>
              idx === i ? { ...f, status: 'error', error: errMsg } : f
            )
          );
        }
      } catch (error: any) {
        errorTotal++;
        setErrorCount(errorTotal);
        setFileStatuses((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? {
                  ...f,
                  status: 'error',
                  error: error.response?.data?.message || 'Upload failed',
                }
              : f
          )
        );
      }

      // Update progress after each file
      const done = i + 1;
      setProgress(Math.round((done / acceptedFiles.length) * 100));
    }

    // Final message
    if (errorTotal === 0) {
      setMessage(
        `All ${successTotal} resume${successTotal !== 1 ? 's' : ''} uploaded successfully!`
      );
      setMessageType('success');
    } else if (successTotal === 0) {
      setMessage(`All ${errorTotal} uploads failed. Check errors below.`);
      setMessageType('error');
    } else {
      setMessage(
        `${successTotal} uploaded successfully, ${errorTotal} failed.`
      );
      setMessageType('success');
    }

    setUploading(false);
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

  const resetUpload = () => {
    setFileStatuses([]);
    setMessage('');
    setProgress(0);
    setSuccessCount(0);
    setErrorCount(0);
    setTotalCount(0);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-900 mb-2">📤 Upload Resumes</h1>
      <p className="text-gray-600 mb-8">Add new applicants by uploading resumes</p>

      {/* Drop Zone — hidden while uploading */}
      {!uploading && fileStatuses.length === 0 && (
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
              <p className="text-gray-500 text-sm mt-2">
                Supported: PDF, DOCX, DOC
              </p>
            </>
          )}
        </div>
      )}

      {/* Progress Section */}
      {(uploading || fileStatuses.length > 0) && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-800">
              {uploading ? '⏳ Uploading Resumes...' : '✅ Upload Complete'}
            </h2>
            {!uploading && (
              <button
                onClick={resetUpload}
                className="text-sm text-blue-600 hover:text-blue-800 font-semibold border border-blue-300 px-3 py-1 rounded-lg hover:bg-blue-50 transition"
              >
                Upload More
              </button>
            )}
          </div>

          {/* Stats Row */}
          <div className="flex gap-4 mb-4">
            <div className="flex-1 bg-blue-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-blue-700">{totalCount}</p>
              <p className="text-xs text-blue-600 font-medium">Total</p>
            </div>
            <div className="flex-1 bg-green-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-green-700">{successCount}</p>
              <p className="text-xs text-green-600 font-medium">Successful</p>
            </div>
            <div className="flex-1 bg-red-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-red-700">{errorCount}</p>
              <p className="text-xs text-red-600 font-medium">Failed</p>
            </div>
            <div className="flex-1 bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-gray-700">
                {totalCount - successCount - errorCount}
              </p>
              <p className="text-xs text-gray-500 font-medium">Remaining</p>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className={`h-4 rounded-full transition-all duration-500 ${
                  uploading
                    ? 'bg-blue-500'
                    : errorCount === 0
                    ? 'bg-green-500'
                    : successCount === 0
                    ? 'bg-red-500'
                    : 'bg-yellow-500'
                }`}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Per-file Status List */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {fileStatuses.map((file, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-3 p-3 rounded-lg text-sm ${
                  file.status === 'success'
                    ? 'bg-green-50 border border-green-200'
                    : file.status === 'error'
                    ? 'bg-red-50 border border-red-200'
                    : file.status === 'uploading'
                    ? 'bg-blue-50 border border-blue-200'
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                {/* Status Icon */}
                <span className="text-lg flex-shrink-0">
                  {file.status === 'success'
                    ? '✅'
                    : file.status === 'error'
                    ? '❌'
                    : file.status === 'uploading'
                    ? '⏳'
                    : '⬜'}
                </span>

                {/* File name */}
                <span
                  className={`flex-1 font-medium truncate ${
                    file.status === 'success'
                      ? 'text-green-800'
                      : file.status === 'error'
                      ? 'text-red-800'
                      : file.status === 'uploading'
                      ? 'text-blue-800'
                      : 'text-gray-500'
                  }`}
                >
                  {file.name}
                </span>

                {/* Status label */}
                <span
                  className={`text-xs font-semibold flex-shrink-0 ${
                    file.status === 'success'
                      ? 'text-green-600'
                      : file.status === 'error'
                      ? 'text-red-600'
                      : file.status === 'uploading'
                      ? 'text-blue-600'
                      : 'text-gray-400'
                  }`}
                >
                  {file.status === 'success'
                    ? 'Parsed'
                    : file.status === 'error'
                    ? file.error || 'Failed'
                    : file.status === 'uploading'
                    ? 'Processing...'
                    : 'Waiting'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Final message */}
      {message && !uploading && (
        <div
          className={`mt-4 p-4 rounded-lg text-center font-semibold ${
            messageType === 'success'
              ? 'bg-green-100 text-green-800 border-2 border-green-400'
              : 'bg-red-100 text-red-800 border-2 border-red-400'
          }`}
        >
          {messageType === 'success' ? '✅ ' : '❌ '}
          {message}
        </div>
      )}

      {/* Supported Formats — only show when not uploading */}
      {!uploading && fileStatuses.length === 0 && (
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
      )}
    </div>
  );
}
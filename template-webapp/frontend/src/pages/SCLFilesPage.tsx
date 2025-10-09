/**
 * SCL Files Management Page (Admin Only)
 *
 * Features:
 * - File upload with drag-and-drop
 * - File gallery with status
 * - RDF schema visualization
 */
import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSCLFiles } from '../hooks/useSCLFiles';
import { SCLFile } from '../types';

const SCLFilesPage: React.FC = () => {
  const { files, loading, error, uploadFile, deleteFile, refreshFiles } = useSCLFiles();
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileSelect = async (selectedFiles: FileList | null) => {
    if (!selectedFiles || selectedFiles.length === 0) return;

    const file = selectedFiles[0];

    // Validate file extension
    const validExtensions = ['.scd', '.icd', '.cid', '.SCD', '.ICD', '.CID'];
    const hasValidExtension = validExtensions.some(ext => file.name.endsWith(ext));

    if (!hasValidExtension) {
      alert('Invalid file format. Only .scd, .icd, .cid files are supported.');
      return;
    }

    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      alert(`File too large. Maximum size is ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    setUploading(true);
    try {
      await uploadFile(file);
      // Refresh file list after upload
      await refreshFiles();
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      alert(`Upload failed: ${err}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDelete = async (fileId: number) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
      await deleteFile(fileId);
      await refreshFiles();
    } catch (err) {
      alert(`Delete failed: ${err}`);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'uploaded': return 'bg-blue-100 text-blue-800';
      case 'converting': return 'bg-yellow-100 text-yellow-800';
      case 'converted': return 'bg-green-100 text-green-800';
      case 'validated': return 'bg-green-200 text-green-900';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">SCL Files Management</h1>
        <p className="text-gray-600">
          Upload and manage IEC 61850 SCL files (.scd, .icd, .cid)
        </p>
      </div>

      {/* Upload Section */}
      <div className="mb-8">
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragOver
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".scd,.icd,.cid,.SCD,.ICD,.CID"
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
            id="file-upload"
          />

          {uploading ? (
            <div>
              <div className="text-lg font-medium mb-2">Uploading...</div>
              <div className="text-sm text-gray-600">Processing file...</div>
            </div>
          ) : (
            <div>
              <div className="mb-4">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div className="mb-4">
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer text-blue-600 hover:text-blue-500 font-medium"
                >
                  Click to upload
                </label>
                <span className="text-gray-600"> or drag and drop</span>
              </div>
              <p className="text-sm text-gray-500">
                SCL files (.scd, .icd, .cid) up to 100MB
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Files Gallery */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Uploaded Files</h2>

        {files.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-600">No files uploaded yet</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {files.map((file) => (
              <div
                key={file.id}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-1 truncate" title={file.original_filename}>
                      {file.original_filename}
                    </h3>
                    <p className="text-sm text-gray-500">{formatFileSize(file.file_size)}</p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      file.status
                    )}`}
                  >
                    {file.status}
                  </span>
                </div>

                {/* Progress Bar */}
                {file.status === 'converting' && file.progress_percent !== null && (
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        {file.conversion_stage || 'Processing'}
                      </span>
                      <span className="text-sm font-medium text-gray-700">
                        {file.progress_percent}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${file.progress_percent}%` }}
                      ></div>
                    </div>
                    {file.stage_message && (
                      <p className="text-xs text-gray-600">{file.stage_message}</p>
                    )}
                    {file.estimated_minutes && (
                      <p className="text-xs text-gray-500 mt-1">
                        Estimated time: ~{file.estimated_minutes} min
                      </p>
                    )}
                  </div>
                )}

                {/* Validation Info */}
                {file.is_validated && (
                  <div className="mb-4">
                    <div className={`text-sm ${file.validation_passed ? 'text-green-600' : 'text-red-600'}`}>
                      {file.validation_passed ? '✓ Validated' : '✗ Validation Failed'}
                    </div>
                    {file.validation_message && (
                      <p className="text-xs text-gray-600 mt-1">{file.validation_message}</p>
                    )}
                  </div>
                )}

                {/* Stats */}
                {file.triple_count && (
                  <div className="mb-4 text-sm text-gray-600">
                    <div>{file.triple_count.toLocaleString()} RDF triples</div>
                    {file.fuseki_dataset && (
                      <div className="text-xs text-gray-500 mt-1">
                        Dataset: {file.fuseki_dataset}
                      </div>
                    )}
                  </div>
                )}

                {/* Error Message */}
                {file.error_message && (
                  <div className="mb-4 text-sm text-red-600 bg-red-50 p-2 rounded">
                    {file.error_message}
                  </div>
                )}

                {/* Metadata */}
                <div className="mb-4 text-xs text-gray-500">
                  <div>Uploaded by: {file.uploaded_by}</div>
                  <div>
                    {new Date(file.uploaded_at).toLocaleString()}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {file.status === 'validated' && (
                    <button
                      onClick={() => navigate(`/scl-files/${file.id}/rdf-schema`)}
                      className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
                    >
                      View RDF Schema
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(file.id)}
                    className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SCLFilesPage;

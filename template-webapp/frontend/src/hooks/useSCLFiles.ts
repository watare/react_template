/**
 * Custom hook for SCL files management
 *
 * Data flow strategy:
 * - Server state: file list, status, validation results → Fetched from API, cached in React state
 * - Local state: uploading status, drag-over state → Component-local (ephemeral UI state)
 * - No Redux: This is admin-only feature with simple data flow
 */
import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { SCLFile } from '../types';

export const useSCLFiles = () => {
  const [files, setFiles] = useState<SCLFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/scl-files/');
      setFiles(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch files');
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/scl-files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  };

  const deleteFile = async (fileId: number) => {
    await api.delete(`/scl-files/${fileId}`);
  };

  const getFileDetails = async (fileId: number): Promise<SCLFile> => {
    const response = await api.get(`/scl-files/${fileId}`);
    return response.data;
  };

  const getRDFSchema = async (fileId: number) => {
    const response = await api.get(`/scl-files/${fileId}/rdf-schema`);
    return response.data;
  };

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  // Auto-refresh files every 5 seconds if any file is processing
  useEffect(() => {
    const hasProcessing = files.some(
      f => f.status === 'uploaded' || f.status === 'converting'
    );

    if (!hasProcessing) return;

    const interval = setInterval(() => {
      fetchFiles();
    }, 5000);

    return () => clearInterval(interval);
  }, [files, fetchFiles]);

  return {
    files,
    loading,
    error,
    uploadFile,
    deleteFile,
    getFileDetails,
    getRDFSchema,
    refreshFiles: fetchFiles,
  };
};

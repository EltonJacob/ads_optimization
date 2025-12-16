'use client';

import { useState, useRef } from 'react';
import { apiClient } from '@/lib/api-client';
import type {
  UploadResponse,
  FilePreviewResponse,
  ImportStatusResponse,
} from '@/lib/api-client';

export default function DataImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadData, setUploadData] = useState<UploadResponse | null>(null);
  const [preview, setPreview] = useState<FilePreviewResponse | null>(null);
  const [importing, setImporting] = useState(false);
  const [importStatus, setImportStatus] = useState<ImportStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const profileId = process.env.NEXT_PUBLIC_DEFAULT_PROFILE_ID || 'profile_123';

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFileSelect(e.target.files[0]);
    }
  };

  const handleFileSelect = async (selectedFile: File) => {
    try {
      setError(null);
      setFile(selectedFile);
      setPreview(null);
      setUploadData(null);
      setImportStatus(null);

      // Upload file
      const uploadResponse = await apiClient.uploadFile(selectedFile, profileId);
      setUploadData(uploadResponse);

      // Get preview
      const previewResponse = await apiClient.previewUpload(uploadResponse.upload_id);
      setPreview(previewResponse);
    } catch (err) {
      console.error('File upload failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    }
  };

  const handleImport = async () => {
    if (!uploadData) return;

    try {
      setError(null);
      setImporting(true);

      // Start import
      const importResponse = await apiClient.importFile(uploadData.upload_id, profileId);

      // Poll status
      await apiClient.pollJobStatus(
        importResponse.job_id,
        'import',
        (status) => {
          setImportStatus(status as ImportStatusResponse);
        },
        60,
        2000
      );

      setImporting(false);
    } catch (err) {
      console.error('Import failed:', err);
      setError(err instanceof Error ? err.message : 'Import failed');
      setImporting(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setUploadData(null);
    setPreview(null);
    setImportStatus(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-black">Data Import</h1>
        <p className="text-gray-600 mt-1">
          Upload CSV or Excel files to import campaign performance data
        </p>
      </div>

      {/* Upload Area */}
      {!file && (
        <div
          className={`
            relative border-2 border-dashed rounded-lg p-12 text-center
            transition-all duration-200
            ${
              dragActive
                ? 'border-yellow-400 bg-yellow-50'
                : 'border-gray-300 bg-white hover:border-yellow-400'
            }
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileInputChange}
            className="hidden"
          />

          <div className="flex flex-col items-center">
            <svg
              className="w-16 h-16 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>

            <p className="text-lg font-medium text-black mb-2">
              Drag and drop your file here
            </p>
            <p className="text-sm text-gray-500 mb-4">or</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-yellow-400 text-black font-medium rounded-md hover:bg-yellow-500 transition-colors"
            >
              Browse Files
            </button>
            <p className="text-xs text-gray-500 mt-4">
              Supported formats: CSV, XLSX, XLS (Max 100MB)
            </p>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-red-800 font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* File Preview */}
      {preview && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-black">File Preview</h2>
              <p className="text-sm text-gray-600">
                {preview.filename} - {preview.total_rows} rows
              </p>
            </div>
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
          </div>

          {/* Validation Errors */}
          {preview.validation_errors.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <h3 className="font-medium text-yellow-800 mb-2">Validation Warnings</h3>
              <ul className="space-y-1">
                {preview.validation_errors.map((err, idx) => (
                  <li key={idx} className="text-sm text-yellow-700">
                    <strong>{err.field}:</strong> {err.message}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Missing Columns */}
          {preview.missing_columns.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <h3 className="font-medium text-red-800 mb-2">Missing Required Columns</h3>
              <p className="text-sm text-red-700">{preview.missing_columns.join(', ')}</p>
            </div>
          )}

          {/* Preview Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {preview.detected_columns.map((col) => (
                    <th
                      key={col}
                      className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {preview.preview_rows.map((row) => (
                  <tr key={row.row_number}>
                    {preview.detected_columns.map((col) => (
                      <td
                        key={col}
                        className="px-4 py-3 whitespace-nowrap text-sm text-gray-900"
                      >
                        {row.data[col] || '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Import Button */}
          {preview.missing_columns.length === 0 && (
            <div className="flex justify-end">
              <button
                onClick={handleImport}
                disabled={importing}
                className={`
                  px-6 py-3 font-medium rounded-md transition-colors
                  ${
                    importing
                      ? 'bg-gray-400 text-white cursor-not-allowed'
                      : 'bg-yellow-400 text-black hover:bg-yellow-500'
                  }
                `}
              >
                {importing ? 'Importing...' : 'Import Data'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Import Progress */}
      {importing && importStatus && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-black mb-4">Import Progress</h2>

          <div className="space-y-4">
            {/* Progress Bar */}
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Status: {importStatus.status}</span>
                <span>{importStatus.progress || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${importStatus.progress || 0}%` }}
                />
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-black">
                  {importStatus.rows_processed}
                </p>
                <p className="text-sm text-gray-600">Processed</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {importStatus.rows_added}
                </p>
                <p className="text-sm text-gray-600">Added</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-600">
                  {importStatus.rows_skipped}
                </p>
                <p className="text-sm text-gray-600">Skipped</p>
              </div>
            </div>

            {/* Errors */}
            {importStatus.errors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <h3 className="font-medium text-red-800 mb-2">Errors</h3>
                <ul className="space-y-1">
                  {importStatus.errors.map((err, idx) => (
                    <li key={idx} className="text-sm text-red-700">
                      {err}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Success Message */}
      {importStatus && importStatus.status === 'completed' && !importing && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center gap-3">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <h3 className="text-lg font-semibold text-green-800">Import Completed</h3>
              <p className="text-sm text-green-700">
                Successfully imported {importStatus.rows_added} rows
              </p>
            </div>
          </div>
          <div className="mt-4 flex gap-4">
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-white border border-gray-300 text-black font-medium rounded-md hover:bg-gray-50 transition-colors"
            >
              Import Another File
            </button>
            <button
              onClick={() => (window.location.href = '/dashboard')}
              className="px-4 py-2 bg-yellow-400 text-black font-medium rounded-md hover:bg-yellow-500 transition-colors"
            >
              View Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

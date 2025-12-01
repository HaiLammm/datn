"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { uploadPdf } from '@/lib/pdf'; // Adjust path if necessary based on your tsconfig.json paths

export function PdfUploader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Replace with your actual backend API endpoint
  const API_URL = '/api/upload-pdf'; 

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setMessage('');
      setError('');
    } else {
      setSelectedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file first.');
      return;
    }

    setUploading(true);
    setMessage('');
    setError('');

    try {
      const response = await uploadPdf(selectedFile, API_URL);
      setMessage(`File uploaded successfully! Response: ${JSON.stringify(response)}`);
      setSelectedFile(null); // Clear selected file after successful upload
      if (document.getElementById('pdf-file-input') instanceof HTMLInputElement) {
        (document.getElementById('pdf-file-input') as HTMLInputElement).value = ''; // Reset input field
      }
    } catch (err) {
      setError(`Upload failed: ${(err as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4 p-6 border rounded-lg shadow-md bg-white">
      <h2 className="text-xl font-semibold">Upload PDF</h2>
      <div>
        <Input
          id="pdf-file-input"
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
        {selectedFile && (
          <p className="mt-2 text-sm text-gray-600">Selected file: {selectedFile.name}</p>
        )}
      </div>
      <Button
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
      >
        {uploading ? 'Uploading...' : 'Upload PDF'}
      </Button>
      {message && <p className="text-green-600 text-sm">{message}</p>}
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  );
}

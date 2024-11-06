// src/components/ImageUpload.jsx

import React, { useState, useCallback, useEffect } from 'react';
import { Upload, X, Image as ImageIcon, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const ImageUpload = () => {
  // State management
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Constants
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  const VALID_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
  const UPLOAD_TIMEOUT = 30000; // 30 seconds

  // Cleanup preview URL on unmount
  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  // Reset success message after 5 seconds
  useEffect(() => {
    let timer;
    if (uploadSuccess) {
      timer = setTimeout(() => {
        setUploadSuccess(false);
      }, 5000);
    }
    return () => clearTimeout(timer);
  }, [uploadSuccess]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
  }, []);

  const validateFile = (file) => {
    if (!file) return 'Please select a file';
    if (!VALID_TYPES.includes(file.type)) 
      return 'Please select a valid image file (JPG, PNG, or GIF)';
    if (file.size > MAX_FILE_SIZE) 
      return 'File size must be less than 5MB';
    return null;
  };

  const handleFileSelect = (selectedFile) => {
    setError(null);
    setUploadSuccess(false);
    setUploadProgress(0);

    const validationError = validateFile(selectedFile);
    if (validationError) {
      setError(validationError);
      toast.error(validationError);
      return;
    }

    setFile(selectedFile);

    // Create preview
    const previewUrl = URL.createObjectURL(selectedFile);
    setPreview(previewUrl);
  };

  const handleUpload = async () => {
    if (!file) {
      const errorMsg = 'Please select a file first';
      setError(errorMsg);
      toast.error(errorMsg);
      return;
    }

    setLoading(true);
    setError(null);
    setUploadSuccess(false);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), UPLOAD_TIMEOUT);

      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
        },
      });

      clearTimeout(timeoutId);

      const responseText = await response.text();
      let data;
      
      try {
        data = JSON.parse(responseText);
      } catch (e) {
        console.error('Failed to parse response:', responseText);
        throw new Error('Invalid response from server');
      }

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }

      setUploadSuccess(true);
      toast.success('File uploaded successfully!');
      console.log('Upload successful:', data.s3_path);
      
      // Clear form after successful upload
      clearFile();
      
    } catch (err) {
      console.error('Upload error:', err);
      const errorMsg = err.name === 'AbortError' 
        ? 'Upload timed out. Please try again.'
        : err.message || 'An error occurred during upload';
      
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const clearFile = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setFile(null);
    setPreview(null);
    setError(null);
    setUploadSuccess(false);
    setUploadProgress(0);
  };

  return (
    <div className="w-full max-w-xl mx-auto p-6">
      {/* Upload Area */}
      <div 
        className={`
          border-2 border-dashed rounded-lg p-6 text-center 
          ${error ? 'border-red-400' : 'border-gray-300'} 
          hover:border-gray-400 transition-colors
          ${file ? 'bg-gray-50' : 'bg-white'}
          ${loading ? 'opacity-50 pointer-events-none' : ''}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
      >
        {!file ? (
          <div className="space-y-4">
            <div className="flex justify-center">
              <ImageIcon className="h-12 w-12 text-gray-400" />
            </div>
            <div>
              <label className="cursor-pointer text-blue-500 hover:text-blue-600">
                <span>Choose a file</span>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                  disabled={loading}
                />
              </label>
              <p className="text-gray-500 mt-2">or drag and drop</p>
            </div>
            <p className="text-sm text-gray-500">
              PNG, JPG, GIF up to 5MB
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {preview && (
              <div className="relative w-48 h-48 mx-auto">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-full object-cover rounded"
                />
                <button
                  onClick={clearFile}
                  className="absolute -top-2 -right-2 p-1 bg-red-500 rounded-full text-white hover:bg-red-600"
                  disabled={loading}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
            <div className="text-sm text-gray-500">
              {file.name}
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {/* Success Message */}
      {uploadSuccess && (
        <div className="mt-4 p-3 bg-green-100 text-green-700 rounded">
          File uploaded successfully!
        </div>
      )}

      {/* Upload Progress */}
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="mt-4">
          <div className="h-2 bg-gray-200 rounded">
            <div 
              className="h-full bg-blue-500 rounded transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className={`
          mt-4 w-full flex items-center justify-center px-4 py-2 rounded
          ${loading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'}
          text-white transition-colors
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
      >
        {loading ? (
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-b-transparent border-white mr-2" />
            Uploading...
          </div>
        ) : (
          <div className="flex items-center">
            <Upload className="h-5 w-5 mr-2" />
            Upload Image
          </div>
        )}
      </button>
    </div>
  );
};

export default ImageUpload;
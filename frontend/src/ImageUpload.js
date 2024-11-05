import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [recentUploads, setRecentUploads] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecentUploads();
  }, []);

  const fetchRecentUploads = async () => {
    try {
      const { data } = await axios.get(`${process.env.REACT_APP_API_URL}/recent-uploads`);
      setRecentUploads(data.uploads);
    } catch (error) {
      console.error('Error fetching recent uploads:', error);
      setError('Failed to fetch recent uploads');
    }
  };

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setUploading(true);
    setError(null);
    
    try {
      const { data } = await axios.post(
        `${process.env.REACT_APP_API_URL}/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      setSelectedFile(null);
      fetchRecentUploads();
      alert('File uploaded successfully!');
    } catch (error) {
      console.error('Error uploading file:', error.response?.data?.error || error.message);
      setError(error.response?.data?.error || 'Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Upload Image to S3</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="mb-4">
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleFileSelect}
          className="mb-2"
        />
        <button 
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          className={`px-4 py-2 rounded ${
            !selectedFile || uploading 
              ? 'bg-gray-300 cursor-not-allowed' 
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>

      <h3 className="text-lg font-semibold mb-2">Recent Uploads</h3>
      <div className="grid grid-cols-2 gap-4">
        {recentUploads.map((url, index) => (
          <div key={index} className="border rounded p-2">
            <img 
              src={url} 
              alt={`Upload ${index + 1}`} 
              className="w-full h-48 object-cover rounded"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ImageUpload;
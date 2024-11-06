import React from 'react';
import { Toaster } from 'react-hot-toast';
import ImageUpload from './ImageUpload';

const App = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
            Image Upload
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
            Upload your images securely to S3
          </p>
        </div>
        <div className="mt-12">
          <ImageUpload />
        </div>
      </div>
      <Toaster position="top-right" />
    </div>
  );
};

export default App;
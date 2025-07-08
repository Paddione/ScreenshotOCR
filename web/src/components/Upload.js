import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon, File, X, Check, AlertCircle } from 'lucide-react';
import { api } from '../services/web_auth_service';

const Upload = () => {
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState('');
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState('');

  React.useEffect(() => {
    loadFolders();
  }, []);

  const loadFolders = async () => {
    try {
      const response = await api.get('/folders');
      if (response.data) {
        setFolders(response.data);
      }
    } catch (error) {
      console.error('Error loading folders:', error);
    }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    setError('');
    
    for (const file of acceptedFiles) {
      if (!file.type.startsWith('image/')) {
        setError('Please upload only image files (PNG, JPG, GIF, etc.)');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError('File size must be less than 10MB');
        return;
      }
    }

    setUploadStatus('uploading');
    
    try {
      const uploadPromises = acceptedFiles.map(async (file) => {
        const formData = new FormData();
        formData.append('image', file);
        
        if (selectedFolder) {
          formData.append('folder_id', selectedFolder);
        }

        const response = await api.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        return {
          file,
          response: response.data,
          status: 'success'
        };
      });

      const results = await Promise.allSettled(uploadPromises);
      
      const successfulUploads = results
        .filter(result => result.status === 'fulfilled')
        .map(result => result.value);
      
      const failedUploads = results
        .filter(result => result.status === 'rejected')
        .map(result => result.reason);

      setUploadedFiles(successfulUploads);
      
      if (failedUploads.length > 0) {
        setError(`${failedUploads.length} file(s) failed to upload`);
        setUploadStatus('error');
      } else {
        setUploadStatus('success');
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      setError('Upload failed. Please try again.');
      setUploadStatus('error');
    }
  }, [selectedFolder]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    multiple: true
  });

  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadedFiles([]);
    setError('');
  };

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1>Upload Screenshots</h1>
        <p>Upload images for OCR processing and AI analysis</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Select Folder (Optional)</h2>
          <p>Choose a folder to organize your uploads</p>
        </div>
        
        <div className="folder-selector">
          <select
            value={selectedFolder}
            onChange={(e) => setSelectedFolder(e.target.value)}
            className="form-control"
          >
            <option value="">No folder (General)</option>
            {folders.map(folder => (
              <option key={folder.id} value={folder.id}>
                {folder.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        <div className="upload-area">
          {uploadStatus === 'idle' && (
            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
              <input {...getInputProps()} />
              <div className="dropzone-content">
                <UploadIcon size={48} />
                <h3>
                  {isDragActive 
                    ? 'Drop the files here...' 
                    : 'Drag & drop images here, or click to select'
                  }
                </h3>
                <p>Supports PNG, JPG, GIF and other image formats (max 10MB each)</p>
                <button type="button" className="btn btn-primary">
                  Choose Files
                </button>
              </div>
            </div>
          )}

          {uploadStatus === 'uploading' && (
            <div className="upload-progress">
              <div className="loading-spinner"></div>
              <h3>Uploading and processing...</h3>
              <p>Your images are being uploaded and queued for analysis</p>
            </div>
          )}

          {uploadStatus === 'success' && (
            <div className="upload-success">
              <Check size={48} className="success-icon" />
              <h3>Upload Successful!</h3>
              <p>
                {uploadedFiles.length} file(s) uploaded and queued for processing.
                You can view the results in the Responses section once processing is complete.
              </p>
              
              <div className="uploaded-files">
                {uploadedFiles.map((upload, index) => (
                  <div key={index} className="uploaded-file">
                    <File size={16} />
                    <span>{upload.file.name}</span>
                    <Check size={16} className="file-success" />
                  </div>
                ))}
              </div>

              <div className="upload-actions">
                <button onClick={resetUpload} className="btn btn-secondary">
                  Upload More Files
                </button>
                <a href="/responses" className="btn btn-primary">
                  View Responses
                </a>
              </div>
            </div>
          )}

          {uploadStatus === 'error' && (
            <div className="upload-error">
              <AlertCircle size={48} className="error-icon" />
              <h3>Upload Failed</h3>
              <p>{error}</p>
              
              <div className="upload-actions">
                <button onClick={resetUpload} className="btn btn-primary">
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Processing Information</h2>
          <p>What happens after upload</p>
        </div>
        
        <div className="info-grid">
          <div className="info-item">
            <div className="info-number">1</div>
            <div className="info-content">
              <h4>Image Upload</h4>
              <p>Your image is securely uploaded to the server</p>
            </div>
          </div>
          
          <div className="info-item">
            <div className="info-number">2</div>
            <div className="info-content">
              <h4>OCR Processing</h4>
              <p>Advanced OCR extracts text with high accuracy</p>
            </div>
          </div>
          
          <div className="info-item">
            <div className="info-number">3</div>
            <div className="info-content">
              <h4>AI Analysis</h4>
              <p>GPT-4 analyzes content and provides insights</p>
            </div>
          </div>
          
          <div className="info-item">
            <div className="info-number">4</div>
            <div className="info-content">
              <h4>Results Available</h4>
              <p>View, search, and export your analysis results</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload; 
import { useState } from 'react'
import './App.css'

function App() {
  const [files, setFiles] = useState({
    designDoc: null,
    specDoc: null
  });
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (e, fileType) => {
    setFiles(prev => ({
      ...prev,
      [fileType]: e.target.files[0]
    }));
  };

  const handleUpload = async () => {
    if (!files.designDoc || !files.specDoc) {
      setUploadStatus('Please select both documents before uploading');
      return;
    }

    const formData = new FormData();
    formData.append('designDoc', files.designDoc);
    formData.append('specDoc', files.specDoc);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      console.log(response);

      if (response.ok) {
        setUploadStatus('Documents uploaded successfully!');
        setFiles({ designDoc: null, specDoc: null });
      } else {
        setUploadStatus('Upload failed. Please try again.');
      }
    } catch (error) {
      setUploadStatus('Error uploading documents. Please try again.');
      console.error('Upload error:', error);
    }
  };

  return (
    <div className="upload-container">
      <h1>Upload</h1>
      <div className="file-inputs">
        <div className="file-input-group">
          <label htmlFor="designDoc">Design Document</label>
          <input
            type="file"
            id="designDoc"
            onChange={(e) => handleFileChange(e, 'designDoc')}
          />
          <span>{files.designDoc?.name || 'No design document selected'}</span>
        </div>
        
        <div className="file-input-group">
          <label htmlFor="specDoc">Specification Document</label>
          <input
            type="file"
            id="specDoc"
            onChange={(e) => handleFileChange(e, 'specDoc')}
          />
          <span>{files.specDoc?.name || 'No specification document selected'}</span>
        </div>
      </div>

      <button 
        onClick={handleUpload}
        disabled={!files.designDoc || !files.specDoc}
        className="upload-button"
      >
        Upload Documents
      </button>

      {uploadStatus && (
        <p className="status-message">{uploadStatus}</p>
      )}
    </div>
  )
}

export default App

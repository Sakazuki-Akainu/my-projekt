import React from 'react';

const UploadForm = ({ onUpload }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    const file = e.target.file.files[0];
    if (file) onUpload(file);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
      <input type="file" name="file" />
      <button type="submit">Upload</button>
    </form>
  );
};

export default UploadForm;

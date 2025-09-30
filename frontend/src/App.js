import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import GraphCard from './components/GraphCard';
import UploadForm from './components/UploadForm';
import ChatBox from './components/ChatBox';
import './styles/App.css';

function App() {
  const [graphs, setGraphs] = useState([]);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Fetch initial graphs if needed
  }, []);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch('http://localhost:3000/upload', { method: 'POST', body: formData });
    const data = await response.json();
    setGraphs(data.graphs || []);
  };

  return (
    <div className={darkMode ? 'dark' : ''} style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar */}
      <div className="sidebar">
        <a href="#"><i>📊</i><span>Dashboard</span></a>
        <a href="#">⬇️<span>Download</span></a>
        <a href="#" onClick={() => setDarkMode(!darkMode)}><i>🌙</i><span>Dark Mode</span></a>
        <a href="#"><i>🤖</i><span>AI Chat</span></a>
      </div>
      {/* Left: Graphs */}
      <motion.div 
        className="graph-area"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{ width: '300px', overflowY: 'auto', padding: '10px', borderRight: '1px solid #ddd' }}
      >
        <h3>Graphs</h3>
        {graphs.map((graph, i) => (
          <GraphCard key={i} index={i} graphData={graph} />
        ))}
      </motion.div>
      {/* Right: Upload/Features */}
      <div className="content" style={{ flex: 1, padding: '20px' }}>
        <h2>Data Dashboard</h2>
        <UploadForm onUpload={handleUpload} />
        <div className="features">
          <a href="#">Feature 1</a>
          <a href="#">Feature 2</a>
          <a href="#">Feature 3</a>
        </div>
        <ChatBox />
      </div>
    </div>
  );
}

export default App;

import React from 'react';

const ChatBox = () => {
  return (
    <div style={{ marginTop: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <div style={{ padding: '10px', maxHeight: '200px', overflowY: 'auto', background: '#f9f9f9' }}></div>
      <div style={{ display: 'flex', borderTop: '1px solid #ddd' }}>
        <input type="text" placeholder="Ask about data..." style={{ flex: 1, padding: '8px', border: 'none' }} />
        <button style={{ padding: '8px 12px', background: '#007bff', color: '#fff', border: 'none' }}>Send</button>
      </div>
    </div>
  );
};

export default ChatBox;

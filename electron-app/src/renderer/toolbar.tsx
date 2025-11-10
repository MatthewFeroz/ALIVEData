import React from 'react';
import ReactDOM from 'react-dom/client';

function Toolbar() {
  return (
    <div style={{
      width: '100%',
      height: '60px',
      backgroundColor: 'rgba(26, 26, 26, 0.95)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderTop: '1px solid #333',
      backdropFilter: 'blur(10px)',
    }}>
      <div style={{ color: '#fff', fontSize: '14px' }}>
        ALIVE Data Toolbar
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('toolbar-root')!).render(
  <React.StrictMode>
    <Toolbar />
  </React.StrictMode>
);


import React, { useState, useEffect } from 'react';

interface Capture {
  timestamp: string;
  screenshotPath: string;
  command?: string;
}

interface RecordingLogProps {
  isRecording: boolean;
}

const RecordingLog: React.FC<RecordingLogProps> = ({ isRecording }) => {
  const [captures, setCaptures] = useState<Capture[]>([]);

  useEffect(() => {
    if (isRecording) {
      // Listen for capture events
      const handleCapture = (event: any, data: Capture) => {
        setCaptures(prev => [...prev, data]);
      };

      // TODO: Set up IPC listener for captures
      // window.electronAPI.onCapture(handleCapture);

      return () => {
        // Cleanup listener
      };
    } else {
      setCaptures([]);
    }
  }, [isRecording]);

  return (
    <div
      style={{
        position: 'fixed',
        top: '10px',
        right: '10px',
        width: '400px',
        maxHeight: '500px',
        backgroundColor: 'rgba(26, 26, 26, 0.95)',
        borderRadius: '8px',
        padding: '15px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        zIndex: 1000,
        overflowY: 'auto',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: 0, color: '#fff' }}>
          {isRecording ? '🔴 Recording...' : 'Recording Log'}
        </h3>
        <button
          onClick={() => setCaptures([])}
          style={{
            padding: '5px 10px',
            backgroundColor: '#444',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Clear
        </button>
      </div>

      {captures.length === 0 ? (
        <p style={{ color: '#888', fontSize: '14px' }}>No captures yet...</p>
      ) : (
        <div>
          {captures.map((capture, index) => (
            <div
              key={index}
              style={{
                padding: '10px',
                marginBottom: '10px',
                backgroundColor: '#2a2a2a',
                borderRadius: '4px',
                fontSize: '12px',
              }}
            >
              <div style={{ color: '#888', marginBottom: '5px' }}>
                {capture.timestamp}
              </div>
              {capture.command && (
                <div style={{ color: '#fff', marginBottom: '5px', fontFamily: 'monospace' }}>
                  {capture.command}
                </div>
              )}
              <div style={{ color: '#4A9EFF', fontSize: '11px' }}>
                {capture.screenshotPath.split('/').pop()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecordingLog;


import React, { useState, useEffect } from 'react';

interface Window {
  hwnd: number;
  title: string;
  processName: string;
  executablePath: string;
  processId: number;
}

interface WindowSelectorProps {
  onSelect: (windows: number[], processes: string[]) => void;
  onCancel: () => void;
}

const WindowSelector: React.FC<WindowSelectorProps> = ({ onSelect, onCancel }) => {
  const [windows, setWindows] = useState<Window[]>([]);
  const [selectedWindows, setSelectedWindows] = useState<Set<number>>(new Set());
  const [selectedProcesses, setSelectedProcesses] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWindows();
  }, []);

  const loadWindows = async () => {
    try {
      setLoading(true);
      const windowList = await window.electronAPI.getWindows();
      setWindows(windowList || []);
    } catch (error) {
      console.error('Failed to load windows:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleWindow = (hwnd: number) => {
    const newSelected = new Set(selectedWindows);
    if (newSelected.has(hwnd)) {
      newSelected.delete(hwnd);
    } else {
      newSelected.add(hwnd);
    }
    setSelectedWindows(newSelected);
  };

  const toggleProcess = (processName: string) => {
    const newSelected = new Set(selectedProcesses);
    if (newSelected.has(processName)) {
      newSelected.delete(processName);
    } else {
      newSelected.add(processName);
    }
    setSelectedProcesses(newSelected);
  };

  const handleSelect = () => {
    onSelect(Array.from(selectedWindows), Array.from(selectedProcesses));
  };

  const filteredWindows = windows.filter(
    win =>
      win.title.toLowerCase().includes(filter.toLowerCase()) ||
      win.processName.toLowerCase().includes(filter.toLowerCase())
  );

  // Group by process
  const processGroups = filteredWindows.reduce((acc, win) => {
    if (!acc[win.processName]) {
      acc[win.processName] = [];
    }
    acc[win.processName].push(win);
    return acc;
  }, {} as Record<string, Window[]>);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>Loading windows...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Select Windows to Track</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Filter windows..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '14px',
            borderRadius: '4px',
            border: '1px solid #333',
            backgroundColor: '#2a2a2a',
            color: '#fff',
          }}
        />
      </div>

      <div style={{ maxHeight: '400px', overflowY: 'auto', marginBottom: '20px' }}>
        {Object.entries(processGroups).map(([processName, processWindows]) => (
          <div key={processName} style={{ marginBottom: '15px' }}>
            <div
              style={{
                padding: '10px',
                backgroundColor: '#2a2a2a',
                borderRadius: '4px',
                cursor: 'pointer',
                marginBottom: '5px',
              }}
              onClick={() => toggleProcess(processName)}
            >
              <input
                type="checkbox"
                checked={selectedProcesses.has(processName)}
                onChange={() => toggleProcess(processName)}
                style={{ marginRight: '10px' }}
              />
              <strong>{processName}</strong>
            </div>
            {processWindows.map((win) => (
              <div
                key={win.hwnd}
                style={{
                  padding: '8px',
                  paddingLeft: '30px',
                  backgroundColor: '#1a1a1a',
                  borderRadius: '4px',
                  marginBottom: '2px',
                  cursor: 'pointer',
                }}
                onClick={() => toggleWindow(win.hwnd)}
              >
                <input
                  type="checkbox"
                  checked={selectedWindows.has(win.hwnd)}
                  onChange={() => toggleWindow(win.hwnd)}
                  style={{ marginRight: '10px' }}
                />
                {win.title || 'Untitled'}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
        <button
          onClick={onCancel}
          style={{
            padding: '10px 20px',
            backgroundColor: '#444',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Cancel
        </button>
        <button
          onClick={handleSelect}
          disabled={selectedWindows.size === 0 && selectedProcesses.size === 0}
          style={{
            padding: '10px 20px',
            backgroundColor: '#4CAF50',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            opacity: selectedWindows.size === 0 && selectedProcesses.size === 0 ? 0.5 : 1,
          }}
        >
          Select ({selectedWindows.size} windows, {selectedProcesses.size} processes)
        </button>
      </div>
    </div>
  );
};

export default WindowSelector;


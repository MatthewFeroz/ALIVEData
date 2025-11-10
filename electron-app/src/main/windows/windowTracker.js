// Simplified WindowTracker - no native modules required
// This provides a basic interface that can be extended later with native modules if needed

class WindowTracker {
  constructor() {
    this.knownWindows = new Map();
    this.lastForegroundWindow = null;
    this.isTracking = false;
    this.trackingInterval = null;
  }

  /**
   * Get all visible windows
   * Returns empty array - can be extended with native modules later
   */
  getAllWindows() {
    // Return empty array for now - app will work without window list
    return [];
  }

  /**
   * Get information about a specific window
   */
  getWindowInfo(hwnd) {
    // Return null - not available without native modules
    return null;
  }

  /**
   * Get current foreground window
   */
  getForegroundWindow() {
    // Return null - not available without native modules
    return null;
  }

  /**
   * Start tracking window focus changes
   * No-op without native modules
   */
  startTracking(callback) {
    if (this.isTracking) {
      return;
    }

    // Silently do nothing - tracking not available without native modules
    this.isTracking = true;
    console.log('Window tracking started (fallback mode - no native modules)');
  }

  /**
   * Stop tracking window focus changes
   */
  stopTracking() {
    this.isTracking = false;
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
      this.trackingInterval = null;
    }
  }
}

module.exports = WindowTracker;

const screenshot = require('screenshot-desktop');
const fs = require('fs').promises;
const path = require('path');

class ScreenshotCapture {
  constructor() {
    this.outputDir = path.join(__dirname, '../../../../screenshots');
    this.ensureOutputDir();
  }

  async ensureOutputDir() {
    try {
      await fs.mkdir(this.outputDir, { recursive: true });
    } catch (error) {
      console.error('Error creating screenshots directory:', error);
    }
  }

  /**
   * Capture entire screen
   */
  async captureScreen(options = {}) {
    try {
      const img = await screenshot({ screen: options.screen || 0 });
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `screenshot_${timestamp}.png`;
      const filepath = path.join(this.outputDir, filename);

      await fs.writeFile(filepath, img);
      return filepath;
    } catch (error) {
      console.error('Error capturing screen:', error);
      throw error;
    }
  }

  /**
   * Capture specific window (by hwnd)
   * Note: screenshot-desktop doesn't support window capture directly,
   * so we'll capture the screen and crop to window bounds
   */
  async captureWindow(hwnd, windowRect) {
    try {
      // For now, capture full screen
      // In a full implementation, we'd crop to windowRect
      const img = await screenshot();
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `window_${hwnd}_${timestamp}.png`;
      const filepath = path.join(this.outputDir, filename);

      await fs.writeFile(filepath, img);
      return filepath;
    } catch (error) {
      console.error('Error capturing window:', error);
      throw error;
    }
  }

  /**
   * Capture region of screen
   */
  async captureRegion(x, y, width, height) {
    try {
      const img = await screenshot();
      // In a full implementation, we'd crop the image to the region
      // For now, return full screenshot
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `region_${x}_${y}_${width}_${height}_${timestamp}.png`;
      const filepath = path.join(this.outputDir, filename);

      await fs.writeFile(filepath, img);
      return filepath;
    } catch (error) {
      console.error('Error capturing region:', error);
      throw error;
    }
  }
}

module.exports = ScreenshotCapture;


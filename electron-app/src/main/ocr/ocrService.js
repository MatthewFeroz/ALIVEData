const Tesseract = require('tesseract.js');
const fs = require('fs').promises;
const path = require('path');

class OCRService {
  constructor() {
    this.worker = null;
    this.isInitialized = false;
  }

  /**
   * Initialize Tesseract worker
   */
  async initialize() {
    if (this.isInitialized && this.worker) {
      return;
    }

    try {
      this.worker = await Tesseract.createWorker('eng');
      await this.worker.setParameters({
        tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?@#$%^&*()_+-=[]{}|\\/"\'<>~` ',
      });
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize OCR worker:', error);
      throw error;
    }
  }

  /**
   * Extract text from image
   */
  async extractText(imagePath, options = {}) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      const { data } = await this.worker.recognize(imagePath, {
        rectangle: options.region ? {
          left: options.region.x,
          top: options.region.y,
          width: options.region.width,
          height: options.region.height,
        } : undefined,
      });

      return {
        text: data.text.trim(),
        confidence: data.confidence,
        words: data.words || [],
      };
    } catch (error) {
      console.error('OCR extraction failed:', error);
      throw error;
    }
  }

  /**
   * Extract text from a specific region of an image
   */
  async extractTextFromRegion(imagePath, region) {
    return this.extractText(imagePath, { region });
  }

  /**
   * Extract terminal command from screenshot
   * Attempts to find command lines in the text
   */
  async extractTerminalCommand(imagePath, region = null) {
    const result = await this.extractText(imagePath, { region });
    const lines = result.text.split('\n').filter(line => line.trim().length > 0);
    
    // Look for command patterns (lines starting with $, >, or common shell prompts)
    const commandPatterns = [
      /^\$ (.+)$/,           // $ command
      /^> (.+)$/,            // > command
      /^(.+@.+):(.+) (.+)$/, // user@host:path $ command
      /^(.+)$/,              // Any non-empty line (fallback)
    ];

    for (const line of lines.reverse()) { // Start from bottom (most recent commands)
      for (const pattern of commandPatterns) {
        const match = line.match(pattern);
        if (match) {
          const command = match[match.length - 1].trim();
          if (command.length > 0) {
            return {
              command,
              fullText: result.text,
              confidence: result.confidence,
            };
          }
        }
      }
    }

    // If no command pattern found, return the last line
    if (lines.length > 0) {
      return {
        command: lines[lines.length - 1].trim(),
        fullText: result.text,
        confidence: result.confidence,
      };
    }

    return {
      command: '',
      fullText: result.text,
      confidence: result.confidence,
    };
  }

  /**
   * Cleanup worker
   */
  async terminate() {
    if (this.worker) {
      await this.worker.terminate();
      this.worker = null;
      this.isInitialized = false;
    }
  }
}

module.exports = OCRService;


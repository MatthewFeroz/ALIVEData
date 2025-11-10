import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  root: path.resolve(__dirname, 'src/renderer'),
  base: './',
  build: {
    outDir: path.resolve(__dirname, 'dist/renderer'),
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    strictPort: true,
  },
  define: {
    // Expose environment variables to the renderer process
    'import.meta.env.VITE_WORKOS_CLIENT_ID': JSON.stringify(process.env.WORKOS_CLIENT_ID || ''),
    'import.meta.env.VITE_SKIP_AUTH': JSON.stringify(process.env.SKIP_AUTH || 'false'),
  },
});


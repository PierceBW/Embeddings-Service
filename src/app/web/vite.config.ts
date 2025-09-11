// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/predict': 'http://localhost:8000',
      '/predictions': 'http://localhost:8000',
      '/metadata': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    },
  },
}); 
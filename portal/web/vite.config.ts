import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

// Built into the portal image (Dockerfile stage "web"); dist/ becomes app/static. Assets get hashed names under /assets.
export default defineConfig({
  plugins: [react()],
  build: {target: 'es2022', outDir: 'dist', emptyOutDir: true, sourcemap: false, chunkSizeWarningLimit: 900},
});

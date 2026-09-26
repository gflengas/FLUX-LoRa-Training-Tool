import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [vue()],
    server: {
      host: '127.0.0.1',
      port: 3000,
      strictPort: true,
      proxy: { '/api': env.API_PROXY_TARGET || 'http://127.0.0.1:5000' },
    },
    preview: {
      host: '127.0.0.1',
      port: 3000,
      strictPort: true,
      proxy: { '/api': env.API_PROXY_TARGET || 'http://127.0.0.1:5000' },
    },
  };
});

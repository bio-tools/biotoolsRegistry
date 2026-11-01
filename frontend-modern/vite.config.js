import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  base: './',
  plugins: [vue()],
  server: { fs: { allow: ['.', '../backend/elixirapp/tests/data', '../backend/elixir/resource-contract.generated.ts'] } },
  test: { environment: 'jsdom', include: ['src/**/*.test.ts'] },
  build: {
    outDir: '../backend/elixir/static/modern',
    emptyOutDir: true,
    manifest: 'manifest.json',
    rollupOptions: { input: 'src/main.js' },
  },
});

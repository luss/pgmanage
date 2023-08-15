import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from "vite";
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { BootstrapVueNextResolver } from 'unplugin-vue-components/resolvers'
import path from 'node:path';
import { nodePolyfills } from 'vite-plugin-node-polyfills'

const outDir = path.join('..', 'dist');


export default defineConfig({
  plugins: [vue(), Components({
    resolvers: [BootstrapVueNextResolver()]
  }),
  nodePolyfills({
    globals: {
      process: true
    }
  })
],
  server: {
    host: '127.0.0.1',
    port: 3000,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  build: {
    manifest: true,
    rollupOptions: {
      input: './src/main.js'
    },
    outDir: outDir
  },
  base: '/static/',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js',
    },
  },
})
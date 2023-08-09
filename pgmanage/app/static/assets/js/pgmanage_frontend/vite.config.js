import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from "vite";
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { BootstrapVueNextResolver } from 'unplugin-vue-components/resolvers'
import path from 'node:path';

const outDir = path.join('..', 'dist');


export default defineConfig({
  plugins: [vue(), Components({
    resolvers: [BootstrapVueNextResolver()]
  })],
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
  // this makes Knex.js happy
  define: {
    'process.env': {}
  }
})
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // expõe em 0.0.0.0 para acessar de fora do container
    port: 5173,
    watch: {
      usePolling: true, // necessário para hot-reload em volumes Docker
    },
  },
});

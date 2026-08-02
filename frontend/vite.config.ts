import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/qa": "http://localhost:8000",
      "/index-pdf": "http://localhost:8000",
      "/upload-pdf": "http://localhost:8000"
    }
  }
});

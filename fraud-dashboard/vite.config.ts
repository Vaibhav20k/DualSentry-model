import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],

  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes("node_modules")) {
            if (id.includes("recharts") || id.includes("d3") || id.includes("victory")) {
              return "vendor-recharts";
            }
            if (id.includes("react-dom") || id.includes("react-router") || id.includes("react/")) {
              return "vendor-react";
            }
            if (id.includes("@tanstack") || id.includes("axios")) {
              return "vendor-query";
            }
            if (id.includes("lucide")) {
              return "vendor-icons";
            }
            return "vendor";
          }
        },
      },
    },
  },
});
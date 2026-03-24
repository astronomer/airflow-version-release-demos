import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react({ jsxRuntime: "classic" })],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  build: {
    lib: {
      entry: "src/index.tsx",
      formats: ["iife"],
      name: "ThemeExplorer",
      fileName: () => "theme-explorer.js",
    },
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
        },
      },
    },
    outDir: "static",
    emptyOutDir: false,
  },
});

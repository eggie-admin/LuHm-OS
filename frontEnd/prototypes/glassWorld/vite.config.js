import { defineConfig } from "vite";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  base: "./",
  build: {
    target: "es2022",
    sourcemap: false,
    reportCompressedSize: true,
    rollupOptions: {
      input: {
        index: fileURLToPath(new URL("./index.html", import.meta.url)),
        kiosk: fileURLToPath(new URL("./kiosk.html", import.meta.url))
      }
    }
  }
});

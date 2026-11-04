import { defineConfig } from "vite";
import { fileURLToPath } from "node:url";
export default defineConfig({
  base: "./",
  build: { target: "es2022", sourcemap: false, reportCompressedSize: true,
    rollupOptions: { input: {
      index: fileURLToPath(new URL("./index.html", import.meta.url)),
      antenna: fileURLToPath(new URL("./antenna.html", import.meta.url))
    }}
  }
});

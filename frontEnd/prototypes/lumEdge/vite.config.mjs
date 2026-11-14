import {defineConfig} from "vite";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
const here=fileURLToPath(new URL(".",import.meta.url));
export default defineConfig({
  server:{host:"127.0.0.1",fs:{strict:true,allow:[here,resolve(here,"../../../game/world")]}},
  preview:{host:"127.0.0.1"},
  build:{
    rollupOptions:{
      input:{
        lum:resolve(here,"index.html"),
        aramoor:resolve(here,"aramoor.html")
      }
    }
  }
});

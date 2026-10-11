import {defineConfig} from 'vite';
export default defineConfig({base:'./',build:{minify:false,rollupOptions:{treeshake:false},outDir:'/tmp/dd-build'}});

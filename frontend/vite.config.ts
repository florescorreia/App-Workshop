import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],build:{minify:false,rollupOptions:{treeshake:false}},server:{proxy:{'/api':'http://backend:8000'}}});

import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests',workers:1,timeout:45000,reporter:'list',use:{baseURL:process.env.APP_URL||'http://frontend',headless:true,trace:'off'},outputDir:'/tmp/browser-results'});

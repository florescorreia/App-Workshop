const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://gateway:8080/',{waitUntil:'networkidle'});
 await page.getByRole('heading',{name:'Evidence you can stand behind.'}).waitFor();
 await page.screenshot({path:'/evidence/login-desktop.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:'/evidence/login-mobile.png',fullPage:true});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile layout overflows');
 if(errors.length)throw Error(errors.join('\n'));
 console.log('Login desktop/mobile rendering passed; no browser errors or horizontal overflow.');
 await browser.close();
})();

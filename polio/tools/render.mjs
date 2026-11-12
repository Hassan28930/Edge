import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { resolve, join, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import chromium, { inflate, setupLambdaEnvironment } from '@sparticuz/chromium';
import { chromium as playwright } from 'playwright-core';
import { createServer } from './server.mjs';

const root=resolve(fileURLToPath(new URL('..',import.meta.url)));
const script=JSON.parse(await readFile(join(root,'script.json'),'utf8'));
const args=process.argv.slice(2);
const flag=(name,defaultValue)=>{
  const index=args.findIndex(a=>a===`--${name}` || a.startsWith(`--${name}=`));
  if(index<0) return defaultValue;
  return args[index].includes('=') ? args[index].split('=').slice(1).join('=') : args[index+1] ?? defaultValue;
};
const draft=args.includes('--draft');
const sheet=args.includes('--sheet');
const still=flag('still',null);
const start=Number(flag('from',0));
const end=Number(flag('to',script.format.duration));
const fps=draft?15:script.format.fps;
const scale=(draft||sheet)?.5:1;
if(!Number.isFinite(start)||!Number.isFinite(end)||start<0||end>script.format.duration||end<=start)
  throw new Error('Use 0 <= --from < --to <= 67.');
const defaultOutput=sheet ? 'export/stills' : still!==null ? `export/still-${Number(still).toFixed(2)}.png` :
  draft?'export/polio-draft.mp4':'export/polio-is-back-vertical.mp4';
const dest=flag('output',defaultOutput);
const output=isAbsolute(dest)?dest:join(root,dest);
await mkdir(sheet ? output : resolve(output,'..'),{recursive:true});

// The npm Chromium binary includes the Amazon Linux NSS libraries. Load those
// explicitly on Debian-based CI/sandboxes; no system browser or apt install needed.
const libArchive=join(root,'node_modules/@sparticuz/chromium/bin/al2023.tar.br');
await inflate(libArchive);
setupLambdaEnvironment('/tmp/al2023/lib');
const executablePath=await chromium.executablePath();
const server=createServer();
await new Promise(ok=>server.listen(0,'0.0.0.0',ok));
const address=server.address();
let browser;
try {
  browser=await playwright.launch({executablePath,args:chromium.args,headless:true});
  const page=await browser.newPage({viewport:{width:Math.round(1080*scale),height:Math.round(1920*scale)},deviceScaleFactor:1});
  page.on('pageerror',error=>console.error('Browser error:',error));
  await page.goto(`http://127.0.0.1:${address.port}/?render=1&scale=${scale}`);
  await page.waitForFunction('window.__POLIO_READY__ === true',null,{timeout:30000});
  if(sheet){
    for(let i=0;i<script.shots.length;i++){
      const shot=script.shots[i];
      const next=script.shots[i+1]?.at ?? script.format.duration;
      const t=shot.at+Math.min((next-shot.at)*.62,1.35);
      const png=await page.evaluate(t=>window.__POLIO_PNG__(t),t);
      await writeFile(join(output,`${shot.id}.png`),Buffer.from(png,'base64'));
    }
    console.log(`Saved ${script.shots.length} 540 x 960 storyboard frames in ${output}`);
  } else if(still!==null){
    const t=Number(still);
    if(!Number.isFinite(t)||t<0||t>script.format.duration) throw new Error('Invalid still time.');
    const png=await page.evaluate(t=>window.__POLIO_PNG__(t),t);
    await writeFile(output,Buffer.from(png,'base64'));
    console.log(`Saved ${Math.round(1080*scale)} x ${Math.round(1920*scale)} still: ${output}`);
  } else {
    const frames=Math.round((end-start)*fps), ffmpeg=join(root,'node_modules/@ffmpeg-installer/linux-x64/ffmpeg');
    const ffargs=['-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate',String(fps),
      '-vcodec','png','-i','pipe:0','-ss',String(start),'-i',join(root,'audio/mix.m4a'),
      '-map','0:v:0','-map','1:a:0','-frames:v',String(frames),'-t',String(end-start),
      '-c:v','libx264','-preset','veryfast','-threads','2','-crf',draft?'22':'19',
      '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',output];
    const encoder=spawn(ffmpeg,ffargs,{stdio:['pipe','ignore','pipe']});
    let encoderError=''; encoder.stderr.on('data',chunk=>encoderError+=chunk.toString());
    const done=new Promise((ok,fail)=>{
      encoder.on('error',fail);
      encoder.on('close',code=>code===0?ok():fail(new Error(`ffmpeg exited ${code}: ${encoderError.slice(-2000)}`)));
    });
    console.log(`Rendering ${frames} deterministic frames at ${Math.round(1080*scale)}x${Math.round(1920*scale)} / ${fps} fps.`);
    const begun=Date.now();
    for(let i=0;i<frames;i++){
      const t=start+i/fps;
      const png=await page.evaluate(t=>window.__POLIO_PNG__(t),t);
      const buffer=Buffer.from(png,'base64');
      await new Promise((ok,fail)=>encoder.stdin.write(buffer,error=>error?fail(error):ok()));
      if((i+1)%Math.max(1,Math.floor(fps*5))===0 || i===frames-1)
        console.log(`${(100*(i+1)/frames).toFixed(0)}% · frame ${i+1}/${frames} · ${(Date.now()-begun)/1000|0}s`);
    }
    encoder.stdin.end();
    await done;
    console.log(`Saved ${output}`);
  }
} finally {
  if(browser) await browser.close();
  await new Promise(ok=>server.close(ok));
}

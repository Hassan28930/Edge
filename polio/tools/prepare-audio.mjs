import { readFile, writeFile, mkdir, unlink } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root=resolve(fileURLToPath(new URL('..',import.meta.url)));
const ffmpeg=join(root,'node_modules/@ffmpeg-installer/linux-x64/ffmpeg');
const script=JSON.parse(await readFile(join(root,'script.json'),'utf8'));
const rate=48000, duration=script.format.duration, length=rate*duration;
const mix=new Float32Array(length);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const add=(index,value)=>{ if(index>=0 && index<length) mix[index]+=value; };

// A quiet, original, synthesized three-note bed: no sampled music or licensed assets.
const chords=[[196,246.94,293.66],[174.61,220,261.63],[164.81,207.65,246.94],[146.83,196,246.94]];
for(let i=0;i<length;i++){
  const t=i/rate, chord=chords[Math.floor(t/8)%chords.length];
  const envelope=Math.min(1,t/1.3,(duration-t)/.72);
  const breathe=.82+.18*Math.sin(t*.47);
  mix[i]=.0095*envelope*breathe*(Math.sin(2*Math.PI*chord[0]*t)*.5+
    Math.sin(2*Math.PI*chord[1]*t)*.24+Math.sin(2*Math.PI*chord[2]*t)*.16);
}

// Deterministic pseudo-noise makes a soft paper-like whoosh at each edit.
let seed=1789;
function random(){ seed=(Math.imul(seed,1664525)+1013904223)>>>0; return (seed/4294967296)*2-1; }
function whoosh(at,gain=.021){
  const start=Math.round(at*rate), count=Math.round(.17*rate);
  let smooth=0;
  for(let j=0;j<count;j++){
    const u=j/count;
    smooth=smooth*.94+random()*.06;
    add(start+j, smooth*gain*Math.sin(Math.PI*u)*(.28+.72*u));
  }
}
function pop(at,gain=.025,frequency=490){
  const start=Math.round(at*rate),count=Math.round(.19*rate);
  for(let j=0;j<count;j++){
    const u=j/count;
    add(start+j,Math.sin(2*Math.PI*frequency*(1-u*.34)*j/rate)*gain*(1-u)**3);
  }
}
function alarm(at){
  for(let k=0;k<3;k++) pop(at+k*.15,.018,331-k*50);
}
for(const shot of script.shots.slice(1)) whoosh(shot.at-.035);
for(const t of [5.05,12.37,17.45,36.72,41.23,46.04,52.72,57.61,66.13]) pop(t+.16,.022);
for(const t of [15.88,24.33,48.21,60.25,62.45]) alarm(t+.20);
for(const t of [29.25,30.18,50.57,51.40]) pop(t+.15,.010,680);

for(const voice of script.voice){
  const decoded=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-i',join(root,voice.file),
    '-ac','1','-ar',String(rate),'-f','s16le','pipe:1'],{maxBuffer:16*1024*1024});
  if(decoded.status!==0) throw new Error(`Cannot decode ${voice.file}: ${decoded.stderr}`);
  const input=decoded.stdout;
  const count=Math.min(Math.floor(input.length/2),Math.round(voice.duration*rate));
  let sum=0,peak=0;
  for(let i=0;i<count;i++){
    const v=input.readInt16LE(i*2)/32768;
    sum+=v*v; peak=Math.max(peak,Math.abs(v));
  }
  const rms=Math.sqrt(sum/count),gain=clamp(.15/rms,.88,1.50);
  const start=Math.round(voice.at*rate);
  for(let i=0;i<count;i++){
    const v=input.readInt16LE(i*2)/32768;
    const fade=Math.min(1,i/(rate*.012),(count-i-1)/(rate*.022));
    add(start+i,v*gain*Math.max(0,fade));
  }
  console.log(`${voice.file}: decoded ${(count/rate).toFixed(2)}s, RMS ${rms.toFixed(3)}, gain ${gain.toFixed(2)}`);
}

let peak=0;
for(let i=0;i<length;i++) peak=Math.max(peak,Math.abs(mix[i]));
const attenuation=peak>.94?.94/peak:1;
const pcm=Buffer.allocUnsafe(length*2);
for(let i=0;i<length;i++) pcm.writeInt16LE(Math.round(clamp(mix[i]*attenuation,-1,1)*32767),i*2);
const header=Buffer.alloc(44);
header.write('RIFF',0); header.writeUInt32LE(36+pcm.length,4); header.write('WAVEfmt ',8);
header.writeUInt32LE(16,16); header.writeUInt16LE(1,20); header.writeUInt16LE(1,22);
header.writeUInt32LE(rate,24); header.writeUInt32LE(rate*2,28);
header.writeUInt16LE(2,32); header.writeUInt16LE(16,34);
header.write('data',36); header.writeUInt32LE(pcm.length,40);
await mkdir(join(root,'export'),{recursive:true});
const temp=join(root,'export','audio-working.wav');
await writeFile(temp,Buffer.concat([header,pcm]));
const encoded=spawnSync(ffmpeg,['-y','-hide_banner','-loglevel','error','-i',temp,
  '-c:a','aac','-b:a','144k','-ar','48000','-t',String(duration),'-movflags','+faststart',
  join(root,'audio/mix.m4a')],{stdio:'inherit'});
await unlink(temp);
if(encoded.status!==0) throw new Error(`Audio encode failed (${encoded.status}).`);
console.log(`Finished 67-second narration, music and edit sound design. Peak: ${peak.toFixed(3)}.`);

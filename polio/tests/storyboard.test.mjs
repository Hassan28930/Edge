import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve, join } from 'node:path';
import { sceneNames } from '../src/shots.js';
import { parseCaption, activeCaption } from '../src/core/captions.js';

const root=resolve(fileURLToPath(new URL('..',import.meta.url)));
const script=JSON.parse(await readFile(join(root,'script.json'),'utf8'));

test('matches the requested output contract',()=>{
  assert.deepEqual(script.format,{width:1080,height:1920,fps:30,duration:67});
  assert.equal(script.captionLanguage,'English');
  assert.equal(script.narrationLanguage,'Hinglish');
  assert.equal(script.lead,.45);
  assert.equal(script.outro,.87);
});

test('30 cuts cover all 67 seconds without long static shots',()=>{
  assert.equal(script.shots.length,30);
  assert.equal(script.shots[0].at,0);
  for(let i=0;i<script.shots.length;i++){
    const shot=script.shots[i],next=script.shots[i+1]?.at ?? script.format.duration;
    const length=next-shot.at;
    assert.equal(shot.id,`S${String(i+1).padStart(2,'0')}`);
    assert.ok(sceneNames.includes(shot.scene),`missing scene: ${shot.scene}`);
    assert.ok(length>=1.5 && length<=3.5 || i===29 && Math.abs(length-script.outro)<.001,`${shot.id} lasts ${length}s`);
    assert.ok(next>shot.at);
  }
  assert.equal(script.shots.at(-1).at,script.format.duration-script.outro);
});

test('English captions are authored in timed 1-3 word chunks with one yellow keyword',()=>{
  assert.equal(script.shots[0].caps[0].at,script.lead);
  assert.deepEqual(script.shots.at(-1).caps,[]);
  for(let i=0;i<script.shots.length-1;i++){
    const shot=script.shots[i],duration=script.shots[i+1].at-shot.at;
    assert.ok(shot.caps.length>0,`missing captions on ${shot.id}`);
    let last=-1;
    for(const cap of shot.caps){
      assert.ok(cap.at>last && cap.at<duration,`${shot.id}: caption outside shot`);
      assert.match(cap.text,/^[A-Z0-9 ,.!?\-’'*]+$/i);
      const words=parseCaption(cap.text);
      assert.ok(words.length>=1 && words.length<=3,`${shot.id}: caption exceeds three words: ${cap.text}`);
      assert.equal(words.filter(w=>w.yellow).length,1,`${shot.id}: highlight exactly one word: ${cap.text}`);
      assert.ok(words.every(w=>w.word.length>0));
      assert.equal(activeCaption(shot,cap.at),cap);
      last=cap.at;
    }
  }
});

test('voice segments meet the lead, gaps, and final silent outro',async()=>{
  assert.equal(script.voice.length,7);
  assert.equal(script.voice[0].at,script.lead);
  for(let i=0;i<script.voice.length;i++){
    const clip=script.voice[i];
    await access(join(root,clip.file));
    if(i) assert.ok(clip.at>=script.voice[i-1].at+script.voice[i-1].duration+.14);
  }
  const last=script.voice.at(-1);
  assert.ok(Math.abs(last.at+last.duration-(script.format.duration-script.outro))<.001);
  await access(join(root,'audio/mix.m4a'));
});

test('chapter timestamps land exactly on shot starts',()=>{
  assert.equal(script.chapters.length,7);
  for(const chapter of script.chapters)
    assert.ok(script.shots.some(s=>s.at===chapter.at),`chapter ${chapter.title} is not a cut`);
});

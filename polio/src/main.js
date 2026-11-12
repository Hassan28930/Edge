import { C, W, H, clamp, seg, eo, box, rr, line, text } from './core/lib.js';
import { drawCaption } from './core/captions.js';
import { drawScene } from './shots.js';

const params = new URLSearchParams(location.search);
const exportMode = params.has('render');
const scale = exportMode ? clamp(Number(params.get('scale') || 1), .2, 1) : 1;
if (exportMode) document.body.classList.add('export-mode');
const canvas = document.getElementById('film');
canvas.width = Math.round(W * scale);
canvas.height = Math.round(H * scale);
const g = canvas.getContext('2d', { alpha:false, willReadFrequently:false });
let script, shownTime = 0, captionsOn = true, activeChapter = -1;
const chaptersElement = document.getElementById('chapter-list');
const playButton = document.getElementById('play');
const seek = document.getElementById('seek');
const current = document.getElementById('time-current');
const chapterIndex = document.getElementById('chapter-index');
const muteButton = document.getElementById('mute');
const captionsButton = document.getElementById('captions');
const audio = exportMode ? null : new Audio('./audio/mix.m4a');
const playIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6 3v18l15-9z"/></svg>';
const pauseIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="3" width="6" height="18" rx="1.4" fill="currentColor"/><rect x="14" y="3" width="6" height="18" rx="1.4" fill="currentColor"/></svg>';
const soundIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 4V5L7 9H3zm12-1c2 1 3 2.3 3 4s-1 3-3 4m2-11c3 1.7 5 4.1 5 7s-2 5.3-5 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const muteIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 4V5L7 9H3zM16 9l6 6m0-6l-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

function findIndex(items, t) {
  let index = 0;
  for (let i = 1; i < items.length && items[i].at <= t + 1e-7; i++) index = i;
  return index;
}
function stamp(g, t, darkMode) {
  const fg = darkMode ? C.paper : C.ink;
  rr(g, 80, 72, 87, 61, 13, C.yellow);
  text(g, 'IO', 123, 104, 36, C.ink);
  text(g, 'INSIDE OUT', 190, 104, 33, fg, 'left');
  text(g, 'POLIO / 01', 998, 104, 25, fg, 'right');
  line(g, 80, 170, 999, 170, darkMode ? '#555157' : C.stone, 5);
  rr(g, 80, 165, Math.max(1, 919 * t / script.format.duration), 10, 5, C.yellow);
  line(g, 80, 1678, 999, 1678, darkMode ? '#555157' : C.stone, 5);
  text(g, 'A VISUAL FIELD NOTE', 80, 1743, 25, fg, 'left');
  text(g, `${String(Math.floor(t/60)).padStart(2,'0')}:${String(Math.floor(t%60)).padStart(2,'0')} / 01:07`, 999, 1743, 26, fg, 'right');
  // Graphic pagination stays outside the caption safe zone.
  for (let i=0;i<7;i++) {
    rr(g, 80+i*38, 1804, i===findIndex(script.chapters,t) ? 28 : 12, 12, 6,
      i===findIndex(script.chapters,t) ? C.yellow : (darkMode ? '#666168' : C.stone));
  }
}
function paint(time) {
  if (!script) return;
  const t = clamp(Number(time) || 0, 0, script.format.duration);
  const i = findIndex(script.shots, t);
  const shot = script.shots[i];
  const next = script.shots[i+1]?.at ?? script.format.duration;
  const duration = next - shot.at;
  const lt = t - shot.at;
  const darkMode = ['conflict','problem','warZones','oneCase','momentum','risk'].includes(shot.scene);
  g.setTransform(scale, 0, 0, scale, 0, 0);
  g.clearRect(0, 0, W, H);
  g.save();
  // Punch on every cut, followed by a gentle continuous camera push.
  const zoom = 1.018 + .036 * seg(lt, 0, duration) + .053 * (1 - eo(seg(lt, 0, .28)));
  const drift = seg(lt, 0, duration);
  g.translate(W/2 + 8*drift, H/2 - 13*drift);
  g.scale(zoom, zoom);
  g.translate(-W/2, -H/2);
  drawScene(g, shot.scene, lt, duration, t);
  g.restore();
  if (i > 0 && lt < .095) {
    g.fillStyle = `rgba(255,255,255,${.63 * (1 - lt / .095)})`;
    g.fillRect(0,0,W,H);
  }
  stamp(g, t, darkMode);
  drawCaption(g, shot, lt, captionsOn);
  shownTime = t;
  if (!exportMode) updateUI(t);
}
function clock(t) {
  const sec = Math.floor(t);
  return `${Math.floor(sec/60)}:${String(sec%60).padStart(2,'0')}`;
}
function updateUI(t) {
  seek.value = String(t);
  seek.style.setProperty('--progress', `${100*t/script.format.duration}%`);
  current.textContent = clock(t);
  const ci = findIndex(script.chapters,t);
  chapterIndex.textContent = `${String(ci+1).padStart(2,'0')} / 07`;
  if (activeChapter !== ci) {
    activeChapter = ci;
    [...chaptersElement.children].forEach((el,j)=>el.classList.toggle('active', j===ci));
  }
}
let raf = 0, lastPreviewFrame = -1;
function tick() {
  const frame = Math.floor(audio.currentTime * script.format.fps);
  if (frame !== lastPreviewFrame) {
    paint(Math.min(frame / script.format.fps, script.format.duration));
    lastPreviewFrame = frame;
  }
  if (!audio.paused) raf = requestAnimationFrame(tick);
}
async function togglePlay() {
  if (audio.paused) {
    if (shownTime >= script.format.duration-.1) audio.currentTime=0;
    try {
      await audio.play();
      playButton.innerHTML = pauseIcon; playButton.setAttribute('aria-label','Pause video');
      cancelAnimationFrame(raf); tick();
    } catch (error) {
      playButton.title = 'Audio could not start: '+error.message;
      console.error(error);
    }
  } else {
    audio.pause(); cancelAnimationFrame(raf);
    playButton.innerHTML=playIcon; playButton.setAttribute('aria-label','Play video');
    paint(audio.currentTime);
  }
}
function seekTo(t) {
  const at = clamp(t,0,script.format.duration-.001);
  audio.currentTime = at;
  lastPreviewFrame = -1;
  paint(at);
}
async function boot() {
  const response = await fetch('./script.json');
  if (!response.ok) throw new Error('Cannot load the storyboard.');
  script = await response.json();
  await Promise.all([document.fonts.load('900 150px Inter'),document.fonts.load('600 28px Inter')]);
  paint(0);
  // Rendering interface: always deterministic, including for out-of-order frames.
  window.__POLIO_FRAME__ = t => { paint(t); return true; };
  window.__POLIO_PNG__ = t => { paint(t); return canvas.toDataURL('image/png').split(',')[1]; };
  window.__POLIO_INFO__ = script.format;
  window.__POLIO_READY__ = true;
  if (exportMode) return;
  audio.preload='auto';
  seek.max=String(script.format.duration);
  script.chapters.forEach((chapter,i) => {
    const button=document.createElement('button');
    button.type='button'; button.className='chapter'+(i===0?' active':'');
    button.innerHTML=`<span class="chapter-number">${chapter.number}</span><span><span class="chapter-title">${chapter.title}</span><span class="chapter-summary">${chapter.summary}</span></span>`;
    button.setAttribute('aria-label',`Go to chapter ${i+1}: ${chapter.title}`);
    button.addEventListener('click',()=>seekTo(chapter.at));
    chaptersElement.append(button);
  });
  playButton.addEventListener('click',togglePlay);
  audio.addEventListener('ended',()=>{
    cancelAnimationFrame(raf); paint(script.format.duration);
    playButton.innerHTML=playIcon; playButton.setAttribute('aria-label','Replay video');
  });
  seek.addEventListener('input',()=>seekTo(Number(seek.value)));
  muteButton.addEventListener('click',()=>{
    audio.muted=!audio.muted;
    muteButton.innerHTML=audio.muted?muteIcon:soundIcon;
    muteButton.setAttribute('aria-label',audio.muted?'Unmute narration':'Mute narration');
  });
  captionsButton.addEventListener('click',()=>{
    captionsOn=!captionsOn;
    captionsButton.textContent=captionsOn?'CC · ON':'CC · OFF';
    captionsButton.setAttribute('aria-pressed',String(captionsOn));
    paint(audio.currentTime);
  });
  document.addEventListener('keydown',e=>{
    if (e.target instanceof HTMLInputElement) return;
    if (e.code==='Space') { e.preventDefault(); togglePlay(); }
    if (e.code==='ArrowRight') { e.preventDefault(); seekTo(audio.currentTime+2); }
    if (e.code==='ArrowLeft') { e.preventDefault(); seekTo(audio.currentTime-2); }
  });
  // The download link is only offered after an export actually exists.
  fetch('./export/polio-is-back-vertical.mp4',{method:'HEAD'}).then(r=>{
    if (r.ok) document.getElementById('download').classList.add('show');
  }).catch(()=>{});
}
boot().catch(error=>{
  console.error(error);
  if (!exportMode) document.querySelector('.player-label').textContent=`Could not load animation: ${error.message}`;
});

import { C, W, H, clamp, seg, eob } from './lib.js';

export const CAP = Object.freeze({ y: 1445, size: 150, maxWidth: 958, outline: 27 });

export function parseCaption(source) {
  return source.trim().split(/\s+/).map(token => ({
    word: token.replace(/^\*/, ''), yellow: token.startsWith('*'),
  }));
}

// English is a translation of the spoken Hinglish; chunks have authored cue
// times, not unreliable spelling-based matches across two languages.
export function activeCaption(shot, localTime) {
  if (!shot?.caps?.length) return null;
  let found = null;
  for (const cap of shot.caps) {
    if (localTime + 1e-5 >= cap.at) found = cap;
    else break;
  }
  return found;
}

export function drawCaption(g, shot, localTime, enabled = true) {
  if (!enabled) return;
  const cap = activeCaption(shot, localTime);
  if (!cap) return;
  const words = parseCaption(cap.text);
  const elapsed = Math.max(0, localTime - cap.at);
  const pop = 1 + .15 * (1 - eob(seg(elapsed, 0, .20)));
  let size = CAP.size, widths, total;
  do {
    g.font = `900 ${size}px Inter, Arial, sans-serif`;
    widths = words.map(({ word }) => g.measureText(word).width);
    const space = g.measureText(' ').width;
    total = widths.reduce((a, b) => a + b, 0) + space * (words.length - 1);
    if (total <= CAP.maxWidth / pop || size <= 72) break;
    size -= 2;
  } while (true);
  const space = g.measureText(' ').width;
  let cursor = -total / 2;
  g.save(); g.translate(W / 2, CAP.y); g.scale(pop, pop);
  g.textAlign = 'left'; g.textBaseline = 'middle';
  g.lineJoin = 'round'; g.miterLimit = 2;
  for (let i = 0; i < words.length; i++) {
    const { word, yellow } = words[i];
    const x = cursor, y = 0;
    // Flat offset shadow and broad ink outline; no glow or blur.
    g.strokeStyle = C.ink; g.lineWidth = CAP.outline + 5;
    g.strokeText(word, x + 7, y + 9);
    g.strokeStyle = C.ink; g.lineWidth = CAP.outline;
    g.strokeText(word, x, y);
    g.fillStyle = yellow ? C.yellow : C.white;
    g.fillText(word, x, y);
    cursor += widths[i] + space;
  }
  g.restore();
}

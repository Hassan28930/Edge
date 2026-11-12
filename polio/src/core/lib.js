// All artwork is drawn in a 1080 x 1920 logical coordinate system.
// No raster art, gradients, shadows, filters, or stateful animation.
export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const C = Object.freeze({
  bg: '#F4F1EA', paper: '#FFFDF7', ink: '#1A1A1E', muted: '#68646A',
  skin: '#E8B89A', skinDark: '#D7997F', hair: '#242327',
  organ: '#E57A8A', organLight: '#F4B0B8', organDark: '#B9556A',
  red: '#D62839', redPale: '#F7D9DC', yellow: '#FFD43B', yellowPale: '#FFF0B4',
  xray: '#4FD1E8', xrayLight: '#D9F5F7', xrayDark: '#198BA1',
  stone: '#D7D1C6', stoneDark: '#A9A296', white: '#FFFFFF',
});

export const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const eo = t => 1 - Math.pow(1 - clamp(t), 3);
export const eio = t => { t = clamp(t); return t * t * (3 - 2 * t); };
export const eob = t => { t = clamp(t); return 1 + 2.1 * (t - 1) ** 3 + 1.1 * (t - 1) ** 2; };

export function box(g, x, y, w, h, color) {
  g.fillStyle = color; g.fillRect(x, y, w, h);
}
export function rr(g, x, y, w, h, r, color, border = null, bw = 0) {
  g.beginPath(); g.roundRect(x, y, w, h, Math.min(r, w / 2, h / 2));
  if (color) { g.fillStyle = color; g.fill(); }
  if (border) { g.strokeStyle = border; g.lineWidth = bw; g.stroke(); }
}
export function circle(g, x, y, r, color, border = null, bw = 0) {
  g.beginPath(); g.arc(x, y, Math.max(0.01, r), 0, Math.PI * 2);
  if (color) { g.fillStyle = color; g.fill(); }
  if (border) { g.strokeStyle = border; g.lineWidth = bw; g.stroke(); }
}
export function ell(g, x, y, rx, ry, color, border = null, bw = 0) {
  g.beginPath(); g.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), 0, 0, Math.PI * 2);
  if (color) { g.fillStyle = color; g.fill(); }
  if (border) { g.strokeStyle = border; g.lineWidth = bw; g.stroke(); }
}
export function line(g, x1, y1, x2, y2, color, w = 8) {
  g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2);
  g.lineWidth = w; g.lineCap = 'round'; g.strokeStyle = color; g.stroke();
}
export function path(g, points, color, border = null, bw = 0) {
  g.beginPath(); g.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) g.lineTo(points[i][0], points[i][1]);
  g.closePath();
  if (color) { g.fillStyle = color; g.fill(); }
  if (border) { g.strokeStyle = border; g.lineWidth = bw; g.lineJoin = 'round'; g.stroke(); }
}
export function arc(g, x, y, r, a0, a1, color, w = 8) {
  g.beginPath(); g.arc(x, y, r, a0, a1);
  g.strokeStyle = color; g.lineWidth = w; g.lineCap = 'round'; g.stroke();
}
export function text(g, str, x, y, size, color = C.ink, align = 'center', weight = 900) {
  g.fillStyle = color; g.font = `${weight} ${size}px Inter, Arial, sans-serif`;
  g.textAlign = align; g.textBaseline = 'middle';
  g.fillText(str, x, y);
}
export function label(g, str, x, y, opts = {}) {
  const { bg = C.ink, fg = C.paper, size = 27, pad = 23, h = 62, border = null } = opts;
  g.font = `900 ${size}px Inter, Arial, sans-serif`;
  const w = g.measureText(str).width + pad * 2;
  rr(g, x - w / 2, y - h / 2, w, h, h / 2, bg, border, border ? 4 : 0);
  text(g, str, x, y + 1, size, fg);
  return w;
}
export function arrow(g, x, y, length, angle, color = C.ink, width = 12) {
  const x2 = x + Math.cos(angle) * length, y2 = y + Math.sin(angle) * length;
  line(g, x, y, x2, y2, color, width);
  const a = angle + Math.PI * 0.82, b = angle - Math.PI * 0.82;
  line(g, x2, y2, x2 + Math.cos(a) * 31, y2 + Math.sin(a) * 31, color, width);
  line(g, x2, y2, x2 + Math.cos(b) * 31, y2 + Math.sin(b) * 31, color, width);
}
export function dotted(g, x1, y1, x2, y2, color = C.ink, r = 8, count = 12) {
  for (let i = 0; i <= count; i++) {
    const p = i / count; circle(g, lerp(x1, x2, p), lerp(y1, y2, p), r, color);
  }
}
export function burst(g, x, y, r, color = C.yellow, rays = 10, amount = 1) {
  for (let i = 0; i < rays; i++) {
    const a = i * Math.PI * 2 / rays;
    line(g, x + Math.cos(a) * r * .7, y + Math.sin(a) * r * .7,
      x + Math.cos(a) * r * amount, y + Math.sin(a) * r * amount, color, 17);
  }
}
export function cross(g, x, y, s, color = C.red, w = 18) {
  line(g, x - s, y - s, x + s, y + s, color, w);
  line(g, x + s, y - s, x - s, y + s, color, w);
}
export function background(g, color = C.bg) {
  // Deliberately exceeds the frame, including during the camera push.
  box(g, -500, -500, W + 1000, H + 1000, color);
}

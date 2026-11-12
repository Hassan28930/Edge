import { C, clamp, lerp, seg, eo, rr, box, circle, ell, line, path, arc, text, label, burst, cross, arrow } from './lib.js';

// A deliberately small, reusable vector component set. Every component accepts a
// CanvasRenderingContext2D, draws only flat fills, and has no frame-to-frame state.
export function man(g, x, y, s = 1, opts = {}) {
  const { xray = false, child = false, eyes = 'normal', mouth = 'smile',
    arm = 'down', look = 0, shirt = child ? C.yellow : C.organ,
    pulse = 0, blink = false, holding = null } = opts;
  g.save(); g.translate(x, y); g.scale(s, s);
  const limb = xray ? C.xrayDark : C.skin;
  const limbShade = xray ? C.xray : C.skinDark;
  const fabric = xray ? C.xrayDark : shirt;
  ell(g, 0, 610, 170, 23, C.stone);
  // Legs and shoes.
  path(g, [[-140, 250], [140, 250], [134, 525], [37, 525], [3, 370], [-24, 525], [-130, 525]], xray ? C.xrayDark : C.ink);
  line(g, -85, 408, -89, 548, limb, 62);
  line(g, 82, 409, 86, 548, limb, 62);
  rr(g, -155, 537, 148, 59, 28, xray ? C.xrayDark : C.ink);
  rr(g, 18, 537, 148, 59, 28, xray ? C.xrayDark : C.ink);
  // Arms are both x-ray when x-ray mode is active (not skin-tone sleeves).
  const rhand = arm === 'up' ? [277, -331] : arm === 'point' ? [295, -28]
    : arm === 'hold' ? [270, 27] : arm === 'protect' ? [75, 110] : [245, 255];
  line(g, -155, -112, -254, 163, limb, 89);
  circle(g, -254, 163, 43, limbShade);
  line(g, 155, -110, rhand[0], rhand[1], limb, 88);
  circle(g, rhand[0], rhand[1], 43, limbShade);
  if (arm === 'point') {
    line(g, rhand[0] + 9, rhand[1] - 23, rhand[0] + 82, rhand[1] - 81, limb, 25);
  }
  if (arm === 'up') {
    line(g, rhand[0] + 7, rhand[1] - 31, rhand[0] + 9, rhand[1] - 116, limb, 25);
  }
  if (holding === 'vial') vial(g, rhand[0] + 4, rhand[1] - 85, .32, { labelText: '' });
  // Torso and neck.
  rr(g, -52, -209, 104, 91, 26, limb);
  path(g, [[-165, -155], [155, -155], [192, 246], [125, 287], [-126, 287], [-192, 246]], fabric);
  if (!xray) {
    path(g, [[-135, -145], [-38, -145], [-65, 244], [-144, 244]], child ? '#EAC431' : C.organDark);
    path(g, [[60, -140], [145, -142], [156, 210], [112, 242]], child ? C.yellowPale : C.organLight);
    arc(g, 0, -143, 79, .17, Math.PI - .17, C.ink, 11);
  } else {
    // A single coherent x-ray body. The head below stays normal, as in the style guide.
    rr(g, -18, -116, 36, 322, 18, C.xrayLight);
    for (let i = 0; i < 6; i++) {
      arc(g, 0, -78 + i * 37, 72 - i * 3, .10, Math.PI - .10, C.xrayLight, 13);
    }
    ell(g, -17, 119, 80, 73, C.organ);
    ell(g, -34, 104, 22 + pulse * 12, 13 + pulse * 8, C.organLight);
    line(g, -121, 326, -101, 465, C.xrayLight, 18);
    line(g, 107, 326, 102, 465, C.xrayLight, 18);
  }
  // Head. Ink hair, dot eyes with highlights, soft expressions.
  ell(g, 0, -371, 154, 164, C.skin);
  ell(g, -145, -361, 28, 47, C.skinDark);
  ell(g, 145, -361, 28, 47, C.skinDark);
  g.beginPath();
  g.moveTo(-152, -409);
  g.bezierCurveTo(-143, -556, 105, -568, 154, -421);
  g.bezierCurveTo(100, -467, 72, -461, 35, -496);
  g.bezierCurveTo(-5, -458, -70, -492, -152, -409);
  g.closePath(); g.fillStyle = C.hair; g.fill();
  if (child) {
    path(g, [[-51, -508], [-14, -569], [9, -510]], C.hair);
    path(g, [[17, -510], [55, -562], [55, -480]], C.hair);
  }
  if (blink || eyes === 'closed') {
    arc(g, -56, -366, 14, 0, Math.PI, C.ink, 8);
    arc(g, 56, -366, 14, 0, Math.PI, C.ink, 8);
  } else {
    ell(g, -55 + look * 8, -369, eyes === 'wide' ? 18 : 13, eyes === 'wide' ? 24 : 17, C.ink);
    ell(g, 55 + look * 8, -369, eyes === 'wide' ? 18 : 13, eyes === 'wide' ? 24 : 17, C.ink);
    circle(g, -60 + look * 8, -375, 5, C.paper);
    circle(g, 50 + look * 8, -375, 5, C.paper);
  }
  if (eyes === 'wide') {
    line(g, -83, -419, -31, -425, C.ink, 9);
    line(g, 31, -425, 83, -419, C.ink, 9);
  } else {
    line(g, -83, -411, -33, -414, C.ink, 7);
    line(g, 33, -414, 83, -411, C.ink, 7);
  }
  if (mouth === 'o') ell(g, 0, -290, 24, 32, C.ink);
  else if (mouth === 'flat') line(g, -26, -289, 27, -289, C.ink, 8);
  else if (mouth === 'smirk') arc(g, 4, -300, 42, .05, 1.76, C.ink, 8);
  else arc(g, 0, -325, 50, .18, Math.PI - .18, C.ink, 8);
  g.restore();
}

export function smallPerson(g, x, y, s = 1, opts = {}) {
  const { color = C.organ, dark = false, shielded = false, child = true } = opts;
  g.save(); g.translate(x, y); g.scale(s, s);
  const ink = dark ? C.paper : C.ink;
  ell(g, 0, 210, 87, 12, dark ? '#39383C' : C.stone);
  line(g, -38, 119, -40, 198, ink, 22);
  line(g, 38, 119, 40, 198, ink, 22);
  line(g, -69, -1, -89, 111, C.skin, 30);
  line(g, 69, -1, 89, 111, C.skin, 30);
  rr(g, -68, -34, 136, 158, 36, color);
  ell(g, 0, -113, child ? 67 : 74, child ? 73 : 80, C.skin);
  arc(g, 0, -122, 60, Math.PI * 1.05, Math.PI * 1.91, C.hair, 22);
  circle(g, -22, -111, 6, C.ink); circle(g, 22, -111, 6, C.ink);
  arc(g, 0, -103, 21, .25, Math.PI - .25, C.ink, 5);
  if (shielded) { circle(g, 105, -173, 29, C.yellow); text(g, '✓', 105, -177, 34, C.ink); }
  g.restore();
}

export function virus(g, x, y, r = 115, opts = {}) {
  const { danger = false, weak = false, rot = 0, scale = 1 } = opts;
  const fill = danger ? C.red : weak ? C.organLight : C.organ;
  const dark = danger ? '#A91E2E' : C.organDark;
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(scale, scale);
  for (let i = 0; i < 11; i++) {
    const a = i * Math.PI * 2 / 11;
    line(g, Math.cos(a) * r * .72, Math.sin(a) * r * .72,
      Math.cos(a) * r * 1.2, Math.sin(a) * r * 1.2, dark, r * .13);
    circle(g, Math.cos(a) * r * 1.25, Math.sin(a) * r * 1.25, r * .13, fill);
  }
  circle(g, 0, 0, r, fill, C.ink, Math.max(3, r * .045));
  circle(g, -r * .22, -r * .29, r * .23, danger ? '#EE6570' : C.organLight);
  circle(g, r * .35, r * .14, r * .12, dark);
  circle(g, -r * .27, r * .4, r * .09, dark);
  circle(g, r * .29, -r * .31, r * .07, dark);
  g.restore();
}

export function shield(g, x, y, s = 1, opts = {}) {
  const { fill = C.yellow, stroke = C.ink, check = true } = opts;
  g.save(); g.translate(x, y); g.scale(s, s);
  path(g, [[0,-195],[158,-130],[149,47],[108,149],[0,214],[-108,149],[-149,47],[-158,-130]], fill, stroke, 15);
  if (check) { line(g, -70, 1, -15, 58, C.ink, 23); line(g, -15, 58, 80, -54, C.ink, 23); }
  g.restore();
}

export function vial(g, x, y, s = 1, opts = {}) {
  const { labelText = 'nOPV2', tilt = 0 } = opts;
  g.save(); g.translate(x, y); g.rotate(tilt); g.scale(s, s);
  rr(g, -97, -185, 194, 309, 28, C.paper, C.ink, 12);
  rr(g, -96, 20, 192, 99, 20, C.organLight);
  rr(g, -110, -240, 220, 63, 12, C.ink);
  rr(g, -76, -260, 152, 29, 8, C.stoneDark);
  line(g, -54, -155, -54, -42, C.stone, 10);
  if (labelText) {
    rr(g, -78, -52, 156, 110, 14, C.yellow);
    text(g, labelText, 0, 2, 35, C.ink);
  }
  g.restore();
}

export function drop(g, x, y, size = 30, color = C.organ) {
  g.beginPath(); g.moveTo(x, y - size * 1.4);
  g.bezierCurveTo(x + size * .8, y - size * .2, x + size, y + size, x, y + size);
  g.bezierCurveTo(x - size, y + size, x - size * .8, y - size * .2, x, y - size * 1.4);
  g.fillStyle = color; g.fill();
  circle(g, x - size * .24, y + size * .1, size * .14, C.paper);
}

export function clinic(g, x, y, s = 1) {
  g.save(); g.translate(x, y); g.scale(s, s);
  rr(g, -165, -145, 330, 294, 13, C.paper, C.ink, 12);
  path(g, [[-202,-150],[0,-257],[202,-150]], C.yellow, C.ink, 12);
  rr(g, -50, 30, 100, 118, 10, C.stone, C.ink, 9);
  rr(g, -131, -49, 76, 83, 9, C.organLight);
  rr(g, 55, -49, 76, 83, 9, C.organLight);
  rr(g, -22, -126, 44, 120, 5, C.ink);
  rr(g, -60, -88, 120, 44, 5, C.ink);
  g.restore();
}

export function calendar(g, x, y, s = 1, day = 'WEEK', sub = '03') {
  g.save(); g.translate(x, y); g.scale(s, s);
  rr(g, -160, -199, 320, 363, 24, C.paper, C.ink, 12);
  rr(g, -160, -199, 320, 87, 18, C.organ);
  rr(g, -95, -231, 27, 76, 13, C.ink);
  rr(g, 68, -231, 27, 76, 13, C.ink);
  text(g, day, 0, -24, day.length > 4 ? 55 : 75, C.ink);
  text(g, sub, 0, 88, 73, C.red);
  g.restore();
}

export function clock(g, x, y, r = 150, hand = 0) {
  circle(g, x, y, r, C.paper, C.ink, 16);
  for (let i = 0; i < 12; i++) {
    const a = i * Math.PI / 6 - Math.PI / 2;
    line(g, x + Math.cos(a) * r * .79, y + Math.sin(a) * r * .79,
      x + Math.cos(a) * r * .88, y + Math.sin(a) * r * .88, C.ink, 8);
  }
  line(g, x, y, x + Math.cos(hand) * r * .58, y + Math.sin(hand) * r * .58, C.red, 14);
  line(g, x, y, x - Math.sin(hand) * r * .35, y + Math.cos(hand) * r * .35, C.ink, 11);
  circle(g, x, y, 13, C.ink);
}

export function warning(g, x, y, s = 1) {
  g.save(); g.translate(x, y); g.scale(s, s);
  path(g, [[0,-155],[153,130],[-153,130]], C.yellow, C.ink, 16);
  rr(g, -13, -62, 26, 112, 13, C.red);
  circle(g, 0, 85, 17, C.red);
  g.restore();
}

export function globe(g, x, y, r = 315, spin = 0) {
  circle(g, x, y, r, C.paper, C.ink, 13);
  g.save(); g.beginPath(); g.arc(x, y, r - 10, 0, Math.PI * 2); g.clip();
  // Stylized continents; deliberately not a political border map.
  g.save(); g.translate(x + Math.sin(spin) * 13, y);
  path(g, [[-275,-159],[-217,-219],[-141,-193],[-112,-140],[-156,-79],[-111,-17],[-151,69],[-231,41],[-253,-54]], C.stone);
  path(g, [[-131,90],[-52,138],[-8,216],[-71,316],[-134,274],[-169,180]], C.stone);
  path(g, [[-16,-191],[73,-226],[202,-187],[251,-132],[199,-60],[125,-60],[142,34],[96,73],[66,191],[1,201],[-42,91],[2,-32],[-59,-93]], C.stone);
  path(g, [[212,172],[297,197],[321,264],[258,278],[199,230]], C.stone);
  g.restore();
  for (let i = -2; i <= 2; i++) arc(g, x, y, r * (1 - Math.abs(i) * .13), -1.42, 1.42, '#E9E2D6', 5);
  line(g, x - r, y, x + r, y, '#E9E2D6', 5);
  g.restore();
  circle(g, x, y, r, null, C.ink, 13);
}

export function route(g, fromX, fromY, toX, toY, progress = 1, color = C.ink) {
  g.save(); g.beginPath(); g.moveTo(fromX, fromY);
  g.bezierCurveTo(fromX + 180, fromY - 195, toX - 173, toY + 157, toX, toY);
  g.setLineDash([17, 22]); g.lineWidth = 14; g.strokeStyle = color; g.stroke(); g.setLineDash([]);
  if (progress > 0) {
    const x = lerp(fromX, toX, eo(progress)), y = lerp(fromY, toY, eo(progress));
    circle(g, x, y, 21, C.yellow, C.ink, 7);
  }
  g.restore();
}

export function tinyHeart(g, x, y, s = 1, color = C.organ) {
  g.save(); g.translate(x, y); g.scale(s, s);
  g.beginPath(); g.moveTo(0, 81);
  g.bezierCurveTo(-147, -1, -69, -119, 0, -49);
  g.bezierCurveTo(69, -119, 147, -1, 0, 81);
  g.fillStyle = color; g.fill(); g.restore();
}

export function star(g, x, y, r = 37, color = C.yellow) {
  const p = [];
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + i * Math.PI / 5, d = i % 2 ? r * .49 : r;
    p.push([x + Math.cos(a) * d, y + Math.sin(a) * d]);
  }
  path(g, p, color);
}

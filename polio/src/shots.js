import { C, W, H, clamp, lerp, seg, eo, eio, eob, background, box, rr, circle, ell, line, path, arc, text, label, arrow, dotted, burst, cross } from './core/lib.js';
import * as K from './core/kit.js';

// Each scene is a pure function of time. Seeking, rendering frame 187 before
// frame 2, and re-rendering the same frame produce identical pixels.
function base(g, color = C.bg) {
  background(g, color);
  circle(g, 1130, 170, 300, color === C.ink ? '#28272B' : C.paper);
  circle(g, -250, 1210, 430, color === C.ink ? '#28272B' : '#ECE7DD');
}
function xray(g, t) {
  background(g, C.xrayLight);
  rr(g, 72, 375, 936, 877, 44, '#C4EEF3', C.xrayDark, 10);
  for (let i = 0; i < 5; i++) line(g, 94, 444 + i * 155, 987, 444 + i * 155, '#B5E6EC', 5);
  box(g, 85, 389 + ((t * 145) % 770), 912, 10, '#A5E1E9');
}
function dark(g) {
  background(g, C.ink);
  circle(g, -190, 750, 420, '#29282D');
  circle(g, 1070, 210, 300, '#29282D');
}
function heading(g, name, number, darkMode = false) {
  const c = darkMode ? C.paper : C.ink;
  line(g, 80, 271, 1000, 271, darkMode ? '#4E4B50' : C.stone, 5);
  text(g, name, 86, 323, 29, c, 'left');
  text(g, number, 994, 323, 29, darkMode ? C.yellow : C.red, 'right');
}
function pop(g, x, y, lt, duration, draw) {
  const p = eob(seg(lt, 0, duration));
  g.save(); g.translate(x, y); g.scale(p, p); g.translate(-x, -y); draw(); g.restore();
}
function wave(g, x, y, r, color, count = 3, t = 0) {
  for (let i = 0; i < count; i++) {
    const rad = r * (1 + i * .26 + Math.sin(t * 2 - i) * .018);
    circle(g, x, y, rad, null, color, 8 - i * 1.5);
  }
}
function littlePin(g, x, y, c = C.red) {
  circle(g, x, y, 22, c, C.ink, 6);
  path(g, [[x - 12,y + 12],[x,y + 40],[x + 12,y + 12]], c);
  circle(g, x, y, 6, C.paper);
}

const scenes = {
  hook(g, lt, d, t) {
    base(g);
    heading(g, 'THE POLIO QUESTION', '01 / 30');
    circle(g, 804, 778, 318, C.organLight);
    circle(g, 804, 778, 274, C.redPale);
    const q = 1 + Math.sin(t * 3) * .025;
    pop(g, 789, 790, lt, .54, () => K.virus(g, 793, 775 + Math.sin(t * 2) * 17, 139, { danger:true, rot:t * .13, scale:q }));
    K.man(g, 308, 875, .66, { eyes:lt > .65 ? 'wide':'normal', mouth:lt > 1 ? 'o':'flat', arm:'point', look:1 });
    text(g, '?', 820, 472, 180, C.yellow);
    burst(g, 802, 777, 270, C.red, 9, .97);
    label(g, 'WHY NOW?', 548, 480, { bg:C.ink, fg:C.paper, size:27 });
  },
  globe(g, lt, d, t) {
    base(g);
    heading(g, 'THE GLOBAL EFFORT', '02 / 30');
    K.globe(g, 540, 828, 354, t * .19);
    const vanish = eo(seg(lt, .35, 1.85));
    for (let i = 0; i < 9; i++) {
      const a = i * 2.4, x = 540 + Math.cos(a) * 230, y = 825 + Math.sin(a) * 240;
      g.globalAlpha = Math.max(0, 1 - vanish * (1 + (i % 3) * .12));
      circle(g, x, y, 17, C.organ);
    }
    g.globalAlpha = 1;
    littlePin(g, 635, 713); littlePin(g, 681, 764);
    label(g, 'WILD POLIO', 540, 399, { bg:C.ink, fg:C.paper, size:31 });
    arrow(g, 831, 554, 85, -.65, C.red, 13);
  },
  twoCountries(g, lt, d) {
    base(g);
    heading(g, 'WHERE WILD POLIO REMAINS', '03 / 30');
    circle(g, 545, 813, 396, C.yellowPale);
    text(g, '02', 540, 571, 230, C.ink);
    line(g, 540, 687, 540, 1032, C.ink, 9);
    pop(g, 291, 824, lt, .46, () => {
      path(g, [[200,729],[311,678],[391,753],[360,875],[276,914],[199,840]], C.organLight, C.ink, 12);
      littlePin(g, 299, 770);
    });
    pop(g, 781, 822, lt - .25, .46, () => {
      path(g, [[675,697],[802,729],[864,820],[811,950],[746,890],[692,873]], C.organLight, C.ink, 12);
      littlePin(g, 770, 796);
    });
    label(g, 'AFGHANISTAN', 281, 1070, { size:28, bg:C.paper, fg:C.ink, border:C.ink });
    label(g, 'PAKISTAN', 794, 1070, { size:28, bg:C.paper, fg:C.ink, border:C.ink });
  },
  conflict(g, lt, d, t) {
    dark(g);
    heading(g, 'BARRIER  /  01', '04 / 30', true);
    K.smallPerson(g, 217, 908, .66, { color:C.yellow, dark:true });
    K.clinic(g, 842, 906, .52);
    K.route(g, 241, 1017, 810, 1055, .22, '#B1ABA5');
    // A flat, symbolic broken route, not imagery of injured people.
    path(g, [[462,440],[550,529],[473,639],[580,710],[478,817],[593,881],[488,1014],[564,1137],[463,1182]], C.red, C.paper, 12);
    cross(g, 543, 860, 63, C.ink, 23);
    label(g, 'ACCESS BLOCKED', 560, 449, { bg:C.red, fg:C.paper, size:29 });
    for (let i = 0; i < 3; i++) line(g, 64+i*26, 593, 210+i*26, 593, C.red, 9);
  },
  clinic(g, lt, d, t) {
    base(g);
    heading(g, 'BARRIER  /  02', '05 / 30');
    circle(g, 792, 696, 248, C.yellowPale);
    K.clinic(g, 793, 745, .67);
    K.smallPerson(g, 224, 982, .69, { color:C.organ });
    g.save(); g.beginPath(); g.moveTo(228,1070);
    g.bezierCurveTo(351,1111,455,866,568,961);
    g.bezierCurveTo(628,1012,720,926,782,925);
    g.setLineDash([14,21]); g.lineWidth = 13; g.strokeStyle = C.ink; g.stroke(); g.setLineDash([]); g.restore();
    pop(g, 535, 943, lt-.45, .38, () => cross(g, 535, 943, 52, C.red, 21));
    label(g, 'TOO FAR TO REACH', 533, 429, { bg:C.ink, fg:C.paper, size:28 });
  },
  coverage(g, lt, d, t) {
    base(g);
    heading(g, 'IMMUNISATION COVERAGE', '06 / 30');
    arc(g, 539, 802, 323, -2.65, 1.68, C.yellow, 60);
    arc(g, 539, 802, 323, 2.60, 3.55, C.yellow, 60);
    arc(g, 539, 802, 323, 1.78, 2.45, C.red, 17);
    K.smallPerson(g, 535, 833, .74, { color:C.organ });
    for (let i = 0; i < 5; i++) {
      const a = -2.75 + i * .89;
      circle(g, 539 + Math.cos(a) * 324, 802 + Math.sin(a) * 324, 22, C.ink);
    }
    label(g, 'THE MISSED CHILD', 540, 418, { bg:C.ink, fg:C.paper, size:29 });
    K.warning(g, 821, 1007, .40);
  },
  fragile(g, lt, d, t) {
    base(g);
    heading(g, 'THE WARNING SIGNS', '07 / 30');
    wave(g, 533, 755, 136, C.stoneDark, 4, t);
    circle(g, 533, 755, 24, C.red);
    arrow(g, 710, 544, 74, 2.3, C.red, 14);
    label(g, 'RARE DETECTION', 543, 454, { bg:C.red, fg:C.paper, size:28 });
    rr(g, 160, 1102, 760, 39, 19, C.stone);
    rr(g, 160, 1102, lerp(674, 460, eo(seg(lt,.2,1.25))), 39, 19, C.yellow);
    cross(g, 796, 1120, 36, C.red, 14);
    text(g, 'PROGRESS IS NOT PERMANENT', 540, 1210, 29, C.muted);
  },
  problem(g, lt, d, t) {
    dark(g);
    heading(g, 'A SECOND THREAT', '08 / 30', true);
    circle(g, 530, 806, 316, '#373036');
    pop(g, 540, 801, lt, .48, () => K.warning(g, 540, 780, 1.43));
    K.virus(g, 829, 1056, 66, { weak:true, rot:t*.17 });
    text(g, 'NOT THE SAME VIRUS', 540, 1177, 35, C.paper);
  },
  gaps(g, lt, d, t) {
    base(g);
    heading(g, 'LOW IMMUNITY', '09 / 30');
    for (let i = 0; i < 8; i++) {
      if (i === 1) continue;
      const a = (i / 8) * Math.PI * 2 - Math.PI / 2;
      const x = 540 + Math.cos(a) * 323, y = 800 + Math.sin(a) * 302;
      circle(g, x, y, 61, C.yellowPale, C.ink, 8);
      K.smallPerson(g, x, y + 22, .23, { color:C.yellow });
    }
    K.virus(g, 537, 801, 109, { weak:true, rot:t*.19 });
    circle(g, 764, 581, 67, C.redPale, C.red, 10);
    cross(g, 764, 581, 27, C.red, 12);
    arrow(g, 660, 649, 83, -.5, C.red, 13);
    label(g, 'A GAP IN THE RING', 548, 1180, { bg:C.ink, fg:C.paper, size:27 });
  },
  oral(g, lt, d, t) {
    xray(g,t);
    heading(g, 'INSIDE THE BODY', '10 / 30');
    K.man(g, 439, 875, .64, { xray:true, mouth:'o', eyes:'wide', look:1 });
    K.vial(g, 796, 602, .75, { labelText:'OPV', tilt:-.12 });
    const p = eo(seg(lt,.28,1.56));
    K.drop(g, lerp(733,439,p), lerp(705,690,p) - Math.sin(p*Math.PI)*93, 16 + (1-p)*19, C.organ);
    label(g, 'WEAKENED VIRUS', 739, 1066, { bg:C.ink, fg:C.paper, size:26 });
    arrow(g, 703, 934, 128, 2.60, C.organDark, 11);
  },
  spreads(g, lt, d, t) {
    base(g);
    heading(g, 'WHEN IMMUNITY IS LOW', '11 / 30');
    const xs = [202, 425, 651, 874];
    for (let i=0; i<xs.length; i++) {
      K.smallPerson(g, xs[i], 901, .70, { color:i===0 ? C.organLight : C.stone });
      if (i>0) {
        const p = seg(lt, .22+(i-1)*.48, .64+(i-1)*.48);
        if (p>0) K.virus(g, lerp(xs[i-1]+90,xs[i]-91,eo(p)), 745+Math.sin(p*Math.PI)*-56, 20, { weak:true, rot:t*.3 });
      }
    }
    dotted(g, 265, 1126, 815, 1126, C.red, 7, 18);
    label(g, 'CIRCULATION', 541, 440, { bg:C.ink, fg:C.paper, size:29 });
  },
  mutates(g, lt, d, t) {
    xray(g,t);
    heading(g, 'A RARE REVERSION', '12 / 30');
    K.man(g, 541, 856, .63, { xray:true, eyes:'wide', mouth:'o' });
    const p = eo(seg(lt,.60,1.33));
    K.virus(g, 260, 477, 66, { weak:true, rot:t*.16 });
    arrow(g, 366, 478, 315, 0, C.ink, 13);
    K.virus(g, 816, 477, 74, { danger:p>.46, weak:p<=.46, rot:t*.22, scale:lerp(.72,1, p) });
    if (lt > 1.25) {
      circle(g, 541, 970, 72 + Math.sin(t*8)*12, null, C.red, 11);
      K.warning(g, 829, 951, .45);
    }
    label(g, 'RARE, BUT REAL', 548, 1159, { bg:C.red, fg:C.paper, size:26 });
  },
  comparison(g, lt, d, t) {
    base(g);
    heading(g, 'THE CASE COUNT', '13 / 30');
    text(g, 'VACCINE-DERIVED', 538, 459, 53, C.ink);
    line(g, 176, 1102, 900, 1102, C.ink, 11);
    rr(g, 241, 1100 - 260*eo(seg(lt,0,.58)), 199, 260*eo(seg(lt,0,.58)), 12, C.stoneDark);
    rr(g, 617, 1100 - 504*eo(seg(lt,.2,.82)), 199, 504*eo(seg(lt,.2,.82)), 12, C.organ);
    text(g, 'WILD', 339, 1173, 35, C.ink);
    text(g, 'VACCINE-', 716, 1158, 31, C.ink);
    text(g, 'DERIVED', 716, 1200, 31, C.ink);
    arrow(g, 516, 824, 68, -.55, C.red, 12);
    label(g, 'MORE CASES', 715, 550, { bg:C.red, fg:C.paper, size:27 });
  },
  incubation(g, lt, d, t) {
    base(g);
    heading(g, 'A SLOW-MOVING VIRUS', '14 / 30');
    circle(g, 539, 806, 394, C.yellowPale);
    K.calendar(g, 329, 855, .86, 'WEEK', '01');
    K.clock(g, 764, 835, 187, -Math.PI/2 + t * 1.6);
    arrow(g, 488, 1031, 110, 0, C.red, 12);
    label(g, 'LONG INCUBATION', 541, 433, { bg:C.ink, fg:C.paper, size:27 });
  },
  undetected(g, lt, d, t) {
    base(g);
    heading(g, 'BEFORE ANYONE KNOWS', '15 / 30');
    for (let i=0; i<4; i++) {
      const x = 171 + i*240;
      K.smallPerson(g, x, 859, .65, { color:i===0?C.organLight:C.stone });
      if (i < 3) {
        const p=seg(lt,i*.45,(i+1)*.45);
        circle(g, lerp(x+57,x+178,eo(p)), 747+Math.sin(p*Math.PI)*-62, 16, C.red);
      }
    }
    text(g, '?', 539, 568, 158, C.red);
    label(g, 'NO OBVIOUS SIGN', 544, 1175, { bg:C.ink, fg:C.paper, size:27 });
  },
  unvaccinated(g, lt, d, t) {
    base(g);
    heading(g, 'WEEKS WITHOUT DETECTION', '16 / 30');
    for (let i=0; i<3; i++) {
      K.calendar(g, 244 + 294*i, 661, .48, 'WEEK', `0${i+1}`);
      K.smallPerson(g, 244 + 294*i, 1030, .45, { color:i===0?C.organ:C.stone });
      if (i<2) arrow(g, 340+294*i, 1037, 97, 0, C.red, 12);
    }
    label(g, 'UNVACCINATED', 540, 1219, { bg:C.red, fg:C.paper, size:28 });
  },
  goodNews(g, lt, d, t) {
    base(g);
    heading(g, 'THE TURNING POINT', '17 / 30');
    circle(g, 538, 822, 327, C.yellowPale);
    burst(g, 538, 823, 428, C.yellow, 12, 1);
    pop(g, 541, 794, lt, .55, () => K.vial(g, 541, 818, 1.36, { labelText:'nOPV2', tilt:-.07 }));
    K.star(g, 303, 558, 43); K.star(g, 801, 1074, 49);
    label(g, 'A BETTER TOOL', 538, 433, { bg:C.ink, fg:C.paper, size:28 });
  },
  stable(g, lt, d, t) {
    base(g);
    heading(g, 'A MORE STABLE VACCINE', '18 / 30');
    K.vial(g, 340, 835, 1.11, { labelText:'nOPV2' });
    arrow(g, 466, 788, 119, 0, C.ink, 13);
    K.shield(g, 767, 826, 1.16, { fill:C.yellowPale });
    K.virus(g, 766, 808, 74, { weak:true, rot:t*.12 });
    K.star(g, 712, 610, 27); K.star(g, 885, 1010, 33);
    label(g, 'LESS LIKELY TO REVERT', 541, 439, { bg:C.ink, fg:C.paper, size:26 });
  },
  doses(g, lt, d, t) {
    base(g);
    heading(g, 'A MASSIVE ROLLOUT', '19 / 30');
    text(g, '2', 537, 614, 266, C.ink);
    rr(g, 251, 731, 578, 119, 35, C.yellow);
    text(g, 'BILLION', 540, 792, 112, C.ink);
    for (let i=0; i<7; i++) K.vial(g, 177 + i*120, 1040+Math.sin(t*2+i)*5, .35, { labelText:'' });
    label(g, 'DOSES GIVEN', 541, 416, { bg:C.ink, fg:C.paper, size:30 });
  },
  warZones(g, lt, d, t) {
    dark(g);
    heading(g, 'THE LAST MILE', '20 / 30', true);
    K.man(g, 248, 929, .48, { shirt:C.yellow, mouth:'flat', arm:'hold', holding:'vial' });
    K.smallPerson(g, 858, 1020, .50, { color:C.organ, dark:true });
    K.route(g, 361, 1109, 817, 1109, eo(seg(lt,.3,1.9)), C.yellow);
    path(g, [[515,532],[553,648],[499,744],[565,828],[531,913]], C.red, C.paper, 11);
    label(g, 'WAR ZONE', 560, 469, { bg:C.red, fg:C.paper, size:28 });
    arrow(g, 536, 1050, 88, 0, C.yellow, 12);
  },
  reachChild(g, lt, d, t) {
    base(g);
    heading(g, 'ONE CHILD AT A TIME', '21 / 30');
    circle(g, 721, 813, 302, C.yellowPale);
    K.man(g, 284, 964, .48, { shirt:C.organ, mouth:'smile', arm:'up' });
    K.man(g, 760, 979, .43, { child:true, mouth:'o', eyes:'wide' });
    // The vial is at the worker's raised hand, not floating ahead of the action.
    K.vial(g, 425, 748, .35, { labelText:'OPV', tilt:-.17 });
    const p=eo(seg(lt,.34,1.37));
    K.drop(g, lerp(470,756,p), lerp(812,854,p), 24 - p*10, C.organ);
    if (lt>1.05) burst(g, 770, 852, 133, C.yellow, 8, 1);
    label(g, 'NO CHILD LEFT OUT', 542, 449, { bg:C.ink, fg:C.paper, size:28 });
  },
  oneCase(g, lt, d, t) {
    dark(g);
    heading(g, 'THE FIRST SIGNAL', '22 / 30', true);
    for (let i=3; i>=0; i--) circle(g, 505, 808, 104+i*89+Math.sin(t*2)*4, null, i%2?C.red:'#5D3038', 15);
    circle(g, 505, 808, 61, C.red);
    K.warning(g, 814, 997, .59);
    label(g, 'ONE DETECTION', 523, 437, { bg:C.red, fg:C.paper, size:30 });
    text(g, '01', 507, 808, 57, C.paper);
  },
  surveillance(g, lt, d, t) {
    base(g);
    heading(g, 'FIND IT FAST', '23 / 30');
    circle(g, 523, 828, 337, C.paper, C.ink, 10);
    for (let i=1; i<4; i++) circle(g, 523, 828, i*78, null, C.stone, 7);
    const a = -Math.PI/2 + lt * 2.4;
    path(g, [[523,828],[523+Math.cos(a)*310,828+Math.sin(a)*310],[523+Math.cos(a-.4)*310,828+Math.sin(a-.4)*310]], C.yellowPale);
    line(g, 523, 828, 523+Math.cos(a)*314, 828+Math.sin(a)*314, C.yellow, 12);
    circle(g, 631, 694, 22, C.red);
    circle(g, 399, 923, 14, C.organ);
    circle(g, 758, 930, 14, C.organ);
    label(g, 'REAL-TIME ALERTS', 542, 425, { bg:C.ink, fg:C.paper, size:28 });
    rr(g, 736, 1107, 135, 94, 18, C.ink);
    circle(g, 760, 1130, 9, C.yellow); circle(g, 803, 1130, 9, C.red);
    line(g, 757, 1172, 851, 1172, C.yellow, 8);
  },
  twentyMillion(g, lt, d, t) {
    base(g);
    heading(g, 'A GENERATION PROTECTED', '24 / 30');
    circle(g, 534, 785, 412, C.yellowPale);
    text(g, '20', 539, 593, 240, C.ink);
    text(g, 'MILLION', 540, 775, 112, C.ink);
    for (let i=0; i<5; i++) K.smallPerson(g, 182+i*178, 1050, .50, { color:i%2?C.organ:C.yellow, shielded:i===4 });
    label(g, 'CHILDREN PROTECTED', 534, 430, { bg:C.ink, fg:C.paper, size:27 });
  },
  paralysis(g, lt, d, t) {
    xray(g,t);
    heading(g, 'PARALYSIS PREVENTED', '25 / 30');
    K.man(g, 475, 903, .65, { xray:true, child:true, eyes:'normal', mouth:'smile' });
    K.shield(g, 768, 910, .68, { fill:C.yellow });
    K.star(g, 735, 531, 39); K.star(g, 885, 713, 25);
    label(g, 'A CHANCE TO GROW', 539, 429, { bg:C.ink, fg:C.paper, size:26 });
  },
  livesSaved(g, lt, d, t) {
    base(g);
    heading(g, 'LIVES SAVED', '26 / 30');
    circle(g, 538, 807, 360, C.redPale);
    K.tinyHeart(g, 540, 816, 2.7, C.organ);
    text(g, '1.6', 540, 763, 179, C.paper);
    text(g, 'MILLION', 540, 884, 74, C.paper);
    K.smallPerson(g, 215, 1035, .44, { color:C.yellow });
    K.smallPerson(g, 867, 1035, .44, { color:C.yellow });
    K.star(g, 387, 533, 32); K.star(g, 718, 519, 37);
    label(g, 'EVERY LIFE COUNTS', 539, 427, { bg:C.ink, fg:C.paper, size:28 });
  },
  momentum(g, lt, d, t) {
    dark(g);
    heading(g, 'WHAT IF WE STOP?', '27 / 30', true);
    arc(g, 540, 927, 283, Math.PI, 2*Math.PI, '#5A4F48', 48);
    arc(g, 540, 927, 283, Math.PI, Math.PI*1.62, C.yellow, 48);
    const a = lerp(Math.PI*1.72, Math.PI*1.05, eo(seg(lt,.3,1.62)));
    line(g, 540, 927, 540+Math.cos(a)*236, 927+Math.sin(a)*236, C.red, 19);
    circle(g, 540, 927, 30, C.paper);
    text(g, 'MOMENTUM', 540, 476, 70, C.paper);
    label(g, 'DON’T LET UP', 540, 1116, { bg:C.red, fg:C.paper, size:30 });
  },
  risk(g, lt, d, t) {
    dark(g);
    heading(g, 'THE RISK OF REVERSAL', '28 / 30', true);
    circle(g, 535, 814, 346, C.paper, C.ink, 11);
    g.save(); g.beginPath(); g.arc(535,814,340,0,Math.PI*2); g.clip();
    path(g, [[286,683],[385,576],[488,681],[422,760],[444,946],[353,1035],[267,877]], C.stone);
    path(g, [[555,548],[712,607],[794,723],[750,884],[822,967],[658,1021],[585,901],[539,799]], C.stone);
    g.restore();
    for (let i=0;i<17;i++) {
      const a=i*2.4, r=50 + (i%5)*49, appear=seg(lt,.15+(i%8)*.16,.4+(i%8)*.16);
      if (appear>0) circle(g, 535+Math.cos(a)*r, 815+Math.sin(a)*r*.9, (9+i%3*5)*eo(appear), C.red);
    }
    label(g, 'CASES COULD RETURN', 539, 420, { bg:C.red, fg:C.paper, size:29 });
  },
  protect(g, lt, d, t) {
    base(g);
    heading(g, 'THE WAY FORWARD', '29 / 30');
    circle(g, 529, 840, 367, C.yellowPale);
    K.shield(g, 540, 803, 1.71, { fill:C.yellowPale, check:false });
    K.man(g, 380, 916, .54, { mouth:'flat', arm:'protect', look:1 });
    K.man(g, 697, 996, .38, { child:true, mouth:'smile' });
    K.virus(g, 940, 645, 60, { danger:true, rot:t*.3 });
    cross(g, 911, 764, 28, C.red, 11);
    label(g, 'REACH EVERY CHILD', 540, 402, { bg:C.ink, fg:C.paper, size:30 });
  },
  end(g, lt, d, t) {
    base(g, C.paper);
    heading(g, 'THE END IS WITHIN REACH', '30 / 30');
    circle(g, 540, 762, 356, C.yellow);
    K.shield(g, 540, 751, 1.04, { fill:C.paper, check:false });
    K.smallPerson(g, 540, 849, .64, { color:C.organ, shielded:true });
    text(g, 'EVERY CHILD.', 540, 1148, 100, C.ink);
    text(g, 'EVERYWHERE.', 540, 1270, 100, C.ink);
    rr(g, 244, 1340, 593, 13, 7, C.yellow);
  },
};

export function drawScene(g, scene, localTime, duration, time) {
  const fn = scenes[scene];
  if (!fn) throw new Error(`Unknown shot scene: ${scene}`);
  fn(g, Math.max(0,localTime), duration, time);
}
export const sceneNames = Object.keys(scenes);
